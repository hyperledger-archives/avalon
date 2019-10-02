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
package org.eea.tcf.worker.chain.services;

import org.eea.tcf.worker.chain.events.WorkOrderSubmittedEvent;
import org.eea.tcf.worker.chain.model.ChainWorkOrder;
import org.eea.tcf.worker.executor.TaskExecutionService;
import io.reactivex.Flowable;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigInteger;
import java.util.Optional;

@Service
@Slf4j
public class ComputationService {

    private Web3jService web3jService;
    private WorkOrderRegistryService workOrderRegistryService;
    private TaskExecutionService taskExecutionService;

    @Autowired
    public ComputationService(Web3jService web3jService,
                              WorkOrderRegistryService workOrderRegistryService,
                              TaskExecutionService taskExecutionService) {
        this.web3jService = web3jService;
        this.workOrderRegistryService = workOrderRegistryService;
        this.taskExecutionService = taskExecutionService;
    }

    public void start() {
        BigInteger latestBlockNumber =
                BigInteger.valueOf(web3jService.getLatestBlockNumber());

        Flowable<WorkOrderSubmittedEvent> eventSource =
                workOrderRegistryService.getWorkOrderEventObservable(latestBlockNumber, null);

        eventSource.subscribe((event) -> {
            Optional <ChainWorkOrder> optionalChainWorkOrder =
                    workOrderRegistryService.workOrderGet(event.getWorkOrderId());
            if(optionalChainWorkOrder.isEmpty()) {
                log.error("Cannot get workOrder [workOrderId:{}]",event.getWorkOrderId());
                return;
            }

            ChainWorkOrder workOrder = optionalChainWorkOrder.get();

            log.info("Received WorkOrderSubmitted event [workOrderId:{}, status:{}]",
                    workOrder.getWorkOrderId(),
                    workOrder.getStatus());

            if(workOrder.getStatus() == ChainWorkOrder.WorkOrderStatus.ACTIVE) {
                taskExecutionService.scheduleForExecution(workOrder)
                        .thenAccept((retStatus) -> {
                            String response = taskExecutionService.getWorkOrderResult(workOrder);
                            // enclaveSig.tcf contains a JSON document that includes the signature:
                            String signature = taskExecutionService.getWorkOrderResultSignature(workOrder);
                            ChainWorkOrder.WorkOrderResult result = workOrder.parseResult(signature);


                            workOrderRegistryService.workOrderComplete(
                                    workOrder.getWorkOrderId(),
                                    retStatus,
                                    response,
                                    result.getSignature()
                            );

                            // TODO we should probably cleanup the response and
                            //  signature file now that we’re done
                        });
            }
        });
    }
}
