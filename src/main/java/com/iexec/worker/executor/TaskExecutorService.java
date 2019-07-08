package com.iexec.worker.executor;

import com.iexec.common.chain.ChainReceipt;
import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.replicate.ReplicateDetails;
import com.iexec.common.replicate.ReplicateStatus;
import com.iexec.common.security.Signature;
import com.iexec.common.task.TaskDescription;
import com.iexec.worker.chain.ContributionService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.chain.RevealService;
import com.iexec.worker.config.PublicConfigurationService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.docker.ComputationService;
import com.iexec.worker.feign.CustomFeignClient;
import com.iexec.worker.result.ResultService;
import org.apache.commons.lang3.tuple.Pair;

import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

import static com.iexec.common.replicate.ReplicateStatus.*;


/*
 * this service is only caller by ReplicateDemandService when getting new replicate
 * or by AmnesiaRecoveryService when recovering an interrupted task
 */
@Slf4j
@Service
public class TaskExecutorService {

    // external services
    private TaskExecutorHelperService taskExecutorHelperService;
    private ResultService resultService;
    private ContributionService contributionService;
    private CustomFeignClient customFeignClient;
    private RevealService revealService;
    private WorkerConfigurationService workerConfigurationService;
    private IexecHubService iexecHubService;
    private PublicConfigurationService publicConfigurationService;
    private ComputationService computationService;

    // internal variables
    private int maxNbExecutions;
    private ThreadPoolExecutor executor;
    private String corePublicAddress;

    //TODO make this fat constructor lose weight
    public TaskExecutorService(TaskExecutorHelperService taskExecutorHelperService,
                               ResultService resultService,
                               ContributionService contributionService,
                               CustomFeignClient customFeignClient,
                               RevealService revealService,
                               WorkerConfigurationService workerConfigurationService,
                               IexecHubService iexecHubService,
                               ComputationService computationService,
                               PublicConfigurationService publicConfigurationService) {
        this.taskExecutorHelperService = taskExecutorHelperService;
        this.resultService = resultService;
        this.contributionService = contributionService;
        this.customFeignClient = customFeignClient;
        this.revealService = revealService;
        this.workerConfigurationService = workerConfigurationService;
        this.iexecHubService = iexecHubService;
        this.computationService = computationService;
        this.publicConfigurationService = publicConfigurationService;

        maxNbExecutions = Runtime.getRuntime().availableProcessors() - 1;
        executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(maxNbExecutions);
    }

    @PostConstruct
    public void initIt() {
        corePublicAddress = publicConfigurationService.getSchedulerPublicAddress();
    }

    public boolean canAcceptMoreReplicates() {
        return executor.getActiveCount() < maxNbExecutions;
    }

    public void computeOrContribute(ContributionAuthorization contributionAuth) {

        String chainTaskId = contributionAuth.getChainTaskId();

        if (!contributionService.isContributionAuthorizationValid(contributionAuth, corePublicAddress)) {
            log.error("The contribution contribAuth is NOT valid, the task will not be performed"
                    + " [chainTaskId:{}, contribAuth:{}]", chainTaskId, contributionAuth);
            return;
        }

        boolean isResultAvailable = resultService.isResultAvailable(chainTaskId);

        if (isResultAvailable) {
            log.info("Result found, will restart task from CONTRIBUTING [chainTaskId:{}]", chainTaskId);
            contribute(contributionAuth);    
            return;
        }

        addReplicate(contributionAuth);
    }

