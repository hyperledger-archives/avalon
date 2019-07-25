package com.iexec.eea.worker.executor;

import com.iexec.eea.worker.chain.model.ChainWorkOrder;
import com.iexec.eea.worker.config.WorkerConfigurationService;
import com.iexec.eea.worker.docker.CustomDockerClient;
import com.iexec.eea.worker.utils.FileHelper;
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
    private static final String RESULT_SIGNATURE_FILE = "enclaveSig.iexec";

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

        // Input
        String imageUri = params.getAppUri();
        String cmd = params.getCmd();
        long maxExecutionTime = params.getMaxExecutionTime();

        try {
            // Try to download the app
            log.info("Downloading container image [workOrderId:{}, imageUri:{}]", workOrderId, imageUri);
            taskExecutorHelperService.downloadApp(workOrder);

            // Check the image
            log.info("Checking if container image exists [workOrderId:{}, imageUri:{}]", workOrderId, imageUri);
            taskExecutorHelperService.checkIfAppImageExists(workOrder, params.getAppUri());

            // Set the environment
            List<String> env = Arrays.asList(
                    WORK_ORDER_ID_ENV + "=" + workOrderId,
                    WORKER_ID_ENV     + "=" + workOrder.getWorkerId()
            );

            // Compute
            log.info("Running container [workOrderId:{}, imageUri:{}]", workOrderId, imageUri);
            ContainerConfig containerConfig = customDockerClient.buildContainerConfig(workOrderId, imageUri, env , cmd);
            log.info("ContainerConfig:" + containerConfig);
            long status = customDockerClient.dockerRun(workOrderId, containerConfig, maxExecutionTime);
            log.info("Container terminated [workOrderId:{}, status:{}]", workOrderId, status);

            return (int) status;
        } catch(TaskExecutionException e) {
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
        return FileHelper.readFileInString(workerConfigurationService.getTaskOutputDir(workOrderId) +
                File.separatorChar + RESULT_SIGNATURE_FILE);
    }

}