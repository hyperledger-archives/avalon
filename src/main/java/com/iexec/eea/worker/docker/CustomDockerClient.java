package com.iexec.eea.worker.docker;

import com.iexec.eea.worker.config.WorkerConfigurationService;
import com.iexec.eea.worker.executor.TaskExecutionException;
import com.iexec.eea.worker.utils.FileHelper;
import com.iexec.eea.worker.utils.WaitUtils;
import com.spotify.docker.client.DefaultDockerClient;
import com.spotify.docker.client.exceptions.DockerCertificateException;
import com.spotify.docker.client.exceptions.DockerException;
import com.spotify.docker.client.messages.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.annotation.PreDestroy;
import java.time.Instant;
import java.util.Date;
import java.util.List;


@Slf4j
@Service
public class CustomDockerClient {

    private static final String EXITED = "exited";

    private DefaultDockerClient docker;
    private WorkerConfigurationService workerConfigurationService;

    public CustomDockerClient(WorkerConfigurationService workerConfigurationService) throws DockerCertificateException {
        docker = DefaultDockerClient.fromEnv().build();
        this.workerConfigurationService = workerConfigurationService;
    }

    public ContainerConfig buildContainerConfig(String chainWorkOrderId, String imageUri, List<String> env, String... cmd) {
        if (imageUri == null || imageUri.isEmpty()) return null;

        HostConfig hostConfig = getHostConfig(chainWorkOrderId);
        if (hostConfig == null) return null;

        return buildCommonContainerConfig(hostConfig, imageUri, env, cmd);
    }

    private ContainerConfig buildCommonContainerConfig(HostConfig hostConfig, String imageUri, List<String> env, String... cmd) {
        ContainerConfig.Builder containerConfigBuilder = ContainerConfig.builder();

        if (cmd != null && cmd.length != 0 && cmd[0] != null) containerConfigBuilder.cmd(cmd);

        if(env != null && !env.isEmpty())
            containerConfigBuilder.env(env);

        return containerConfigBuilder.image(imageUri)
                .hostConfig(hostConfig)
                .build();
    }

    private HostConfig getHostConfig(String chainWorkOrderId) {
        HostConfig.Bind outputBind = createOutputBind(chainWorkOrderId);

        if (outputBind == null) return null;

        return HostConfig.builder()
                .appendBinds(outputBind)
                .build();
    }

    private HostConfig.Bind createOutputBind(String chainWorkOrderId) {
        String outputMountPoint = workerConfigurationService.getTaskOutputDir(chainWorkOrderId);
        return createBind(outputMountPoint, FileHelper.OUT_DIR_PATH);
    }

    private HostConfig.Bind createBind(String source, String dest) {
        if (source == null || source.isEmpty() || dest == null || dest.isEmpty()) return null;

        boolean isSourceMountPointSet = FileHelper.createFolder(source);

        if (!isSourceMountPointSet) {
            log.error("Mount point does not exist on host [mountPoint:{}]", source);
            return null;
        }

        return HostConfig.Bind.from(source)
                .to(dest)
                .readOnly(false)
                .build();
    }

    public boolean pullImage(String chainWorkOrderId, String image) {
        log.info("Image pull started [chainWorkOrderId:{}, image:{}]", chainWorkOrderId, image);

        try {
            docker.pull(image);
        } catch (DockerException | InterruptedException e) {
            log.error("Image pull failed [chainWorkOrderId:{}, image:{}]", chainWorkOrderId, image);
            e.printStackTrace();
            return false;
        }

        log.info("Image pull completed [chainWorkOrderId:{}, image:{}]", chainWorkOrderId, image);
        return true;
    }

