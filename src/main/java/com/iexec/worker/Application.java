package com.iexec.worker;


import com.iexec.common.config.PublicConfiguration;
import com.iexec.common.config.WorkerConfigurationModel;
import com.iexec.worker.amnesia.AmnesiaRecoveryService;
import com.iexec.worker.chain.CredentialsService;
import com.iexec.worker.chain.IexecHubService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.feign.CustomFeignClient;
import com.iexec.worker.result.ResultService;
import com.iexec.worker.utils.LoggingUtils;
import com.iexec.worker.utils.version.VersionService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

import java.util.List;


@SpringBootApplication
@EnableFeignClients
@EnableScheduling
@EnableRetry
@EnableAsync
@Slf4j
public class Application implements CommandLineRunner {

    @Value("${core.host}")
    private String coreHost;

    @Value("${core.port}")
    private String corePort;

    @Autowired
    private WorkerConfigurationService workerConfig;

    @Autowired
    private CredentialsService credentialsService;

    @Autowired
    private CustomFeignClient customFeignClient;

    @Autowired
    private IexecHubService iexecHubService;

    @Autowired
    private ResultService resultService;

    @Autowired
    private AmnesiaRecoveryService amnesiaRecoveryService;

    @Autowired
    private VersionService versionService;

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Override
    public void run(String... args) {
        String workerAddress = credentialsService.getCredentials().getAddress();
        WorkerConfigurationModel model = WorkerConfigurationModel.builder()
                .name(workerConfig.getWorkerName())
                .walletAddress(workerAddress)
                .os(workerConfig.getOS())
                .cpu(workerConfig.getCPU())
                .cpuNb(workerConfig.getNbCPU())
                .memorySize(workerConfig.getMemorySize())
                .teeEnabled(workerConfig.isTeeEnabled())
                .build();

        log.info("Number of tasks that can run in parallel on this machine [tasks:{}]", workerConfig.getNbCPU() / 2);
        log.info("Address of the core [address:{}]", "http://" + coreHost + ":" + corePort);
        log.info("Version of the core [version:{}]", customFeignClient.getCoreVersion());
        PublicConfiguration publicConfiguration = customFeignClient.getPublicConfiguration();
        log.info("Get configuration of the core [config:{}]", publicConfiguration);
        if (workerConfig.getHttpProxyHost() != null && workerConfig.getHttpProxyPort() != null) {
            log.info("Running with proxy [proxyHost:{}, proxyPort:{}]", workerConfig.getHttpProxyHost(), workerConfig.getHttpProxyPort());
        }

        if (!publicConfiguration.getRequiredWorkerVersion().isEmpty() &&
                !versionService.getVersion().equals(publicConfiguration.getRequiredWorkerVersion())) {

            String badVersion = String.format("Bad version! please upgrade your iexec-worker [current:%s, required:%s]",
                    versionService.getVersion(), publicConfiguration.getRequiredWorkerVersion());

            LoggingUtils.printHighlightedMessage(badVersion);
            System.exit(0);
        }

        if (!iexecHubService.hasEnoughGas()) {
            String noEnoughGas = String.format("No enough gas! please refill your wallet [walletAddress:%s]", workerAddress);
            LoggingUtils.printHighlightedMessage(noEnoughGas);
            System.exit(0);
        }

        customFeignClient.registerWorker(model);
        log.info("Registered the worker to the core [worker:{}]", model);

        log.info("Cool, your iexec-worker is all set!");

        // ask core for interrupted replicates
        List<String> recoveredTasks = amnesiaRecoveryService.recoverInterruptedReplicates();

        // clean the results folder
        resultService.cleanUnusedResultFolders(recoveredTasks);
    }
}
