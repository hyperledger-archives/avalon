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
package org.eea.tcf.worker;


import org.eea.tcf.worker.chain.model.ChainWorker;
import org.eea.tcf.worker.chain.services.ComputationService;
import org.eea.tcf.worker.chain.services.CredentialsService;
import org.eea.tcf.worker.chain.services.WorkOrderRegistryService;
import org.eea.tcf.worker.chain.services.WorkerRegistryService;
import org.eea.tcf.worker.config.WorkerConfigurationModel;
import lombok.extern.slf4j.Slf4j;
import org.eea.tcf.worker.config.WorkerConfigurationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.web3j.crypto.Credentials;

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

        if (workerConfig.getHttpProxyHost() != null &&
                workerConfig.getHttpProxyPort() != null) {
            log.info("Running with proxy [proxyHost:{}, proxyPort:{}]",
                    workerConfig.getHttpProxyHost(),
                    workerConfig.getHttpProxyPort());
        }

        
        // Register the worker
        Optional<ChainWorker> chainWorker =
                workerRegistryService.workerRetrieve(workerAddress);
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
                        workerConfig.getWorkerWalletAddress(),
                        model.getWorkerRegistryAddress());
                System.exit(2);
            }
        }

        // Start waiting for events
        computationService.start();
        log.info("Worker running and waiting for work");
    }
}
