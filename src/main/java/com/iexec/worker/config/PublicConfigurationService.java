package com.iexec.worker.config;

import com.iexec.common.config.PublicConfiguration;
import com.iexec.worker.feign.CustomFeignClient;
import org.springframework.stereotype.Service;

@Service
public class PublicConfigurationService {

    private PublicConfiguration publicConfiguration;

    public PublicConfigurationService(CustomFeignClient customFeignClient) {
        this.publicConfiguration = customFeignClient.getPublicConfiguration();
    }

    public Integer getChainId() {
        return publicConfiguration.getChainId();
    }

    public String getDefaultBlockchainNodeAddress() {
        return publicConfiguration.getBlockchainURL();
    }

    public String getIexecHubAddress() {
        return publicConfiguration.getIexecHubAddress();
    }

    public String getWorkerPoolAddress() {
        return publicConfiguration.getWorkerPoolAddress();
    }

    public String getSchedulerPublicAddress() {
        return publicConfiguration.getSchedulerPublicAddress();
    }

    public long getAskForReplicatePeriod() {
        return publicConfiguration.getAskForReplicatePeriod();
    }

    public String getResultRepositoryURL() {
        return publicConfiguration.getResultRepositoryURL();
    }

    public String getSmsURL() {
        return publicConfiguration.getSmsURL();
    }

    public String getSconeCasURL() {
        return publicConfiguration.getSconeCasURL();
    }
}
