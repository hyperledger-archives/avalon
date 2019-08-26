package com.iexec.eea.worker.chain.model;

import lombok.*;
import lombok.extern.slf4j.Slf4j;
import org.web3j.tuples.generated.Tuple5;

import java.math.BigInteger;
import java.util.List;

import static com.iexec.eea.worker.utils.BytesUtils.bytesToString;
import static com.iexec.eea.worker.utils.BytesUtils.bytesToStrings;

@Data
@Slf4j
@AllArgsConstructor
@Builder
public class ChainWorker {

    private String workerId;
    private WorkerType type;
    private String workerTypeDataUri;
    private String organizationId;
    private String[] applicationTypeId;
    private String details;
    private WorkerStatus status;

    public static ChainWorker fromTuple(String id, Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String> val) {
        return ChainWorker.builder()
                .workerId(id)
                .status(WorkerStatus.valueOf(val.getValue1().intValue()))
                .type(WorkerType.valueOf(val.getValue2().intValue()))
                .organizationId(bytesToString(val.getValue3()))
                .applicationTypeId(bytesToStrings(val.getValue4()))
                .details(val.getValue5())
                .build();
    }


    @AllArgsConstructor
    @Getter
    public static enum WorkerStatus {
        NULL("NULL"),
        ACTIVE("ACTIVE"),
        OFFLINE("OFFLINE"),
        DECOMMISSIONED("DECOMMISSIONED"),
        COMPROMISED("COMPROMISED");

        @NonNull
        private String name;

        public static WorkerStatus valueOf(int ordinal)
        {
            return WorkerStatus.values()[ordinal];
        }

        public String toString() {
            return name;
        }
    }

    @AllArgsConstructor
    @Getter
    public enum WorkerType {
        NULL("NULL"),
        TEESGX("TEE-SGX"),
        MPC("MPC"),
        ZK("ZK");

        @NonNull
        private String name;

        public static WorkerType valueOf(int ordinal) {
            return WorkerType.values()[ordinal];
        }

        public String toString() {
            return name;
        }
    }
}



