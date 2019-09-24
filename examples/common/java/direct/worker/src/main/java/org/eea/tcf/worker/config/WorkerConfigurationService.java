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
package org.eea.tcf.worker.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eea.tcf.worker.chain.services.CredentialsService;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

@Service
@Slf4j
public class WorkerConfigurationService {

    public static final String OUT_DIR = "eea_out";

    private CredentialsService credentialsService;

    @Value("${worker.name}")
    private String workerName;

    @Value("${worker.organizationId}")
    @Getter
    private String organizationId;

    @Value("${worker.applicationTypeIds}")
    @Getter
    private String[] applicationTypeIds;

    @Value("${worker.registryContractAddress}")
    @Getter
    private String registryAddress;

    @Value("${worker.workOrderContractAddress}")
    @Getter
    private String workOrderRegistryAddress;

    @Value("${worker.detailsFilePath}")
    private String detailsFilePath;

    @Getter
    private WorkerDetails workerDetails;

    @Value("${worker.workerBaseDir}")
    private String workerBaseDir;

    @Value("${worker.gasPriceMultiplier}")
    private float gasPriceMultiplier;

    @Value("${worker.gasPriceCap}")
    private long gasPriceCap;

    @Value("${worker.blockchainNodeAddress}")
    @Getter
    private String blockchainNodeAddress;

    /**
     * TODO this is useless for now
     */
    @Value("${worker.registryListContractAddress}")
    @Getter
    private String registryListAddress;

    public WorkerConfigurationService(CredentialsService credentialsService) {
        this.credentialsService = credentialsService;
    }

    public String getWorkerName() {
        return workerName;
    }

    public String getWorkerWalletAddress() {
        return credentialsService.getCredentials().getAddress();
    }

    public String getWorkerBaseDir() {
        return workerBaseDir + File.separator + workerName;
    }

    public String getTaskBaseDir(String workOrderId) {
        return getWorkerBaseDir() + File.separatorChar + workOrderId;
    }

    public String getTaskOutputDir(String workOrderId) {
        return getTaskBaseDir(workOrderId) + File.separatorChar + OUT_DIR;
    }

    public float getGasPriceMultiplier() {
        return gasPriceMultiplier;
    }

    public long getGasPriceCap() {
        return gasPriceCap;
    }

    public String getHttpProxyHost() {
        return System.getProperty("http.proxyHost");
    }

    public Integer getHttpProxyPort() {
        String proxyPort = System.getProperty("http.proxyPort");
        return proxyPort != null && !proxyPort.isEmpty() ? Integer.valueOf(proxyPort) : null;
    }

    public String getHttpsProxyHost() {
        return System.getProperty("https.proxyHost");
    }

    public Integer getHttpsProxyPort() {
        String proxyPort = System.getProperty("https.proxyPort");
        return proxyPort != null && !proxyPort.isEmpty() ? Integer.valueOf(proxyPort) : null;
    }

    public String getDetails() {
        File detailsFile = new File(detailsFilePath);

        if(!detailsFile.exists() || !detailsFile.canRead()) {
            log.error("Details file does not exist or cannot be read: " +
                    detailsFilePath);
            System.exit(20);
        }

        String content = null;
        try {
            content = Files.readString(detailsFile.toPath());
        } catch (IOException e) {
            log.error("Cannot read details file [path:{}, exception:{}",
                    detailsFilePath, e.getMessage());
            System.exit(21);
        }

        return content;
    }

    @PostConstruct
    private void loadJson() {
        ObjectMapper mapper = new ObjectMapper();
        String jsonString = getDetails();

        if(jsonString == null || jsonString.isEmpty()) {
            log.error("WorkerDetails cannot be empty [workName:{}]",
                    workerName);
            return;
        }

        try {
            workerDetails = new ObjectMapper().readValue(new File(detailsFilePath), WorkerConfigurationService.WorkerDetails.class);
        } catch (IOException e) {
            log.error("Could not parse WorkerDetails JSON [workerName:{}, exception:{}]",
                    workerName, e.getMessage());
        }
    }

    @Data
    @AllArgsConstructor
    @Builder
    public static class WorkerDetails {
        private String fromAddress;
        private String hashingAlgorithm;
        private String signingAlgorithm;
        private String keyEncryptionAlgorithm;
        private String encryptionPublicKey;
        private String dataEncryptionAlgorithm;
        private String workOrderPayloadFormats;
        private String workerTypeData;
    }
}
