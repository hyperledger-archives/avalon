package com.iexec.worker.executor;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.dapp.DappType;
import com.iexec.common.replicate.ReplicateDetails;
import com.iexec.common.replicate.ReplicateStatus;
import com.iexec.common.security.Signature;
import com.iexec.common.task.TaskDescription;
import com.iexec.common.utils.BytesUtils;
import com.iexec.worker.chain.ContributionService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.chain.RevealService;
import com.iexec.worker.config.PublicConfigurationService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.docker.ComputationService;
import com.iexec.worker.feign.CustomFeignClient;
import com.iexec.worker.result.ResultService;
import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import static com.iexec.common.replicate.ReplicateStatus.RESULT_UPLOADED;
import static com.iexec.common.replicate.ReplicateStatus.RESULT_UPLOAD_FAILED;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class TaskExecutorServiceTests {

    @Mock private TaskExecutorHelperService taskExecutorHelperService;
    @Mock private ResultService resultService;
    @Mock private ContributionService contributionService;
    @Mock private CustomFeignClient customFeignClient;
    @Mock private RevealService revealService;
    @Mock private WorkerConfigurationService workerConfigurationService;
    @Mock private IexecHubService iexecHubService;
    @Mock private PublicConfigurationService publicConfigurationService;
    @Mock private ComputationService computationService;


    @InjectMocks
    private TaskExecutorService taskExecutorService;

    private static final String CHAIN_TASK_ID = "0xfoobar";
    private static final String TEE_ENCLAVE_CHALLENGE = "enclaveChallenge";
    private static final String NO_TEE_ENCLAVE_CHALLENGE = BytesUtils.EMPTY_ADDRESS;

    @Before
    public void init() {
        MockitoAnnotations.initMocks(this);
    }

    TaskDescription getStubTaskDescription(boolean isTeeTask) {
        return TaskDescription.builder()
                .chainTaskId(CHAIN_TASK_ID)
                .appType(DappType.DOCKER)
                .appUri("appUri")
                .datasetUri("datasetUri")
                .isTeeTask(isTeeTask)
                .build();
    }

    ContributionAuthorization getStubAuth(String enclaveChallenge) {
        return ContributionAuthorization.builder()
                .chainTaskId(CHAIN_TASK_ID)
                .enclaveChallenge(enclaveChallenge)
                .build();
    }

    // addReplicate()

    @Test
    public void shouldNotAddReplicateWhenTaskNotInitializedOnchain() {
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(false);
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(false)));

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(customFeignClient, never())
                .updateReplicateStatus(CHAIN_TASK_ID, ReplicateStatus.RUNNING);
    }

    @Test
    public void shouldNotAddReplicateWhenTeeRequiredButNotSupported() {
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(true);
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(true)));
        when(workerConfigurationService.isTeeEnabled()).thenReturn(false);

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(customFeignClient, never())
                .updateReplicateStatus(CHAIN_TASK_ID, ReplicateStatus.RUNNING);
    }

    @Test
    public void shouldAddReplicateWithNoTeeRequired() {
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(true);
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(false)));
        when(workerConfigurationService.isTeeEnabled()).thenReturn(false);

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(customFeignClient, times(1))
                .updateReplicateStatus(CHAIN_TASK_ID, ReplicateStatus.RUNNING);
    }

    @Test
    public void shouldAddReplicateWithTeeRequired() {
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(true)));
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(true);
        when(workerConfigurationService.isTeeEnabled()).thenReturn(true);

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(customFeignClient, times(1))
                .updateReplicateStatus(CHAIN_TASK_ID, ReplicateStatus.RUNNING);
    }

    // compute()

    @Test
    public void shouldComputeNonTeeTask() {
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(true);
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(false)));
        when(workerConfigurationService.isTeeEnabled()).thenReturn(false);
        when(taskExecutorHelperService.checkAppType(any(), any())).thenReturn("");
        when(taskExecutorHelperService.tryToDownloadApp(any())).thenReturn("");
        when(taskExecutorHelperService.tryToDownloadData(any(), any())).thenReturn("");
        when(taskExecutorHelperService.checkContributionAbility(any())).thenReturn("");
        when(taskExecutorHelperService.checkIfAppImageExists(any(), any())).thenReturn("");

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(computationService, times(1))
                .runNonTeeComputation(any(), any());
    }

    @Test
    public void shouldComputeTeeTask() {
        when(contributionService.isChainTaskInitialized(CHAIN_TASK_ID)).thenReturn(true);
        when(iexecHubService.getTaskDescriptionFromChain(CHAIN_TASK_ID))
                .thenReturn(Optional.of(getStubTaskDescription(true)));
        when(workerConfigurationService.isTeeEnabled()).thenReturn(true);
        when(taskExecutorHelperService.checkAppType(any(), any())).thenReturn("");
        when(taskExecutorHelperService.tryToDownloadApp(any())).thenReturn("");
        when(taskExecutorHelperService.tryToDownloadData(any(), any())).thenReturn("");
        when(taskExecutorHelperService.checkContributionAbility(any())).thenReturn("");
        when(taskExecutorHelperService.checkIfAppImageExists(any(), any())).thenReturn("");

        CompletableFuture<Boolean> future = taskExecutorService.addReplicate(getStubAuth(TEE_ENCLAVE_CHALLENGE));
        future.join();

        verify(computationService, times(1))
                .runTeeComputation(any(), any());
    }

    // contribute()

    @Test
    public void shouldContribute() {
        ContributionAuthorization contributionAuth = getStubAuth(NO_TEE_ENCLAVE_CHALLENGE);
        String hash = "hash";
        Signature enclaveSignature = new Signature();

        when(taskExecutorHelperService.getTaskDeterminismHash(CHAIN_TASK_ID)).thenReturn(hash);
        when(taskExecutorHelperService.getVerifiedEnclaveSignature(CHAIN_TASK_ID, NO_TEE_ENCLAVE_CHALLENGE))
                .thenReturn(Optional.of(new Signature()));
        when(taskExecutorHelperService.checkContributionAbility(CHAIN_TASK_ID)).thenReturn("");
        when(taskExecutorHelperService.checkGasBalance(CHAIN_TASK_ID)).thenReturn(true);

        taskExecutorService.contribute(contributionAuth);

        verify(contributionService, times(1)).contribute(contributionAuth, hash, enclaveSignature);
    }

    // reveal()

    @Test
    public void shouldReveal() {
        String hash = "hash";
        long consensusBlock = 55;

        when(taskExecutorHelperService.getTaskDeterminismHash(CHAIN_TASK_ID)).thenReturn(hash);
        when(revealService.isConsensusBlockReached(CHAIN_TASK_ID, consensusBlock)).thenReturn(true);
        when(revealService.canReveal(CHAIN_TASK_ID, hash)).thenReturn(true);
        when(taskExecutorHelperService.checkGasBalance(CHAIN_TASK_ID)).thenReturn(true);

        taskExecutorService.reveal(CHAIN_TASK_ID, consensusBlock);

        verify(revealService, times(1)).reveal(CHAIN_TASK_ID, hash);
    }

    // uploadResult()

    @Test
    public void shouldUploadResultWithoutEncrypting() {
        ReplicateDetails details = ReplicateDetails.builder()
        .resultLink("resultUri")
        .chainCallbackData("callbackData")
        .build();

        when(resultService.isResultEncryptionNeeded(CHAIN_TASK_ID)).thenReturn(false);
        when(resultService.uploadResult(CHAIN_TASK_ID)).thenReturn(details.getResultLink());
        when(resultService.getCallbackDataFromFile(CHAIN_TASK_ID)).thenReturn(details.getChainCallbackData());

        taskExecutorService.uploadResult(CHAIN_TASK_ID);

        verify(resultService, never()).encryptResult(CHAIN_TASK_ID);
    }

    @Test
    public void shouldEncryptAndUploadResult() {
        ReplicateDetails details = ReplicateDetails.builder()
        .resultLink("resultUri")
        .chainCallbackData("callbackData")
        .build();

        when(resultService.isResultEncryptionNeeded(CHAIN_TASK_ID)).thenReturn(true);
        when(resultService.encryptResult(CHAIN_TASK_ID)).thenReturn(true);
        when(resultService.uploadResult(CHAIN_TASK_ID)).thenReturn(details.getResultLink());
        when(resultService.getCallbackDataFromFile(CHAIN_TASK_ID)).thenReturn(details.getChainCallbackData());

        taskExecutorService.uploadResult(CHAIN_TASK_ID);

        verify(resultService, times(1)).encryptResult(CHAIN_TASK_ID);
    }

    @Test
    public void shouldNotUploadResultSinceNotEncryptedWhenNeeded() {
        when(resultService.isResultEncryptionNeeded(CHAIN_TASK_ID)).thenReturn(true);
        when(resultService.encryptResult(CHAIN_TASK_ID)).thenReturn(false);

        taskExecutorService.uploadResult(CHAIN_TASK_ID);

        verify(resultService, never()).uploadResult(CHAIN_TASK_ID);
    }

    @Test
    public void shouldUpdateReplicateAfterUploadResult() {
        String chainTaskId = "chainTaskId";
        ReplicateDetails details = ReplicateDetails.builder()
                .resultLink("resultUri")
                .chainCallbackData("callbackData")
                .build();

        when(resultService.isResultEncryptionNeeded(chainTaskId)).thenReturn(false);
        when(resultService.uploadResult(chainTaskId)).thenReturn(details.getResultLink());
        when(resultService.getCallbackDataFromFile(chainTaskId)).thenReturn(details.getChainCallbackData());

        taskExecutorService.uploadResult(chainTaskId);

        verify(customFeignClient, never())
                .updateReplicateStatus(chainTaskId, RESULT_UPLOAD_FAILED);
        verify(customFeignClient, times(1))
                .updateReplicateStatus(chainTaskId, RESULT_UPLOADED, details);
    }

    @Test
    public void shouldNotUpdateReplicateAfterUploadingResultSinceEmptyUri() {
        String chainTaskId = "chainTaskId";
        ReplicateDetails details = ReplicateDetails.builder()
                .resultLink("")
                .chainCallbackData("callbackData")
                .build();

        when(resultService.isResultEncryptionNeeded(chainTaskId)).thenReturn(false);
        when(resultService.uploadResult(chainTaskId)).thenReturn(details.getResultLink());
        when(resultService.getCallbackDataFromFile(chainTaskId)).thenReturn(details.getChainCallbackData());

        taskExecutorService.uploadResult(chainTaskId);

        verify(customFeignClient, times(1))
                .updateReplicateStatus(chainTaskId, RESULT_UPLOAD_FAILED);
        verify(customFeignClient, times(0))
                .updateReplicateStatus(chainTaskId, RESULT_UPLOADED, details);
    }
}