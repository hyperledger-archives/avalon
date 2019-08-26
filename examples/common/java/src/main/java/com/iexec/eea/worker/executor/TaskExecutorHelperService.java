package com.iexec.eea.worker.executor;

import com.iexec.eea.worker.chain.model.ChainWorkOrder;
import com.iexec.eea.worker.config.WorkerConfigurationService;
import com.iexec.eea.worker.dapp.DappType;
import com.iexec.eea.worker.docker.CustomDockerClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;


@Slf4j
@Service
public class TaskExecutorHelperService {

    private WorkerConfigurationService workerConfigurationService;
    private CustomDockerClient customDockerClient;

    public TaskExecutorHelperService(WorkerConfigurationService workerConfigurationService,
                                     CustomDockerClient customDockerClient) {
        this.workerConfigurationService = workerConfigurationService;
        this.customDockerClient = customDockerClient;
    }

    public void checkAppType(String workOrderId, DappType type) throws TaskExecutionException {
        if (!type.equals(DappType.DOCKER))
            throw new TaskExecutionException(workOrderId,
                    "Application is not of type Docker");
    }

    public void downloadApp(ChainWorkOrder workOrder) throws  TaskExecutionException {
        String workOrderId = workOrder.getWorkerId();
        String appUri = workOrder.getParams().getAppUri();

        if(!customDockerClient.pullImage(workOrderId, appUri))
            throw new TaskExecutionException(workOrderId,
                    "Failed to pull application image, URL: " + appUri);
    }

    public void checkIfAppImageExists(ChainWorkOrder workOrder, String imageUri)
            throws TaskExecutionException {
        if(!customDockerClient.isImagePulled(imageUri))
            throw new TaskExecutionException(workOrder.getWorkOrderId(),
                    "Application image not found,  imageUri: " + imageUri);
    }
}