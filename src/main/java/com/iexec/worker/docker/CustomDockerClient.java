package com.iexec.worker.docker;

import com.iexec.common.utils.WaitUtils;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.utils.FileHelper;
import com.spotify.docker.client.DefaultDockerClient;
import com.spotify.docker.client.DockerClient.LogsParam;
import com.spotify.docker.client.exceptions.DockerCertificateException;
import com.spotify.docker.client.exceptions.DockerException;
import com.spotify.docker.client.messages.ContainerConfig;
import com.spotify.docker.client.messages.ContainerCreation;
import com.spotify.docker.client.messages.Device;
import com.spotify.docker.client.messages.HostConfig;
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

    public ContainerConfig buildContainerConfig(String chainTaskId, String imageUri, List<String> env, String... cmd) {
        if (imageUri == null || imageUri.isEmpty()) return null;

        HostConfig hostConfig = getHostConfig(chainTaskId);
        if (hostConfig == null) return null;

        return buildCommonContainerConfig(hostConfig, imageUri, env, cmd);
    }

    public ContainerConfig buildSconeContainerConfig(String chainTaskId, String imageUri, List<String> env, String... cmd) {
        if (imageUri == null || imageUri.isEmpty()) return null;

        HostConfig hostConfig = getSconeHostConfig(chainTaskId);
        if (hostConfig == null) return null;

        return buildCommonContainerConfig(hostConfig, imageUri, env, cmd);
    }

    private ContainerConfig buildCommonContainerConfig(HostConfig hostConfig, String imageUri, List<String> env, String... cmd) {
        ContainerConfig.Builder containerConfigBuilder = ContainerConfig.builder();

        if (cmd != null && cmd.length != 0) containerConfigBuilder.cmd(cmd);

        return containerConfigBuilder.image(imageUri)
                .hostConfig(hostConfig)
                .env(env)
                .build();
    }

    private HostConfig getHostConfig(String chainTaskId) {
        HostConfig.Bind inputBind = createInputBind(chainTaskId);
        HostConfig.Bind outputBind = createOutputBind(chainTaskId);

        if (inputBind == null || outputBind == null) return null;

        return HostConfig.builder()
                .appendBinds(inputBind, outputBind)
                .build();
    }

    private HostConfig getSconeHostConfig(String chainTaskId) {
        HostConfig.Bind inputBind = createInputBind(chainTaskId);
        HostConfig.Bind outputBind = createOutputBind(chainTaskId);
        HostConfig.Bind sconeBind = createSconeBind(chainTaskId);

        if (inputBind == null || outputBind == null || sconeBind == null) return null;

        Device device = Device.builder()
                .pathOnHost("/dev/isgx")
                .pathInContainer("/dev/isgx")
                .cgroupPermissions("rwm")
                .build();

        return HostConfig.builder()
                .appendBinds(inputBind, outputBind, sconeBind)
                .devices(device)
                .build();
    }

    private HostConfig.Bind createInputBind(String chainTaskId) {
        String inputMountPoint = workerConfigurationService.getTaskInputDir(chainTaskId);
        return createBind(inputMountPoint, FileHelper.SLASH_IEXEC_IN);
    }

    private HostConfig.Bind createOutputBind(String chainTaskId) {
        String outputMountPoint = workerConfigurationService.getTaskIexecOutDir(chainTaskId);
        return createBind(outputMountPoint, FileHelper.SLASH_IEXEC_OUT);
    }

    private HostConfig.Bind createSconeBind(String chainTaskId) {
        String sconeMountPoint = workerConfigurationService.getTaskSconeDir(chainTaskId);
        return createBind(sconeMountPoint, FileHelper.SLASH_SCONE);
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

    public boolean pullImage(String chainTaskId, String image) {
        log.info("Image pull started [chainTaskId:{}, image:{}]", chainTaskId, image);

        try {
            docker.pull(image);
        } catch (DockerException | InterruptedException e) {
            log.error("Image pull failed [chainTaskId:{}, image:{}]", chainTaskId, image);
            e.printStackTrace();
            return false;
        }

        log.info("Image pull completed [chainTaskId:{}, image:{}]", chainTaskId, image);
        return true;
    }

    public boolean isImagePulled(String image) {
        try {
            return !docker.inspectImage(image).id().isEmpty();
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to check if image was pulled [image:{}]", image);
            e.printStackTrace();
            return false;
        }
    }

    /**
     * This creates a container, starts, waits then stops it, and returns its logs
     */
    public String dockerRun(String chainTaskId, ContainerConfig containerConfig, long maxExecutionTime) {
        if (containerConfig == null) {
            log.error("Could not run computation, container config is null [chainTaskId:{}]", chainTaskId);
            return "";
        }

        log.info("Running computation [chainTaskId:{}, image:{}, cmd:{}]",
                chainTaskId, containerConfig.image(), containerConfig.cmd());

        // docker create
        String containerId = createContainer(chainTaskId, containerConfig);
        if (containerId.isEmpty()) return "";

        // docker start
        boolean isContainerStarted = startContainer(containerId);

        if (!isContainerStarted) return "";

        Date executionTimeoutDate = Date.from(Instant.now().plusMillis(maxExecutionTime));
        waitContainer(chainTaskId, containerId, executionTimeoutDate);

        // docker stop
        stopContainer(containerId);

        log.info("Computation completed [chainTaskId:{}]", chainTaskId);

        // docker logs
        String stdout = getContainerLogs(containerId);

        // docker rm
        removeContainer(containerId);
        return stdout;
    }

    public String createContainer(String chainTaskId, ContainerConfig containerConfig) {
        log.debug("Creating container [chainTaskId:{}]", chainTaskId);

        if (containerConfig == null) return "";

        ContainerCreation containerCreation;

        try {
            containerCreation = docker.createContainer(containerConfig);
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to create container [chainTaskId:{}, image:{}, cmd:{}]",
                    chainTaskId, containerConfig.image(), containerConfig.cmd());
            e.printStackTrace();
            return "";
        }

        if (containerCreation == null) return "";

        log.info("Created container [chainTaskId:{}, containerId:{}]",
                chainTaskId, containerCreation.id());

        return containerCreation.id() != null ? containerCreation.id() : "";
    }

    public boolean startContainer(String containerId) {
        log.debug("Starting container [containerId:{}]", containerId);

        try {
            docker.startContainer(containerId);
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to start container [containerId:{}]", containerId);
            e.printStackTrace();
            removeContainer(containerId);
            return false;
        }

        log.debug("Started container [containerId:{}]", containerId);
        return true;
    }

    public void waitContainer(String chainTaskId, String containerId, Date executionTimeoutDate) {
        boolean isComputed = false;
        boolean isTimeout = false;

        if (containerId == null || containerId.isEmpty()) return;

        while (!isComputed && !isTimeout) {
            log.info("Computing [chainTaskId:{}, containerId:{}, status:{}, isComputed:{}, isTimeout:{}]",
                    chainTaskId, containerId, getContainerStatus(containerId), isComputed, isTimeout);

            WaitUtils.sleep(1);
            isComputed = isContainerExited(containerId);
            isTimeout = isAfterTimeout(executionTimeoutDate);
        }

        if (isTimeout) {
            log.warn("Container reached timeout, stopping [chainTaskId:{}, containerId:{}]", chainTaskId, containerId);
        }
    }

    public boolean stopContainer(String containerId) {
        log.debug("Stopping container [containerId:{}]", containerId);

        try {
            docker.stopContainer(containerId, 0);
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to stop container [containerId:{}]", containerId);
            e.printStackTrace();
            return false;
        }

        log.debug("Stopped container [containerId:{}]", containerId);
        return true;
    }

    public String getContainerLogs(String containerId) {
        log.debug("Getting container logs [containerId:{}]", containerId);
        String stdout = "";

        try {
            stdout = docker.logs(containerId, LogsParam.stdout(), LogsParam.stderr()).readFully();
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to get container logs [containerId:{}]", containerId);
            e.printStackTrace();
            return "Failed to get computation logs";
        }

        log.debug("Got container logs [containerId:{}]", containerId);
        return stdout;
    }

    public boolean removeContainer(String containerId) {
        log.debug("Removing container [containerId:{}]", containerId);
        try {
            docker.removeContainer(containerId);
        } catch (DockerException | InterruptedException e) {
            log.error("Failed to remove container [containerId:{}]", containerId);
            e.printStackTrace();
            return false;
        }

        log.debug("Removed container [containerId:{}]", containerId);
        return true;
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
