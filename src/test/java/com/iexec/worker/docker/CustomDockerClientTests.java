package com.iexec.worker.docker;

import com.iexec.worker.config.WorkerConfigurationService;
import com.spotify.docker.client.DefaultDockerClient;
import com.spotify.docker.client.messages.ContainerConfig;
import com.spotify.docker.client.messages.Device;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.io.File;
import java.util.Arrays;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;


public class CustomDockerClientTests {

    @Mock private DefaultDockerClient docker;
    @Mock private WorkerConfigurationService workerConfigurationService;

    @InjectMocks
    private CustomDockerClient customDockerClient;

    private static final String TEST_WORKER = "./src/test/resources/tmp/test-worker";
    private static final String CHAIN_TASK_ID = "docker";
    private static String DOCKER_TMP_FOLDER = "";
    private static final long SECOND = 1000;
    private static final long MAX_EXECUTION_TIME = 10 * SECOND;

    private static final String IMAGE_URI = "image:tag";
    private static final String CMD = "cmd";
    private static final List<String> ENV = Arrays.asList("FOO=bar");

    private static final String SGX_DEVICE_PATH = "/dev/isgx";
    private static final String SGX_DEVICE_PERMISSIONS = "rwm";

    private static final String ALPINE = "alpine";
    private static final String ALPINE_LATEST = "alpine:latest";
    private static final String ALPINE_BLABLA = "alpine:blabla";
    private static final String BLABLA_LATEST = "blabla:latest";

    @BeforeClass
    public static void beforeClass() {
        DOCKER_TMP_FOLDER = new File(TEST_WORKER + "/" + CHAIN_TASK_ID).getAbsolutePath();
    }

    @Before
    public void beforeEach() {
        MockitoAnnotations.initMocks(this);
    }

    public String getDockerInput() { return DOCKER_TMP_FOLDER + "/input"; }
    public String getDockerOutput() { return DOCKER_TMP_FOLDER + "/output"; }
    public String getDockerIexecOut() { return getDockerOutput() + "/iexec_out"; }
    public String getDockerScone() { return DOCKER_TMP_FOLDER + "/scone"; }

    // buildContainerConfig()

