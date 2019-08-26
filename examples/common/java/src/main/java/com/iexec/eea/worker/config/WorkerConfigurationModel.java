package com.iexec.eea.worker.config;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkerConfigurationModel {

    private String blockChainNodeAddress;

    private String workerRegistryAddress;

    private String name;
    private String walletAddress;
    private String organizationId;
    private String[] applicationTypeIds;
}
