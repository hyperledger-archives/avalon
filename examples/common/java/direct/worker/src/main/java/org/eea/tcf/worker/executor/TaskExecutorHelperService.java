  /*****************************************************************************
  * Copyright 2019 iExec Blockchain Tech
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  *     http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *****************************************************************************/
package org.eea.tcf.worker.executor;

import org.eea.tcf.worker.chain.model.ChainWorkOrder;
import org.eea.tcf.worker.config.WorkerConfigurationService;
import org.eea.tcf.worker.dapp.DappType;
import org.eea.tcf.worker.docker.CustomDockerClient;
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

    public void checkAppType(String workOrderId, DappType type)
            throws TaskExecutionException {
        if (!type.equals(DappType.DOCKER))
            throw new TaskExecutionException(workOrderId,
                    "Application is not of type Docker");
    }

    public void downloadApp(ChainWorkOrder workOrder)
            throws  TaskExecutionException {
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