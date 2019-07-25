package com.iexec.eea.worker;


import com.iexec.eea.worker.chain.model.ChainWorkOrder;
import com.iexec.eea.worker.chain.model.ChainWorker;
import com.iexec.eea.worker.chain.services.ComputationService;
import com.iexec.eea.worker.chain.services.CredentialsService;
import com.iexec.eea.worker.chain.services.WorkOrderRegistryService;
import com.iexec.eea.worker.chain.services.WorkerRegistryService;
import com.iexec.eea.worker.config.WorkerConfigurationModel;
import lombok.extern.slf4j.Slf4j;
import com.iexec.eea.worker.config.WorkerConfigurationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.web3j.crypto.Credentials;

import javax.swing.text.html.Option;
import java.util.Optional;


@SpringBootApplication
@EnableFeignClients
@EnableScheduling
@EnableRetry
@EnableAsync
@Slf4j
public class Application implements CommandLineRunner {

    @Autowired
    private WorkerConfigurationService workerConfig;

    @Autowired
    private CredentialsService credentialsService;

    @Autowired
    private WorkerRegistryService workerRegistryService;

    @Autowired
    private ComputationService computationService;

    @Autowired
    private WorkOrderRegistryService workOrderRegistryService;

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Override
    public void run(String... args) {
        Credentials credentials = credentialsService.getCredentials();
        String workerAddress = credentials.getAddress();
        WorkerConfigurationModel model = WorkerConfigurationModel.builder()
                .name(workerConfig.getWorkerName())
                .organizationId(workerConfig.getOrganizationId())
                .workerRegistryAddress(workerConfig.getRegistryAddress())
                .applicationTypeIds(workerConfig.getApplicationTypeIds())
                .walletAddress(workerAddress)
                .blockChainNodeAddress(workerConfig.getBlockchainNodeAddress())
                .build();

        if (workerConfig.getHttpProxyHost() != null && workerConfig.getHttpProxyPort() != null) {
            log.info("Running with proxy [proxyHost:{}, proxyPort:{}]", workerConfig.getHttpProxyHost(), workerConfig.getHttpProxyPort());
        }

        
        // Register the worker
        Optional<ChainWorker> chainWorker = workerRegistryService.workerRetrieve(workerAddress);
        if(chainWorker.isPresent()) {
            log.info("Worker already registered [worker:{}]", model);
        }
        else {
            if(!workerRegistryService.workerRegister(
                    workerAddress,
                    ChainWorker.WorkerType.TEESGX,
                    workerConfig.getOrganizationId(),
                    workerConfig.getApplicationTypeIds(),
                    workerConfig.getDetails())) {
                log.error("Could not register worker [workerId:{}, registryAddress:{}]",
                        workerConfig.getWorkerWalletAddress(), model.getWorkerRegistryAddress());
                System.exit(2);
            }
        }

        // Start waiting for events
        computationService.start();
        log.info("Worker running and waiting for work");
    }
}
