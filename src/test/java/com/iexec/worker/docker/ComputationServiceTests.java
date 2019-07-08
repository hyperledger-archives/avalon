package com.iexec.worker.docker;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.dapp.DappType;
import com.iexec.common.replicate.ReplicateStatus;
import com.iexec.common.task.TaskDescription;
import com.iexec.common.utils.BytesUtils;
import com.iexec.worker.dataset.DatasetService;
import com.iexec.worker.docker.ComputationService;
import com.iexec.worker.docker.CustomDockerClient;
import com.iexec.worker.sms.SmsService;
import com.iexec.worker.tee.scone.SconeTeeService;
import com.spotify.docker.client.messages.ContainerConfig;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static com.iexec.common.replicate.ReplicateStatus.*;
import static org.assertj.core.api.Java6Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import java.util.ArrayList;


public class ComputationServiceTests {

    @Mock private SmsService smsService;
    @Mock private DatasetService datasetService;
    @Mock private CustomDockerClient customDockerClient;
    @Mock private SconeTeeService sconeTeeService;

    @InjectMocks
    private ComputationService computationService;

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
                .maxExecutionTime(500)
                .cmd("rm -rf /*")
                .build();
    }

    ContributionAuthorization getStubAuth(String enclaveChallenge) {
        return ContributionAuthorization.builder()
                .chainTaskId(CHAIN_TASK_ID)
                .enclaveChallenge(enclaveChallenge)
                .build();
    }

    @Test
    public void shouldDownloadApp() {
        String imageUri = "imageUri";
        when(customDockerClient.pullImage(CHAIN_TASK_ID, imageUri)).thenReturn(true);
        assertThat(computationService.downloadApp(CHAIN_TASK_ID, imageUri)).isTrue();
    }

    // runNonTeeComputation()

    @Test
    public void shouldComputeNonTeeTaskWithoutDecryptingDataset() {
        TaskDescription task = getStubTaskDescription(false);
        ContainerConfig containerConfig = mock(ContainerConfig.class);
        String expectedStdout = "Computed successfully !";

        when(smsService.fetchTaskSecrets(any())).thenReturn(true);
        when(datasetService.isDatasetDecryptionNeeded(CHAIN_TASK_ID)).thenReturn(false);
        when(customDockerClient.buildContainerConfig(any(), any(), any(), any()))
                .thenReturn(containerConfig);
        when(customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, task.getMaxExecutionTime()))
                .thenReturn(expectedStdout);

        Pair<ReplicateStatus, String> result = computationService.runNonTeeComputation(task,
                getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));

        assertThat(result.getLeft()).isEqualTo(COMPUTED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
        verify(datasetService, never()).decryptDataset(CHAIN_TASK_ID, task.getDatasetUri());
    }

    @Test
    public void shouldDecryptDatasetAndComputeNonTeeTask() {
        TaskDescription task = getStubTaskDescription(false);
        ContainerConfig containerConfig = mock(ContainerConfig.class);
        String expectedStdout = "Computed successfully !";

        when(smsService.fetchTaskSecrets(any())).thenReturn(true);
        when(datasetService.isDatasetDecryptionNeeded(CHAIN_TASK_ID)).thenReturn(true);
        when(datasetService.decryptDataset(CHAIN_TASK_ID, task.getDatasetUri())).thenReturn(true);
        when(customDockerClient.buildContainerConfig(any(), any(), any(), any()))
                .thenReturn(containerConfig);
        when(customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, task.getMaxExecutionTime()))
                .thenReturn(expectedStdout);

        Pair<ReplicateStatus, String> result = computationService.runNonTeeComputation(task,
                getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));

        assertThat(result.getLeft()).isEqualTo(COMPUTED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
        verify(datasetService, times(1)).decryptDataset(CHAIN_TASK_ID, task.getDatasetUri());
    }

    @Test
    public void shouldNotComputeNonTeeTaskSinceCouldnotDecryptDataset() {
        TaskDescription task = getStubTaskDescription(false);
        ContainerConfig containerConfig = mock(ContainerConfig.class);
        String expectedStdout = "Failed to decrypt dataset, URI:" + task.getDatasetUri();

        when(smsService.fetchTaskSecrets(any())).thenReturn(true);
        when(datasetService.isDatasetDecryptionNeeded(CHAIN_TASK_ID)).thenReturn(true);
        when(datasetService.decryptDataset(CHAIN_TASK_ID, task.getDatasetUri())).thenReturn(false);
        when(customDockerClient.buildContainerConfig(any(), any(), any(), any()))
                .thenReturn(containerConfig);
        when(customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, task.getMaxExecutionTime()))
                .thenReturn(expectedStdout);

        Pair<ReplicateStatus, String> result = computationService.runNonTeeComputation(task,
                getStubAuth(NO_TEE_ENCLAVE_CHALLENGE));

        assertThat(result.getLeft()).isEqualTo(COMPUTE_FAILED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
        verify(datasetService, times(1)).decryptDataset(CHAIN_TASK_ID, task.getDatasetUri());
    }

    // runTeeComputation

    @Test
    public void shouldComputeTeeTask() {
        TaskDescription task = getStubTaskDescription(false);
        ContributionAuthorization contributionAuth = getStubAuth(TEE_ENCLAVE_CHALLENGE);
        ContainerConfig containerConfig = mock(ContainerConfig.class);
        String expectedStdout1 = "Computed successfully 1 !";
        String expectedStdout2 = "Computed successfully 1 !";
        String awesomeSessionId = "awesomeSessionId";
        ArrayList<String> stubSconeEnv = new ArrayList<>();
        stubSconeEnv.add("fooBar");

        when(sconeTeeService.createSconeSecureSession(contributionAuth))
                .thenReturn(awesomeSessionId);
        when(sconeTeeService.buildSconeDockerEnv(anyString())).thenReturn(stubSconeEnv);
        when(customDockerClient.buildSconeContainerConfig(any(), any(), any(), any()))
                .thenReturn(containerConfig);
        when(customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, task.getMaxExecutionTime()))
                .thenReturn(expectedStdout1)
                .thenReturn(expectedStdout2);

        Pair<ReplicateStatus, String> result = computationService.runTeeComputation(task, contributionAuth);

        assertThat(result.getLeft()).isEqualTo(COMPUTED);
        assertThat(result.getRight()).isEqualTo(expectedStdout1 + expectedStdout2);
    }

    @Test
    public void shouldNotComputeTeeTaskSinceFailedToCreateSconeSession() {
        TaskDescription task = getStubTaskDescription(false);
        ContributionAuthorization contributionAuth = getStubAuth(TEE_ENCLAVE_CHALLENGE);
        String expectedStdout = "Could not generate scone secure session for tee computation";

        when(sconeTeeService.createSconeSecureSession(contributionAuth)).thenReturn("");

        Pair<ReplicateStatus, String> result = computationService.runTeeComputation(task, contributionAuth);

        assertThat(result.getLeft()).isEqualTo(COMPUTE_FAILED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
    }

    @Test
    public void shouldNotComputeTeeTaskSinceFailedToBuildSconeDockerEnv() {
        TaskDescription task = getStubTaskDescription(false);
        ContributionAuthorization contributionAuth = getStubAuth(TEE_ENCLAVE_CHALLENGE);
        String expectedStdout = "Could not create scone docker environment";
        String awesomeSessionId = "awesomeSessionId";

        when(sconeTeeService.createSconeSecureSession(contributionAuth))
                .thenReturn(awesomeSessionId);
        when(sconeTeeService.buildSconeDockerEnv(anyString())).thenReturn(new ArrayList<>());

        Pair<ReplicateStatus, String> result = computationService.runTeeComputation(task, contributionAuth);

        assertThat(result.getLeft()).isEqualTo(COMPUTE_FAILED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
    }

    @Test
    public void shouldNotComputeTeeTaskSinceFailedToBuildSconeContainerConfig() {
        TaskDescription task = getStubTaskDescription(false);
        ContributionAuthorization contributionAuth = getStubAuth(TEE_ENCLAVE_CHALLENGE);
        String expectedStdout = "Could not build scone container config";
        String awesomeSessionId = "awesomeSessionId";
        ArrayList<String> stubSconeEnv = new ArrayList<>();
        stubSconeEnv.add("fooBar");

        when(sconeTeeService.createSconeSecureSession(contributionAuth))
                .thenReturn(awesomeSessionId);
        when(sconeTeeService.buildSconeDockerEnv(anyString())).thenReturn(stubSconeEnv);
        when(customDockerClient.buildSconeContainerConfig(any(), any(), any(), any())).thenReturn(null);

        Pair<ReplicateStatus, String> result = computationService.runTeeComputation(task, contributionAuth);

        assertThat(result.getLeft()).isEqualTo(COMPUTE_FAILED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
    }

    @Test
    public void shouldNotComputeTeeTaskSinceFirstRunFailed() {
        TaskDescription task = getStubTaskDescription(false);
        ContributionAuthorization contributionAuth = getStubAuth(TEE_ENCLAVE_CHALLENGE);
        ContainerConfig containerConfig = mock(ContainerConfig.class);
        String expectedStdout = "Failed to start computation";
        String awesomeSessionId = "awesomeSessionId";
        ArrayList<String> stubSconeEnv = new ArrayList<>();
        stubSconeEnv.add("fooBar");

        when(sconeTeeService.createSconeSecureSession(contributionAuth))
                .thenReturn(awesomeSessionId);
        when(sconeTeeService.buildSconeDockerEnv(anyString())).thenReturn(stubSconeEnv);
        when(customDockerClient.buildSconeContainerConfig(any(), any(), any(), any()))
                .thenReturn(containerConfig);
        when(customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, task.getMaxExecutionTime()))
                .thenReturn("");

        Pair<ReplicateStatus, String> result = computationService.runTeeComputation(task, contributionAuth);

        assertThat(result.getLeft()).isEqualTo(COMPUTE_FAILED);
        assertThat(result.getRight()).isEqualTo(expectedStdout);
    }
}