    @Test
    public void shouldBuildContainerConfig() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID))
                .thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID))
                .thenReturn(getDockerIexecOut());

        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                IMAGE_URI, ENV, CMD);

        assertThat(containerConfig.image()).isEqualTo(IMAGE_URI);
        assertThat(containerConfig.cmd().get(0)).isEqualTo(CMD);
        assertThat(containerConfig.env()).isEqualTo(ENV);

        String inputBind = containerConfig.hostConfig().binds().get(0);
        String outputBind = containerConfig.hostConfig().binds().get(1);
        assertThat(inputBind).isEqualTo(getDockerInput() + ":/iexec_in");
        assertThat(outputBind).isEqualTo(getDockerIexecOut() + ":/iexec_out");
    }

    @Test
    public void shouldNotBuildContainerConfigWithoutImage() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID))
                .thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID))
                .thenReturn(getDockerIexecOut());

        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                "", ENV, CMD);

        assertThat(containerConfig).isNull();
    }

    @Test
    public void shouldNotBuildContainerConfigWithoutHostConfig() {
        // this causes hostConfig to be null
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn("");
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn("");

        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                IMAGE_URI, ENV, CMD);

        assertThat(containerConfig).isNull();
    }

    // buildSconeContainerConfig()

    @Test
    public void shouldBuildSconeContainerConfig() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID))
                .thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID))
                .thenReturn(getDockerIexecOut());
        when(workerConfigurationService.getTaskSconeDir(CHAIN_TASK_ID))
                .thenReturn(getDockerScone());

        ContainerConfig containerConfig = customDockerClient.buildSconeContainerConfig(CHAIN_TASK_ID,
                IMAGE_URI, ENV, CMD);

        assertThat(containerConfig.image()).isEqualTo(IMAGE_URI);
        assertThat(containerConfig.cmd().get(0)).isEqualTo(CMD);
        assertThat(containerConfig.env()).isEqualTo(ENV);

        String inputBind = containerConfig.hostConfig().binds().get(0);
        String outputBind = containerConfig.hostConfig().binds().get(1);
        assertThat(inputBind).isEqualTo(getDockerInput() + ":/iexec_in");
        assertThat(outputBind).isEqualTo(getDockerIexecOut() + ":/iexec_out");

        Device sgxDevice = containerConfig.hostConfig().devices().get(0);
        assertThat(sgxDevice.pathOnHost()).isEqualTo(SGX_DEVICE_PATH);
        assertThat(sgxDevice.pathInContainer()).isEqualTo(SGX_DEVICE_PATH);
        assertThat(sgxDevice.cgroupPermissions()).isEqualTo(SGX_DEVICE_PERMISSIONS);
    }

    @Test
    public void shouldNotBuildSconeContainerConfigWithoutImage() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID))
                .thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID))
                .thenReturn(getDockerIexecOut());
        when(workerConfigurationService.getTaskSconeDir(CHAIN_TASK_ID))
                .thenReturn(getDockerScone());

        ContainerConfig containerConfig = customDockerClient.buildSconeContainerConfig(CHAIN_TASK_ID,
                "", ENV, CMD);

        assertThat(containerConfig).isNull();
    }

    @Test
    public void shouldNotBuildSconeContainerConfigWithoutHostConfig() {
        // this causes hostConfig to be null
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn("");
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn("");
        when(workerConfigurationService.getTaskSconeDir(CHAIN_TASK_ID)).thenReturn("");

        ContainerConfig containerConfig = customDockerClient.buildSconeContainerConfig(CHAIN_TASK_ID,
                IMAGE_URI, ENV, CMD);

        assertThat(containerConfig).isNull();
    }

    // pullImage()

    @Test
    public void shouldPullImage() {
        boolean imagePulled = customDockerClient.pullImage(CHAIN_TASK_ID, ALPINE_LATEST);
        assertThat(imagePulled).isTrue();
    }

    @Test
    public void shouldNotPullImageWithWrongName() {
        boolean imagePulled = customDockerClient.pullImage(CHAIN_TASK_ID, BLABLA_LATEST);
        assertThat(imagePulled).isFalse();
    }

    @Test
    public void shouldNotPullImageWithWrongTag() {
        boolean imagePulled = customDockerClient.pullImage(CHAIN_TASK_ID, ALPINE_BLABLA);
        assertThat(imagePulled).isFalse();
    }

    @Test
    public void shouldNotPullImageWithoutImageName() {
        boolean imagePulled = customDockerClient.pullImage(CHAIN_TASK_ID, "");
        assertThat(imagePulled).isFalse();
    }

    // shouldn't we refuse apps without tags ??
    @Ignore
    @Test
    public void shouldPullLatestImageWithoutTag() {
        boolean imagePulled = customDockerClient.pullImage(CHAIN_TASK_ID, ALPINE);
        assertThat(imagePulled).isTrue();
    }

    // isImagePulled()

    @Test
    public void shouldIsImagePulledReturnTrue() {
        boolean pullResult = customDockerClient.pullImage(CHAIN_TASK_ID, ALPINE_LATEST);
        boolean isImagePulled = customDockerClient.isImagePulled(ALPINE_LATEST);
        assertThat(pullResult).isTrue();
        assertThat(isImagePulled).isTrue();
    }

    @Test
    public void shouldIsImagePulledReturnFalse() {
        boolean pullResult = customDockerClient.pullImage(CHAIN_TASK_ID, ALPINE_BLABLA);
        boolean isImagePulled = customDockerClient.isImagePulled(ALPINE_BLABLA);
        assertThat(pullResult).isFalse();
        assertThat(isImagePulled).isFalse();
    }

    // dockerRun()

    @Test
    public void shouldComputeAndGetLogs() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(getDockerIexecOut());
        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                ALPINE_LATEST, ENV, "echo", "Hello from Docker alpine!");

        String stdout = customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, MAX_EXECUTION_TIME);

        assertThat(stdout).contains("Hello from Docker alpine!");
    }

    @Test
    public void shouldStopComputingIfTooLong() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(getDockerIexecOut());
        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                ALPINE_LATEST, ENV, "sh", "-c", "sleep 30 && echo Hello from Docker alpine!");

        String stdout = customDockerClient.dockerRun(CHAIN_TASK_ID, containerConfig, MAX_EXECUTION_TIME);

        assertThat(stdout).isEmpty();
    }

    // createContainer()

    @Test
    public void shouldNotCreateContainerWithNullConfig() {
        String containerId = customDockerClient.createContainer(CHAIN_TASK_ID, null);
        assertThat(containerId).isEmpty();
    }

    // startContainer()

    @Test
    public void shouldNotStartContainerWithEmptyId() {
        boolean isStarted = customDockerClient.startContainer("");
        assertThat(isStarted).isFalse();
    }

    @Test
    public void shouldNotStartContainerWithBadId() {
        boolean isStarted = customDockerClient.startContainer("blabla");
        assertThat(isStarted).isFalse();
    }

    // stopContainer()

    @Test
    public void shouldNotStopContainerWithEmptyId() {
        boolean isStopped = customDockerClient.stopContainer("");
        assertThat(isStopped).isFalse();
    }

    @Test
    public void shouldNotStopContainerWithBadId() {
        boolean isStopped = customDockerClient.stopContainer("blabla");
        assertThat(isStopped).isFalse();
    }

    @Test
    public void shouldStopAlreadyStoppedContainer() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(getDockerIexecOut());
        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                ALPINE_LATEST, ENV, "sh", "-c", "sleep 30 && echo Hello from Docker alpine!");

        String containerId = customDockerClient.createContainer(CHAIN_TASK_ID, containerConfig);
        boolean isStopped = customDockerClient.stopContainer(containerId);
        assertThat(isStopped).isTrue();
        customDockerClient.removeContainer(containerId);
    }

    // getContainerLogs()

    @Test
    public void shouldNotGetLogsOfContainerWithEmptyId() {
        String dockerLogs = customDockerClient.getContainerLogs("");
        assertThat(dockerLogs).isEqualTo("Failed to get computation logs");
    }

    @Test
    public void shouldNotGetLogsOfContainerWithBadId() {
        String dockerLogs = customDockerClient.getContainerLogs(CHAIN_TASK_ID);
        assertThat(dockerLogs).isEqualTo("Failed to get computation logs");
    }

    // removeContainer()

    @Test
    public void shouldNotRemoveRunningContainer() {
        when(workerConfigurationService.getTaskInputDir(CHAIN_TASK_ID)).thenReturn(getDockerInput());
        when(workerConfigurationService.getTaskIexecOutDir(CHAIN_TASK_ID)).thenReturn(getDockerIexecOut());
        ContainerConfig containerConfig = customDockerClient.buildContainerConfig(CHAIN_TASK_ID,
                ALPINE_LATEST, ENV, "sh", "-c", "sleep 30 && echo Hello from Docker alpine!");

        String containerId = customDockerClient.createContainer(CHAIN_TASK_ID, containerConfig);
        boolean isStarted = customDockerClient.startContainer(containerId);
        boolean isRemoved = customDockerClient.removeContainer(containerId);

        assertThat(isStarted).isTrue();
        assertThat(isRemoved).isFalse();

        customDockerClient.stopContainer(containerId);
        boolean isRemovedAfterStopped = customDockerClient.removeContainer(containerId);
        assertThat(isRemovedAfterStopped).isTrue();
    }

    @Test
    public void shouldNotRemoveContainerWithEmptyId() {
        boolean isRemoved = customDockerClient.removeContainer("");
        assertThat(isRemoved).isFalse();
    }

    @Test
    public void shouldNotRemoveContainerWithBadId() {
        boolean isRemoved = customDockerClient.removeContainer("blabla");
        assertThat(isRemoved).isFalse();
    }
}
