package com.iexec.worker.chain;

import com.iexec.common.chain.Web3jAbstractService;
import com.iexec.worker.config.PublicConfigurationService;
import com.iexec.worker.config.WorkerConfigurationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class Web3jService extends Web3jAbstractService {

    public Web3jService(PublicConfigurationService publicConfService,
                        WorkerConfigurationService workerConfService) {
        super(!workerConfService.getOverrideBlockchainNodeAddress().isEmpty() ?
                        workerConfService.getOverrideBlockchainNodeAddress() :
                        publicConfService.getDefaultBlockchainNodeAddress(),
                workerConfService.getGasPriceMultiplier(), workerConfService.getGasPriceCap());
    }

}