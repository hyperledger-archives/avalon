package com.iexec.worker.docker;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.replicate.ReplicateStatus;
import com.iexec.common.task.TaskDescription;
import com.iexec.worker.dataset.DatasetService;
import com.iexec.worker.docker.CustomDockerClient;
import com.iexec.worker.sms.SmsService;
import com.iexec.worker.tee.scone.SconeTeeService;
import com.iexec.worker.utils.FileHelper;
import org.apache.commons.lang3.tuple.Pair;
import com.spotify.docker.client.messages.ContainerConfig;

import org.springframework.stereotype.Service;

import lombok.extern.slf4j.Slf4j;

import static com.iexec.common.replicate.ReplicateStatus.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


@Slf4j
@Service
public class ComputationService {

    private static final String DATASET_FILENAME = "DATASET_FILENAME";

    private SmsService smsService;
    private DatasetService datasetService;
    private CustomDockerClient customDockerClient;
    private SconeTeeService sconeTeeService;

    public ComputationService(SmsService smsService,
                              DatasetService datasetService,
                              CustomDockerClient customDockerClient,
                              SconeTeeService sconeTeeService) {

        this.smsService = smsService;
        this.datasetService = datasetService;
        this.customDockerClient = customDockerClient;
        this.sconeTeeService = sconeTeeService;
    }

    public boolean downloadApp(String chainTaskId, String appUri) {
        return customDockerClient.pullImage(chainTaskId, appUri);
    }

    public Pair<ReplicateStatus, String> runNonTeeComputation(TaskDescription taskDescription,
                                                              ContributionAuthorization contributionAuth) {
        String chainTaskId = taskDescription.getChainTaskId();
        String imageUri = taskDescription.getAppUri();
        String cmd = taskDescription.getCmd();
        long maxExecutionTime = taskDescription.getMaxExecutionTime();
        String stdout = "";

        // fetch task secrets from SMS
        boolean isFetched = smsService.fetchTaskSecrets(contributionAuth);
        if (!isFetched) {
            log.warn("No secrets fetched for this task, will continue [chainTaskId:{}]:", chainTaskId);
        }

        // decrypt data
        boolean isDatasetDecryptionNeeded = datasetService.isDatasetDecryptionNeeded(chainTaskId);
        boolean isDatasetDecrypted = false;

        if (isDatasetDecryptionNeeded) {
            isDatasetDecrypted = datasetService.decryptDataset(chainTaskId, taskDescription.getDatasetUri());
        }

        if (isDatasetDecryptionNeeded && !isDatasetDecrypted) {
            stdout = "Failed to decrypt dataset, URI:" + taskDescription.getDatasetUri();
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        // compute
        String datasetFilename = FileHelper.getFilenameFromUri(taskDescription.getDatasetUri());
        List<String> env = Arrays.asList(DATASET_FILENAME + "=" + datasetFilename);

        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(chainTaskId, imageUri, env, cmd);
        stdout = customDockerClient.dockerRun(chainTaskId, containerConfig, maxExecutionTime);

        if (stdout.isEmpty()) {
            stdout = "Failed to start computation";
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        return Pair.of(COMPUTED, stdout);        
    }

    public Pair<ReplicateStatus, String> runTeeComputation(TaskDescription taskDescription,
                                                           ContributionAuthorization contributionAuth) {
        String chainTaskId = contributionAuth.getChainTaskId();
        String imageUri = taskDescription.getAppUri();
        String datasetUri = taskDescription.getDatasetUri();
        String cmd = taskDescription.getCmd();
        long maxExecutionTime = taskDescription.getMaxExecutionTime();
        String stdout = "";

        String secureSessionId = sconeTeeService.createSconeSecureSession(contributionAuth);

        if (secureSessionId.isEmpty()) {
            stdout = "Could not generate scone secure session for tee computation";
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        ArrayList<String> sconeAppEnv = sconeTeeService.buildSconeDockerEnv(secureSessionId + "/app");
        ArrayList<String> sconeEncrypterEnv = sconeTeeService.buildSconeDockerEnv(secureSessionId + "/encryption");

        if (sconeAppEnv.isEmpty() || sconeEncrypterEnv.isEmpty()) {
            stdout = "Could not create scone docker environment";
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        String datasetFilename = FileHelper.getFilenameFromUri(datasetUri);
        String datasetEnv = DATASET_FILENAME + "=" + datasetFilename;
        sconeAppEnv.add(datasetEnv);
        sconeEncrypterEnv.add(datasetEnv);

        ContainerConfig sconeAppConfig = customDockerClient.buildSconeContainerConfig(chainTaskId, imageUri, sconeAppEnv, cmd);
        ContainerConfig sconeEncrypterConfig = customDockerClient.buildSconeContainerConfig(chainTaskId, imageUri, sconeEncrypterEnv, cmd);

        if (sconeAppConfig == null || sconeEncrypterConfig == null) {
            stdout = "Could not build scone container config";
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        // run computation
        stdout = customDockerClient.dockerRun(chainTaskId, sconeAppConfig, maxExecutionTime);

        if (stdout.isEmpty()) {
            stdout = "Failed to start computation";
            log.error(stdout + " [chainTaskId:{}]", chainTaskId);
            return Pair.of(COMPUTE_FAILED, stdout);
        }

        // encrypt result
        stdout += customDockerClient.dockerRun(chainTaskId, sconeEncrypterConfig, maxExecutionTime);
        return Pair.of(COMPUTED, stdout);
    }
}