    public boolean isImagePulled(String image) {
        try {
            return !docker.inspectImage(image).id().isEmpty();
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to check if image was pulled [image:{}, exception:{}]",
                    image, e);
            return false;
        }
    }

    /**
     * This creates a container, starts, waits then stops it, and returns its logs
     */
    public long dockerRun(String workOrderId, ContainerConfig containerConfig, long maxExecutionTime) throws TaskExecutionException {
        if (containerConfig == null)
            throw new TaskExecutionException(workOrderId, "Could not run computation, container config is null");

        log.info("Running computation [workOrderId:{}, image:{}, cmd:{}]",
                workOrderId, containerConfig.image(), containerConfig.cmd());

        // docker create
        String containerId = createContainer(workOrderId, containerConfig);

        // docker start
        try {
            startContainer(containerId);
        } catch (Exception e) {
            throw new TaskExecutionException(workOrderId, "Could not start container", e);
        }

        Date executionTimeoutDate = Date.from(Instant.now().plusMillis(maxExecutionTime));
        waitContainer(workOrderId, containerId, executionTimeoutDate);

        // docker stop
        long returnCode = -1;
        try {
            returnCode = stopContainer(containerId);
        } catch(Exception e) {
            throw new TaskExecutionException(workOrderId, "Could not stop container", e);
        }

        log.info("Computation completed [workOrderId:{}]", workOrderId);

        // docker rm
        try {
            //removeContainer(containerId);
        } catch (Exception e) {
            throw new TaskExecutionException(workOrderId, "Could not remove container", e);
        }

        return returnCode;
    }

    public String createContainer(String chainWorkOrderId, ContainerConfig containerConfig) {
        log.debug("Creating container [chainWorkOrderId:{}]", chainWorkOrderId);

        if (containerConfig == null) return "";

        ContainerCreation containerCreation;

        try {
            containerCreation = docker.createContainer(containerConfig);
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to create container [chainWorkOrderId:{}, image:{}, cmd:{}]",
                    chainWorkOrderId, containerConfig.image(), containerConfig.cmd());
            e.printStackTrace();
            return "";
        }

        if (containerCreation == null) return "";

        log.info("Created container [chainWorkOrderId:{}, containerId:{}]",
                chainWorkOrderId, containerCreation.id());

        return containerCreation.id() != null ? containerCreation.id() : "";
    }

    public void startContainer(String containerId) throws DockerException, InterruptedException {
        log.debug("Starting container [containerId:{}]", containerId);
        docker.startContainer(containerId);
        log.debug("Started container [containerId:{}]", containerId);
    }

    public void waitContainer(String chainWorkOrderId, String containerId, Date executionTimeoutDate) {
        boolean isComputed = false;
        boolean isTimeout = false;

        if (containerId == null || containerId.isEmpty()) return;

        while (!isComputed && !isTimeout) {
            log.info("Computing [chainWorkOrderId:{}, containerId:{}, status:{}, isComputed:{}, isTimeout:{}]",
                    chainWorkOrderId, containerId, getContainerStatus(containerId), isComputed, isTimeout);

            WaitUtils.sleep(1);
            isComputed = isContainerExited(containerId);
            isTimeout = isAfterTimeout(executionTimeoutDate);
        }

        if (isTimeout) {
            log.warn("Container reached timeout, stopping [chainWorkOrderId:{}, containerId:{}]", chainWorkOrderId, containerId);
        }
    }

    public long stopContainer(String containerId) throws DockerException, InterruptedException {
        log.debug("Stopping container [containerId:{}]", containerId);
        docker.stopContainer(containerId, 0);
        return docker.waitContainer(containerId).statusCode();
    }

    public void removeContainer(String containerId) throws DockerException, InterruptedException {
        log.debug("Removing container [containerId:{}]", containerId);
        docker.removeContainer(containerId);
        log.debug("Removed container [containerId:{}]", containerId);
    }

    public boolean isContainerExited(String containerId) {
        return getContainerStatus(containerId).equals(EXITED);
    }

    private String getContainerStatus(String containerId) {
        try {
            return docker.inspectContainer(containerId).state().status();
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to get container status [containerId:{}]", containerId);
            e.printStackTrace();
            return "";
        }
    }

    private boolean isAfterTimeout(Date executionTimeoutDate) {
        return new Date().after(executionTimeoutDate);
    }

    @PreDestroy
    void onPreDestroy() {
        docker.close();
    }
}