    public CompletableFuture<Boolean> addReplicate(ContributionAuthorization contributionAuth) {
        String chainTaskId = contributionAuth.getChainTaskId();

        // don't compute if task is not initialized onChain
        if (!contributionService.isChainTaskInitialized(chainTaskId)) {
            log.error("Task not initialized onChain [chainTaskId:{}]", chainTaskId);
            return CompletableFuture.completedFuture(false);
        }        

        Optional<TaskDescription> taskDescriptionFromChain =
                iexecHubService.getTaskDescriptionFromChain(chainTaskId);

        if (!taskDescriptionFromChain.isPresent()) {
            log.error("Cannot compute, task description not found onChain [chainTaskId:{}]",
                    chainTaskId);
            return CompletableFuture.completedFuture(false);
        }

        TaskDescription taskDescription = taskDescriptionFromChain.get();
        boolean isTeeTask = taskDescription.isTeeTask();

        // don't compute if task needs TEE && TEE not supported;
        if (isTeeTask && !workerConfigurationService.isTeeEnabled()) {
            log.error("Task needs TEE, I don't support it [chainTaskId:{}]", chainTaskId);
            return CompletableFuture.completedFuture(false);
        }        

        return CompletableFuture.supplyAsync(() -> compute(contributionAuth, taskDescription), executor)
                .thenApply(stdout -> resultService.saveResult(chainTaskId, taskDescription, stdout))
                .thenAccept(isSaved -> { if (isSaved) contribute(contributionAuth); })
                .handle((res, err) -> {
                    if (err != null) err.printStackTrace();
                    return err == null;
                });
    }

    // TODO: keep just one onf the the two args - probably taskDescription
    @Async
    private String compute(ContributionAuthorization contributionAuth, TaskDescription taskDescription) {
        String chainTaskId = contributionAuth.getChainTaskId();
        boolean isTeeTask = taskDescription.isTeeTask();

        customFeignClient.updateReplicateStatus(chainTaskId, RUNNING);

        // check app type
        String appTypeError = taskExecutorHelperService.checkAppType(chainTaskId, taskDescription.getAppType());
        if (!appTypeError.isEmpty()) return appTypeError;

        // try to download app
        String appDownloadError = taskExecutorHelperService.tryToDownloadApp(taskDescription);
        if (!appDownloadError.isEmpty()) return appDownloadError;

        customFeignClient.updateReplicateStatus(chainTaskId, APP_DOWNLOADED);
 
        // try to download data
        String dataDownloadError = taskExecutorHelperService.tryToDownloadData(chainTaskId,
                taskDescription.getDatasetUri());
        if (!dataDownloadError.isEmpty()) return dataDownloadError;

        customFeignClient.updateReplicateStatus(chainTaskId, DATA_DOWNLOADED);
        customFeignClient.updateReplicateStatus(chainTaskId, COMPUTING);

        String contributionAbilityError = taskExecutorHelperService.checkContributionAbility(chainTaskId);
        if (!contributionAbilityError.isEmpty()) return contributionAbilityError;

        String imageExistenceError = taskExecutorHelperService.checkIfAppImageExists(chainTaskId,
                taskDescription.getAppUri());
        if (!imageExistenceError.isEmpty()) return imageExistenceError;

        Pair<ReplicateStatus, String> pair = null;
        if (isTeeTask) {
            pair = computationService.runTeeComputation(taskDescription, contributionAuth);
        } else {
            pair = computationService.runNonTeeComputation(taskDescription, contributionAuth);
        }

        customFeignClient.updateReplicateStatus(chainTaskId, pair.getLeft());
        return pair.getRight();
    }

    @Async
    public void contribute(ContributionAuthorization contributionAuth) {
        String chainTaskId = contributionAuth.getChainTaskId();

        String enclaveChallenge = contributionAuth.getEnclaveChallenge();
        log.info("Trying to contribute [chainTaskId:{}]", chainTaskId);

        String determinismHash = taskExecutorHelperService.getTaskDeterminismHash(chainTaskId);
        if (determinismHash.isEmpty()) return;

        Optional<Signature> oEnclaveSignature = taskExecutorHelperService.getVerifiedEnclaveSignature(chainTaskId, enclaveChallenge);
        if (!oEnclaveSignature.isPresent()) return;

        Signature enclaveSignature = oEnclaveSignature.get();

        String contributionAbilityError = taskExecutorHelperService.checkContributionAbility(chainTaskId);
        if (!contributionAbilityError.isEmpty()) return;

        customFeignClient.updateReplicateStatus(chainTaskId, ReplicateStatus.CAN_CONTRIBUTE);

        boolean hasEnoughGas = taskExecutorHelperService.checkGasBalance(chainTaskId);
        if (!hasEnoughGas) System.exit(0);

        customFeignClient.updateReplicateStatus(chainTaskId, CONTRIBUTING);

        Optional<ChainReceipt> oChainReceipt =
                contributionService.contribute(contributionAuth, determinismHash, enclaveSignature);

        boolean isValidChainReceipt = taskExecutorHelperService.isValidChainReceipt(chainTaskId, oChainReceipt);
        if (!isValidChainReceipt) return;

        customFeignClient.updateReplicateStatus(chainTaskId, CONTRIBUTED,
                ReplicateDetails.builder().chainReceipt(oChainReceipt.get()).build());
    }

