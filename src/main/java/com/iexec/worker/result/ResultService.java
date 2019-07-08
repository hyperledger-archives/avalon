package com.iexec.worker.result;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iexec.common.result.ResultModel;
import com.iexec.common.result.eip712.Eip712Challenge;
import com.iexec.common.result.eip712.Eip712ChallengeUtils;
import com.iexec.common.task.TaskDescription;
import com.iexec.common.utils.BytesUtils;
import com.iexec.worker.chain.CredentialsService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.sms.SmsService;
import com.iexec.worker.tee.scone.SconeEnclaveSignatureFile;
import com.iexec.worker.utils.FileHelper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.web3j.crypto.ECKeyPair;
import org.web3j.crypto.Hash;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

import static com.iexec.common.utils.BytesUtils.bytesToString;
import static com.iexec.worker.utils.FileHelper.createFileWithContent;

@Slf4j
@Service
public class ResultService {

    @Value("${encryptFilePath}")
    private String scriptFilePath;

    private static final String DETERMINIST_FILE_NAME = "determinism.iexec";
    private static final String TEE_ENCLAVE_SIGNATURE_FILE_NAME = "enclaveSig.iexec";
    private static final String CALLBACK_FILE_NAME = "callback.iexec";
    private static final String STDOUT_FILENAME = "stdout.txt";

    private WorkerConfigurationService workerConfigurationService;
    private ResultRepoService resultRepoService;
    private CredentialsService credentialsService;
    private IexecHubService iexecHubService;
    private SmsService smsService;

    private Map<String, ResultInfo> resultInfoMap;

    public ResultService(WorkerConfigurationService configurationService,
                         ResultRepoService resultRepoService,
                         CredentialsService credentialsService,
                         IexecHubService iexecHubService,
                         SmsService smsService) {
        this.workerConfigurationService = configurationService;
        this.resultRepoService = resultRepoService;
        this.credentialsService = credentialsService;
        this.iexecHubService = iexecHubService;
        this.smsService = smsService;
        this.resultInfoMap = new ConcurrentHashMap<>();
    }

