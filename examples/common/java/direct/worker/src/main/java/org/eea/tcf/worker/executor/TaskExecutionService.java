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
import org.eea.tcf.worker.docker.CustomDockerClient;
import org.eea.tcf.worker.utils.FileHelper;
import com.spotify.docker.client.messages.ContainerConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;


@Slf4j
@Service
public class TaskExecutionService {

    private static final String RESULT_FILE = "result.txt";
    private static final String RESULT_SIGNATURE_FILE = "enclaveSig.eea";

    private static final String WORKER_ID_ENV = "WORKER_ID";
    private static final String WORK_ORDER_ID_ENV = "WORK_ORDER_ID";

    private WorkerConfigurationService workerConfigurationService;
    private TaskExecutorHelperService taskExecutorHelperService;
    private CustomDockerClient customDockerClient;

    private int nbThreads;
    private ThreadPoolExecutor executor;

    public TaskExecutionService(WorkerConfigurationService workerConfigurationService,
                                TaskExecutorHelperService taskExecutorHelperService,
                                CustomDockerClient customDockerClient) {
        this.workerConfigurationService = workerConfigurationService;
        this.taskExecutorHelperService = taskExecutorHelperService;
        this.customDockerClient = customDockerClient;

        // TODO add parallelism here
        nbThreads = 1;
        executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(1);
    }

    public CompletableFuture<Integer> scheduleForExecution(ChainWorkOrder workOrder) {
        return CompletableFuture.supplyAsync(() -> compute(workOrder), executor);
    }

    @Async
    private int compute(ChainWorkOrder workOrder) {
        String workOrderId = workOrder.getWorkOrderId();
        ChainWorkOrder.WorkOrderParams params = workOrder.getParams();
        log.info("Computing [workOrderId:{}]", workOrderId);

        // Input
        String imageUri = params.getAppUri();
        String cmd[] = new String[params.getArgs().length + 1];
        long maxExecutionTime = params.getMaxExecutionTime();

        try {
            // Construct command line
            cmd[0] = params.getCmd();
            System.arraycopy(params.getArgs(), 0, cmd, 1,
                    params.getArgs().length);

            // Try to download the app
            log.info("Downloading container image [workOrderId:{}, imageUri:{}]",
                    workOrderId, imageUri);
            taskExecutorHelperService.downloadApp(workOrder);

            // Check the image
            log.info("Checking if container image exists [workOrderId:{}, imageUri:{}]",
                    workOrderId, imageUri);
            taskExecutorHelperService.checkIfAppImageExists(workOrder, params.getAppUri());

            // Set the environment
            List<String> env = Arrays.asList(
                    WORK_ORDER_ID_ENV + "=" + workOrderId,
                    WORKER_ID_ENV     + "=" + workOrder.getWorkerId()
            );

            // Compute
            log.info("Running container [workOrderId:{}, imageUri:{}]",
                    workOrderId, imageUri);
            ContainerConfig containerConfig = customDockerClient.buildContainerConfig(workOrderId, imageUri, env , cmd);
            log.info("ContainerConfig:" + containerConfig);
            long status = customDockerClient.dockerRun(workOrderId,
                    containerConfig, maxExecutionTime);
            log.info("Container terminated [workOrderId:{}, status:{}]",
                    workOrderId, status);

            return (int) status;
        } catch(TaskExecutionException e) {
            log.error("Exception during task execution:\n" + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    public String getWorkOrderResult(ChainWorkOrder workOrder) {
        return getWorkOrderResult(workOrder.getWorkOrderId());
    }

    public String getWorkOrderResult(String workOrderId) {
        // TODO for now the result is not zipped but it will be soon
        // TODO for now we ignore the case in which the zip contains multiple files
        String resultPath = workerConfigurationService.getTaskOutputDir(workOrderId) +
                File.separatorChar + RESULT_FILE;

        return FileHelper.readFileInString(resultPath, resultPath.endsWith(".zip"));
    }

    public String getWorkOrderResultSignature(ChainWorkOrder workOrder) {
        return getWorkOrderResultSignature(workOrder.getWorkOrderId());
    }

    public String getWorkOrderResultSignature(String workOrderId) {
        String path = workerConfigurationService.getTaskOutputDir(workOrderId) +
                File.separatorChar + RESULT_SIGNATURE_FILE;
        return FileHelper.readFileInString(path);
    }

}