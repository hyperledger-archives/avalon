package com.iexec.worker.dataset;

import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.sms.SmsService;
import com.iexec.worker.utils.FileHelper;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.file.Paths;


@Slf4j
@Service
public class DatasetService {

    @Value("${decryptFilePath}")
    private String scriptFilePath;

    private final WorkerConfigurationService workerConfigurationService;
    private final SmsService smsService;

    public DatasetService(WorkerConfigurationService workerConfigurationService,
                          SmsService smsService) {
        this.workerConfigurationService = workerConfigurationService;
        this.smsService = smsService;
    }

    /*
     * In order to keep a linear replicate workflow, we'll always have the steps:
     * APP_DOWNLOADING, ..., DATA_DOWNLOADING, ..., COMPUTING (even when the dataset requested is 0x0).
     * In the 0x0 dataset case, we'll have an empty datasetUri, and we'll consider the dataset as downloaded
     */
    public boolean downloadDataset(String chainTaskId, String datasetUri) {
        if (chainTaskId.isEmpty()) {
            log.error("Failed to downloadDataset, chainTaskId shouldn't be empty [chainTaskId:{}, datasetUri:{}]",
                    chainTaskId, datasetUri);
            return false;
        }
        if (datasetUri.isEmpty()) {
            log.info("There's nothing to download for this task [chainTaskId:{}, datasetUri:{}]",
                    chainTaskId, datasetUri);
            return true;
        }
        return FileHelper.downloadFileInDirectory(datasetUri, workerConfigurationService.getTaskInputDir(chainTaskId));
    }

    public boolean isDatasetDecryptionNeeded(String chainTaskId) {
        String datasetSecretFilePath = smsService.getDatasetSecretFilePath(chainTaskId);

        if (!new File(datasetSecretFilePath).exists()) {
            log.info("No dataset secret file found, will continue without decrypting dataset [chainTaskId:{}]", chainTaskId);
            return false;
        }

        return true;
    }

    public boolean decryptDataset(String chainTaskId, String datasetUri) {
        String datasetFileName = Paths.get(datasetUri).getFileName().toString();
        String datasetFilePath = workerConfigurationService.getTaskInputDir(chainTaskId) + File.separator + datasetFileName;
        String datasetSecretFilePath = smsService.getDatasetSecretFilePath(chainTaskId);

        log.info("Decrypting dataset file [datasetFile:{}, secretFile:{}]", datasetFilePath, datasetSecretFilePath);

        decryptFile(datasetFilePath, datasetSecretFilePath);

        String decryptedDatasetFilePath = datasetFilePath + ".recovered";

        if (!new File(decryptedDatasetFilePath).exists()) {
            log.error("Decrypted dataset file not found [chainTaskId:{}, decryptedDatasetFilePath:{}]",
                    chainTaskId, decryptedDatasetFilePath);
            return false;
        }

        // replace original dataset file with decrypted one
        return FileHelper.replaceFile(datasetFilePath, decryptedDatasetFilePath);
    }

    private void decryptFile(String dataFilePath, String secretFilePath) {
        ProcessBuilder pb = new ProcessBuilder(this.scriptFilePath, dataFilePath, secretFilePath);

        try {
            Process pr = pb.start();

            BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream()));
            String line;

            while ((line = in.readLine()) != null) { log.info(line); }

            pr.waitFor();
            in.close();
        } catch (Exception e) {
            log.error("Error while trying to decrypt data [datasetFile{}, secretFile:{}]",
                    dataFilePath, secretFilePath);
            e.printStackTrace();
        }
    }
}