    @Async
    public void reveal(String chainTaskId, long consensusBlock) {
        log.info("Trying to reveal [chainTaskId:{}]", chainTaskId);
        String determinismHash = taskExecutorHelperService.getTaskDeterminismHash(chainTaskId);
        if (determinismHash.isEmpty()) return;

        boolean isBlockReached = revealService.isConsensusBlockReached(chainTaskId, consensusBlock);
        boolean canReveal = revealService.canReveal(chainTaskId, determinismHash);

        if (!isBlockReached || !canReveal) {
            log.error("The worker will not be able to reveal [chainTaskId:{}]", chainTaskId);
            customFeignClient.updateReplicateStatus(chainTaskId, CANT_REVEAL);
            return;
        }

        boolean hasEnoughGas = taskExecutorHelperService.checkGasBalance(chainTaskId);
        if (!hasEnoughGas) System.exit(0);

        customFeignClient.updateReplicateStatus(chainTaskId, REVEALING);

        Optional<ChainReceipt> oChainReceipt = revealService.reveal(chainTaskId, determinismHash);

        boolean isValidChainReceipt = taskExecutorHelperService.isValidChainReceipt(chainTaskId, oChainReceipt);
        if (!isValidChainReceipt) return;

        customFeignClient.updateReplicateStatus(chainTaskId, REVEALED,
                ReplicateDetails.builder().chainReceipt(oChainReceipt.get()).build());
    }

    @Async
    public void abortConsensusReached(String chainTaskId) {
        resultService.removeResult(chainTaskId);
        customFeignClient.updateReplicateStatus(chainTaskId, ABORTED_ON_CONSENSUS_REACHED);
    }

    @Async
    public void abortContributionTimeout(String chainTaskId) {
        resultService.removeResult(chainTaskId);
        customFeignClient.updateReplicateStatus(chainTaskId, ABORTED_ON_CONTRIBUTION_TIMEOUT);
    }

    @Async
    public void uploadResult(String chainTaskId) {
        customFeignClient.updateReplicateStatus(chainTaskId, RESULT_UPLOADING);

        boolean isResultEncryptionNeeded = resultService.isResultEncryptionNeeded(chainTaskId);
        boolean isResultEncrypted = false;

        if (isResultEncryptionNeeded) {
            isResultEncrypted = resultService.encryptResult(chainTaskId);
        }

        if (isResultEncryptionNeeded && !isResultEncrypted) {
            customFeignClient.updateReplicateStatus(chainTaskId, RESULT_UPLOAD_FAILED);
            log.error("Failed to encrypt result [chainTaskId:{}]", chainTaskId);
            return;
        }

        String resultLink = resultService.uploadResult(chainTaskId);

        if (resultLink.isEmpty()) {
            log.error("ResultLink missing (aborting) [chainTaskId:{}]", chainTaskId);
            customFeignClient.updateReplicateStatus(chainTaskId, RESULT_UPLOAD_FAILED);
            return;
        }

        String callbackData = resultService.getCallbackDataFromFile(chainTaskId);

        log.info("Uploaded result with details [chainTaskId:{}, resultLink:{}, callbackData:{}]",
                chainTaskId, resultLink, callbackData);

        ReplicateDetails details = ReplicateDetails.builder()
                .resultLink(resultLink)
                .chainCallbackData(callbackData)
                .build();

        customFeignClient.updateReplicateStatus(chainTaskId, RESULT_UPLOADED, details);
    }

    @Async
    public void completeTask(String chainTaskId) {
        resultService.removeResult(chainTaskId);
        customFeignClient.updateReplicateStatus(chainTaskId, COMPLETED);
    }
}