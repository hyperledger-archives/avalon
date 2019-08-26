package com.iexec.eea.worker.chain.services;

import com.iexec.eea.worker.chain.events.WorkOrderSubmittedEvent;
import com.iexec.eea.worker.chain.model.ChainWorkOrder;
import com.iexec.eea.worker.executor.TaskExecutionService;
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
        BigInteger latestBlockNumber = BigInteger.valueOf(web3jService.getLatestBlockNumber());

        Flowable<WorkOrderSubmittedEvent> eventSource =
                workOrderRegistryService.getWorkOrderEventObservable(latestBlockNumber, null);

        eventSource.subscribe((event) -> {
            Optional <ChainWorkOrder> optionalChainWorkOrder = workOrderRegistryService.workOrderGet(event.getWorkOrderId());
            if(optionalChainWorkOrder.isEmpty()) {
                log.error("Cannot get workOrder [workOrderId:{}]", event.getWorkOrderId());
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
                            //String signature = taskExecutionService.getWorkOrderResultSignature(workOrder);
                            String signature = "{\"result\": \"You have a risk of 71% to have heart disease.\", \"resultHash\": \"8839208909fb43bb4fe8a10b28685ede79a05789cd10c73e57d7ae602005d869\", \"resultSalt\": \"77c4ceaa30d08a57b4b86403d32c025cde5a6f119bcba6412c15432eefc13d59\", \"signature\":  \"bfcbe2e1c61f5ab13f7044565b82ceef25a842e2c7eca8e50bc5e8604623b360\"}";
                            ChainWorkOrder.WorkOrderResult result = workOrder.parseResult(signature);


                            workOrderRegistryService.workOrderComplete(
                                    workOrder.getWorkOrderId(),
                                    retStatus,
                                    response,
                                    result.getSignature()
                            );

                            // TODO we should probably cleanup the response and signature file now that we’re done
                        });
            }
        });
    }
}
