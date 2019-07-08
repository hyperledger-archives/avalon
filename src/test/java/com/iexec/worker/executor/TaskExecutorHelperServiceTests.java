package com.iexec.worker.executor;

import com.iexec.common.chain.ChainReceipt;
import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.dapp.DappType;
import com.iexec.common.security.Signature;
import com.iexec.common.task.TaskDescription;
import com.iexec.common.utils.BytesUtils;
import com.iexec.common.utils.SignatureUtils;
import com.iexec.worker.chain.ContributionService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.dataset.DatasetService;
import com.iexec.worker.docker.ComputationService;
import com.iexec.worker.docker.CustomDockerClient;
import com.iexec.worker.feign.CustomFeignClient;
import com.iexec.worker.result.ResultService;
import com.iexec.worker.tee.scone.SconeEnclaveSignatureFile;
import com.iexec.worker.tee.scone.SconeTeeService;

import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Optional;

import static com.iexec.common.replicate.ReplicateStatus.*;
import static org.assertj.core.api.Java6Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;


public class TaskExecutorHelperServiceTests {

    @Mock private DatasetService datasetService;
    @Mock private ResultService resultService;
    @Mock private ContributionService contributionService;
    @Mock private CustomFeignClient customFeignClient;
    @Mock private WorkerConfigurationService workerConfigurationService;
    @Mock private SconeTeeService sconeTeeService;
    @Mock private IexecHubService iexecHubService;
    @Mock private CustomDockerClient customDockerClient;
    @Mock private ComputationService computationService;

    @InjectMocks
    private TaskExecutorHelperService taskExecutorHelperService;

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

    @Test
    public void ShouldAppTypeBeDocker() {
        String error = taskExecutorHelperService.checkAppType(CHAIN_TASK_ID, DappType.DOCKER);

        assertThat(error).isEmpty();
    }

    @Test
    public void shouldDownloadApp() {
        TaskDescription task = getStubTaskDescription(false);
        when(contributionService.getCannotContributeStatus(CHAIN_TASK_ID))
                .thenReturn(Optional.empty());
        when(computationService.downloadApp(CHAIN_TASK_ID, task.getAppUri()))
                .thenReturn(true);

        String error = taskExecutorHelperService.tryToDownloadApp(task);

        assertThat(error).isEmpty();
    }

    @Test
    public void shouldDownloadData() {
        TaskDescription task = getStubTaskDescription(false);
        when(contributionService.getCannotContributeStatus(CHAIN_TASK_ID))
                .thenReturn(Optional.empty());
        when(datasetService.downloadDataset(CHAIN_TASK_ID, task.getDatasetUri()))
                .thenReturn(true);

        String error = taskExecutorHelperService.tryToDownloadData(CHAIN_TASK_ID, task.getDatasetUri());
        assertThat(error).isEmpty();
    }

    @Test
    public void shouldBeAbleToContribute() {
        when(contributionService.getCannotContributeStatus(CHAIN_TASK_ID))
                .thenReturn(Optional.empty());

        String error = taskExecutorHelperService.checkContributionAbility(CHAIN_TASK_ID);
        assertThat(error).isEmpty();
    }

    @Test
    public void shouldNotBeAbleToContribute() {
        when(contributionService.getCannotContributeStatus(CHAIN_TASK_ID))
                .thenReturn(Optional.of(CANT_CONTRIBUTE_SINCE_CHAIN_UNREACHABLE));

        String error = taskExecutorHelperService.checkContributionAbility(CHAIN_TASK_ID);
        assertThat(error).isEqualTo("Cannot contribute");
    }

    @Test
    public void shouldFindAppImage() {
        TaskDescription task = getStubTaskDescription(false);
        when(customDockerClient.isImagePulled(task.getAppUri())).thenReturn(true);
        
        String error = taskExecutorHelperService.checkIfAppImageExists(CHAIN_TASK_ID, task.getAppUri());
        assertThat(error).isEmpty();
    }

    @Test
    public void shouldGetDeterminismHash() {
        String expectedHash = "expectedHash";

        when(resultService.getTaskDeterminismHash(CHAIN_TASK_ID)).thenReturn(expectedHash);
        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(false);
        
        String hash = taskExecutorHelperService.getTaskDeterminismHash(CHAIN_TASK_ID);
        assertThat(hash).isEqualTo(expectedHash);
    }

