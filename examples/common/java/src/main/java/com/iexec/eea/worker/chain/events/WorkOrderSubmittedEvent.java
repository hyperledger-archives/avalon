package com.iexec.eea.worker.chain.events;

import lombok.*;

import java.math.BigInteger;

@Data
@Getter
@AllArgsConstructor
@Builder
public class WorkOrderSubmittedEvent {

    private String workOrderId;
    private String workerId;
    private String requesterId;

}

