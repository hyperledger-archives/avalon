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
package org.eea.tcf.worker.chain.model;

import lombok.*;
import lombok.extern.slf4j.Slf4j;
import org.web3j.tuples.generated.Tuple5;

import java.math.BigInteger;
import java.util.List;

import static org.eea.tcf.worker.utils.BytesUtils.bytesToString;
import static org.eea.tcf.worker.utils.BytesUtils.bytesToStrings;

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

    public static ChainWorker fromTuple(String id, Tuple5<BigInteger,
            BigInteger, byte[], List<byte[]>, String> val) {
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