    @Test
    public void shouldNotGetNonTeeDeterminismHash() {
        when(resultService.getTaskDeterminismHash(CHAIN_TASK_ID)).thenReturn("");
        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(false);

        String hash = taskExecutorHelperService.getTaskDeterminismHash(CHAIN_TASK_ID);
        assertThat(hash).isEmpty();
        verify(customFeignClient, times(1)).updateReplicateStatus(CHAIN_TASK_ID,
                CANT_CONTRIBUTE_SINCE_DETERMINISM_HASH_NOT_FOUND);
    }

    @Test
    public void shouldNotGetTeeDeterminismHash() {
        when(resultService.getTaskDeterminismHash(CHAIN_TASK_ID)).thenReturn("");
        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(true);

        String hash = taskExecutorHelperService.getTaskDeterminismHash(CHAIN_TASK_ID);
        assertThat(hash).isEmpty();
        verify(customFeignClient, times(1)).updateReplicateStatus(CHAIN_TASK_ID,
                CANT_CONTRIBUTE_SINCE_TEE_EXECUTION_NOT_VERIFIED);
    }

    @Test
    public void shouldGetNonTeeEnclaveSignature() {
        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(false);

        Optional<Signature> sign =
                taskExecutorHelperService.getVerifiedEnclaveSignature(CHAIN_TASK_ID, NO_TEE_ENCLAVE_CHALLENGE);
        assertThat(sign.get()).isEqualTo(SignatureUtils.emptySignature());
    }

    @Test
    public void shouldGetTeeVerifiedEnclaveSignature() {
        SconeEnclaveSignatureFile sconeFile = SconeEnclaveSignatureFile.builder()
                .signature("signature")
                .resultHash("resultHash")
                .resultSalt("resultSalt")
                .build();

        Signature expectedSign = new Signature(sconeFile.getSignature());

        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(true);
        when(resultService.readSconeEnclaveSignatureFile(CHAIN_TASK_ID))
                .thenReturn(Optional.of(sconeFile));
        when(sconeTeeService.isEnclaveSignatureValid(any(), any(), any(), any())).thenReturn(true);

        Optional<Signature> oSign =
                taskExecutorHelperService.getVerifiedEnclaveSignature(CHAIN_TASK_ID, TEE_ENCLAVE_CHALLENGE);
        assertThat(oSign.get()).isEqualTo(expectedSign);
    }

    @Test
    public void shouldNotGetTeeEnclaveSignatureSinceNotValid() {
        String enclaveChallenge = "dummyEnclaveChallenge";
        SconeEnclaveSignatureFile sconeFile = SconeEnclaveSignatureFile.builder()
                .signature("signature")
                .resultHash("resultHash")
                .resultSalt("resultSalt")
                .build();

        when(iexecHubService.isTeeTask(CHAIN_TASK_ID)).thenReturn(true);
        when(resultService.readSconeEnclaveSignatureFile(CHAIN_TASK_ID))
                .thenReturn(Optional.of(sconeFile));
        when(sconeTeeService.isEnclaveSignatureValid(any(), any(), any(), any())).thenReturn(false);

        Optional<Signature> oSign =
                taskExecutorHelperService.getVerifiedEnclaveSignature(CHAIN_TASK_ID, enclaveChallenge);
        assertThat(oSign.isPresent()).isFalse();
    }

    @Test
    public void shouldFindEnoughGasBalance() {
        when(iexecHubService.hasEnoughGas()).thenReturn(true);
        assertThat(taskExecutorHelperService.checkGasBalance(CHAIN_TASK_ID)).isTrue();
    }

    @Test
    public void shouldNotFindEnoughGasBalance() {
        when(iexecHubService.hasEnoughGas()).thenReturn(false);
        assertThat(taskExecutorHelperService.checkGasBalance(CHAIN_TASK_ID)).isFalse();
        verify(customFeignClient, times(1)).updateReplicateStatus(CHAIN_TASK_ID, OUT_OF_GAS);
    }

    @Test
    public void shouldFindChainReceiptValid() {
        Optional<ChainReceipt> receipt = Optional.of(new ChainReceipt(5, "txHash"));

        boolean isValid = taskExecutorHelperService.isValidChainReceipt(CHAIN_TASK_ID, receipt);
        assertThat(isValid).isTrue();
    }

    @Test
    public void shouldFindChainReceiptNotValidSinceBlockIsZero() {
        Optional<ChainReceipt> receipt = Optional.of(new ChainReceipt(0, "txHash"));

        boolean isValid = taskExecutorHelperService.isValidChainReceipt(CHAIN_TASK_ID, receipt);
        assertThat(isValid).isFalse();
    }

}