    public boolean saveResult(String chainTaskId, TaskDescription taskDescription, String stdout) {
        try {
            saveStdoutFileInResultFolder(chainTaskId, stdout);
            zipResultFolder(chainTaskId);
            saveResultInfo(chainTaskId, taskDescription);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private File saveStdoutFileInResultFolder(String chainTaskId, String stdoutContent) {
        log.info("Stdout file added to result folder [chainTaskId:{}]", chainTaskId);
        String filePath = getResultFolderPath(chainTaskId) + File.separator + STDOUT_FILENAME;
        return createFileWithContent(filePath, stdoutContent);
    }

    public void zipResultFolder(String chainTaskId) {
        File zipFile = FileHelper.zipFolder(getResultFolderPath(chainTaskId));
        log.info("Zip file has been created [chainTaskId:{}, zipFile:{}]", chainTaskId, zipFile.getAbsolutePath());
    }

    public void saveResultInfo(String chainTaskId, TaskDescription taskDescription) {
        ResultInfo resultInfo = ResultInfo.builder()
                .image(taskDescription.getAppUri())
                .cmd(taskDescription.getCmd())
                .deterministHash(getTaskDeterminismHash(chainTaskId))
                .datasetUri(taskDescription.getDatasetUri())
                .build();

        resultInfoMap.put(chainTaskId, resultInfo);
    }

    public ResultModel getResultModelWithZip(String chainTaskId) {
        ResultInfo resultInfo = getResultInfos(chainTaskId);
        byte[] zipResultAsBytes = new byte[0];
        String zipLocation = getResultZipFilePath(chainTaskId);
        try {
            zipResultAsBytes = Files.readAllBytes(Paths.get(zipLocation));
        } catch (IOException e) {
            log.error("Failed to get zip result [chainTaskId:{}, zipLocation:{}]", chainTaskId, zipLocation);
        }

        return ResultModel.builder()
                .chainTaskId(chainTaskId)
                .image(resultInfo.getImage())
                .cmd(resultInfo.getCmd())
                .zip(zipResultAsBytes)
                .deterministHash(resultInfo.getDeterministHash())
                .build();
    }

    public ResultInfo getResultInfos(String chainTaskId) {
        return resultInfoMap.get(chainTaskId);
    }

    public String getResultZipFilePath(String chainTaskId) {
        return getResultFolderPath(chainTaskId) + ".zip";
    }

    public String getResultFolderPath(String chainTaskId) {
        return workerConfigurationService.getTaskOutputDir(chainTaskId);
    }

    public String getEncryptedResultFilePath(String chainTaskId) {
        return workerConfigurationService.getTaskOutputDir(chainTaskId) + FileHelper.SLASH_IEXEC_OUT + ".zip";
    }

    public boolean isResultZipFound(String chainTaskId) {
        return new File(getResultZipFilePath(chainTaskId)).exists();
    }

    public boolean isResultFolderFound(String chainTaskId) {
        return new File(getResultFolderPath(chainTaskId)).exists();
    }

    public boolean isEncryptedResultZipFound(String chainTaskId) {
        return new File(getEncryptedResultFilePath(chainTaskId)).exists();
    }

    public boolean removeResult(String chainTaskId) {
        boolean deletedInMap = resultInfoMap.remove(chainTaskId) != null;
        boolean deletedTaskFolder = FileHelper.deleteFolder(new File(getResultFolderPath(chainTaskId)).getParent());

        boolean deleted = deletedInMap && deletedTaskFolder;
        if (deletedTaskFolder) {
            log.info("The result of the chainTaskId has been deleted [chainTaskId:{}]", chainTaskId);
        } else {
            log.warn("The result of the chainTaskId couldn't be deleted [chainTaskId:{}, deletedInMap:{}, " +
                            "deletedTaskFolder:{}]",
                    chainTaskId, deletedInMap, deletedTaskFolder);
        }

        return deleted;
    }

    public void cleanUnusedResultFolders(List<String> recoveredTasks) {
        for (String chainTaskId : getAllChainTaskIdsInResultFolder()) {
            if (!recoveredTasks.contains(chainTaskId)) {
                removeResult(chainTaskId);
            }
        }
    }

    public List<String> getAllChainTaskIdsInResultFolder() {
        File resultsFolder = new File(workerConfigurationService.getWorkerBaseDir());
        String[] chainTaskIdFolders = resultsFolder.list((current, name) -> new File(current, name).isDirectory());

        if (chainTaskIdFolders == null || chainTaskIdFolders.length == 0) {
            return Collections.emptyList();
        }
        return Arrays.asList(chainTaskIdFolders);
    }

    public String getTaskDeterminismHash(String chainTaskId) {
        boolean isTeeTask = iexecHubService.isTeeTask(chainTaskId);

        if (!isTeeTask) return getNonTeeDeterminismHash(chainTaskId);

        log.info("This is a TEE task, getting determinism hash from enclave output");
        return getTeeDeterminismHash(chainTaskId);
    }

    private String getNonTeeDeterminismHash(String chainTaskId) {
        String hash = "";
        String filePath = workerConfigurationService.getTaskIexecOutDir(chainTaskId)
                + File.separator + DETERMINIST_FILE_NAME;

        Path determinismFilePath = Paths.get(filePath);

        try {
            if (determinismFilePath.toFile().exists()) {
                hash = getHashFromDeterminismIexecFile(determinismFilePath);
                log.info("Determinism file found and its hash has been computed "
                        + "[chainTaskId:{}, hash:{}]", chainTaskId, hash);
                return hash;
            }

            log.info("Determinism file not found, the hash of the result file will be used instead "
                    + "[chainTaskId:{}]", chainTaskId);
            String resultFilePathName = getResultZipFilePath(chainTaskId);
            byte[] content = Files.readAllBytes(Paths.get(resultFilePathName));
            hash = bytesToString(Hash.sha256(content));
        } catch (IOException e) {
            log.error("Failed to compute determinism hash [chainTaskId:{}]", chainTaskId);
            e.printStackTrace();
            return "";
        }

        log.info("Computed hash of the result file [chainTaskId:{}, hash:{}]", chainTaskId, hash);
        return hash;
    }

    /** This method is to compute the hash of the determinist.iexec file
     * if the file is a text and if it is a byte32, no need to hash it
     * if the file is a text and if it is NOT a byte32, it is hashed using sha256
     * if the file is NOT a text, it is hashed using sha256
     */
    private String getHashFromDeterminismIexecFile(Path deterministFilePath) throws IOException {
        try (Scanner scanner = new Scanner(deterministFilePath.toFile())) {
            // command to put the content of the whole file into string (\Z is the end of the string anchor)
            // This ultimately makes the input have one actual token, which is the entire file
            String contentFile = scanner.useDelimiter("\\Z").next();
            byte[] content = BytesUtils.stringToBytes(contentFile);

            // if determinism.iexec file is already a byte32, no need to hash it again
            return bytesToString(BytesUtils.isBytes32(content) ? content : Hash.sha256(content));

        } catch (Exception e) {
            return bytesToString(Hash.sha256(Files.readAllBytes(deterministFilePath)));
        }
    }

    private String getTeeDeterminismHash(String chainTaskId) {
        Optional<SconeEnclaveSignatureFile> oSconeEnclaveSignatureFile =
                readSconeEnclaveSignatureFile(chainTaskId);

        if (!oSconeEnclaveSignatureFile.isPresent()) {
            log.error("Could not get TEE determinism hash [chainTaskId:{}]", chainTaskId);
            return "";
        }

        String hash = oSconeEnclaveSignatureFile.get().getResult();
        log.info("Enclave signature file found, result hash retrieved successfully "
                + "[chainTaskId:{}, hash:{}]", chainTaskId, hash);
        return hash;
    }

    public Optional<SconeEnclaveSignatureFile> readSconeEnclaveSignatureFile(String chainTaskId) {
        String enclaveSignatureFilePath = workerConfigurationService.getTaskIexecOutDir(chainTaskId)
                + File.separator + TEE_ENCLAVE_SIGNATURE_FILE_NAME;

        File enclaveSignatureFile = new File(enclaveSignatureFilePath);

        if (!enclaveSignatureFile.exists()) {
            log.error("File enclaveSig.iexec not found [chainTaskId:{}, enclaveSignatureFilePath:{}]",
                    chainTaskId, enclaveSignatureFilePath);
            return Optional.empty();
        }

        ObjectMapper mapper = new ObjectMapper();
        SconeEnclaveSignatureFile sconeEnclaveSignatureFile = null;
        try {
            sconeEnclaveSignatureFile = mapper.readValue(enclaveSignatureFile, SconeEnclaveSignatureFile.class);
        } catch (IOException e) {
            log.error("File enclaveSig.iexec found but failed to parse it [chainTaskId:{}]", chainTaskId);
            e.printStackTrace();
            return Optional.empty();
        }

        if (sconeEnclaveSignatureFile == null) {
            log.error("File enclaveSig.iexec found but was parsed to null [chainTaskId:{}]", chainTaskId);
            return Optional.empty();
        }

        log.debug("Content of enclaveSig.iexec file [chainTaskId:{}, sconeEnclaveSignatureFile:{}]",
                chainTaskId, sconeEnclaveSignatureFile);

        return Optional.of(sconeEnclaveSignatureFile);
    }

    public String getCallbackDataFromFile(String chainTaskId) {
        String hexaString = "";
        try {
            String callbackFilePathName = workerConfigurationService.getTaskIexecOutDir(chainTaskId)
                    + File.separator + CALLBACK_FILE_NAME;

            Path callbackFilePath = Paths.get(callbackFilePathName);

            if (callbackFilePath.toFile().exists()) {
                byte[] callbackFileBytes = Files.readAllBytes(callbackFilePath);
                hexaString = new String(callbackFileBytes);
                boolean isHexaString = BytesUtils.isHexaString(hexaString);
                log.info("Callback file exists [chainTaskId:{}, hexaString:{}, isHexaString:{}]", chainTaskId, hexaString, isHexaString);
                return isHexaString ? hexaString : "";
            } else {
                log.info("No callback file [chainTaskId:{}]", chainTaskId);
            }
        } catch (IOException e) {
            e.printStackTrace();
            log.error("Failed to getCallbackDataFromFile [chainTaskId:{}]", chainTaskId);
        }

        return hexaString;
    }

    public boolean isResultEncryptionNeeded(String chainTaskId) {
        String beneficiarySecretFilePath = smsService.getBeneficiarySecretFilePath(chainTaskId);

        if (!new File(beneficiarySecretFilePath).exists()) {
            log.info("No beneficiary secret file found, will continue without encrypting result [chainTaskId:{}]", chainTaskId);
            return false;
        }

        return true;
    }

    public boolean encryptResult(String chainTaskId) {
        String beneficiarySecretFilePath = smsService.getBeneficiarySecretFilePath(chainTaskId);
        String resultZipFilePath = getResultZipFilePath(chainTaskId);
        String taskOutputDir = workerConfigurationService.getTaskOutputDir(chainTaskId);

        log.info("Encrypting result zip [resultZipFilePath:{}, beneficiarySecretFilePath:{}]",
                resultZipFilePath, beneficiarySecretFilePath);

        encryptFile(taskOutputDir, resultZipFilePath, beneficiarySecretFilePath);

        String encryptedResultFilePath = getEncryptedResultFilePath(chainTaskId);

        if (!new File(encryptedResultFilePath).exists()) {
            log.error("Encrypted result file not found [chainTaskId:{}, encryptedResultFilePath:{}]",
                    chainTaskId, encryptedResultFilePath);
            return false;
        }

        // replace result file with the encypted one
        return FileHelper.replaceFile(resultZipFilePath, encryptedResultFilePath);
    }

    private void encryptFile(String taskOutputDir, String resultZipFilePath, String publicKeyFilePath) {
        String options = String.format("--root-dir=%s --result-file=%s --key-file=%s",
                taskOutputDir, resultZipFilePath, publicKeyFilePath);

        String cmd = this.scriptFilePath + " " + options;

        ProcessBuilder pb = new ProcessBuilder(cmd.split(" "));

        try {
            Process pr = pb.start();

            BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream()));
            String line;
    
            while ((line = in.readLine()) != null) { log.info(line); }
    
            pr.waitFor();
            in.close();
        } catch (Exception e) {
            log.error("Error while trying to encrypt result [resultZipFilePath{}, publicKeyFilePath:{}]",
                    resultZipFilePath, publicKeyFilePath);
            e.printStackTrace();
        }
    }

    public String uploadResult(String chainTaskId) {
        Optional<Eip712Challenge> oEip712Challenge = resultRepoService.getChallenge();

        if (!oEip712Challenge.isPresent()) {
            return "";
        }

        Eip712Challenge eip712Challenge = oEip712Challenge.get();

        ECKeyPair ecKeyPair = credentialsService.getCredentials().getEcKeyPair();
        String authorizationToken = Eip712ChallengeUtils.buildAuthorizationToken(eip712Challenge,
                workerConfigurationService.getWorkerWalletAddress(), ecKeyPair);

        if (authorizationToken.isEmpty()) {
            return "";
        }

        return resultRepoService.uploadResult(authorizationToken, getResultModelWithZip(chainTaskId));
    }


    public boolean isResultAvailable(String chainTaskId) {
        boolean isResultZipFound = isResultZipFound(chainTaskId);
        boolean isResultFolderFound = isResultFolderFound(chainTaskId);

        if (!isResultZipFound && !isResultFolderFound) return false;

        if (!isResultZipFound) zipResultFolder(chainTaskId);

        return true;
    }
}
