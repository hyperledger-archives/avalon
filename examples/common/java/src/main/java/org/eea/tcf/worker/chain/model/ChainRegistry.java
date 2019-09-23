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
import org.web3j.tuples.generated.Tuple4;

import java.math.BigInteger;
import java.util.List;

import static org.eea.tcf.worker.utils.BytesUtils.bytesToString;
import static org.eea.tcf.worker.utils.BytesUtils.bytesToStrings;

@Data
@Slf4j
@AllArgsConstructor
@Builder
public class ChainRegistry {

    @NonNull
    private String organizationId;

    @NonNull
    private String uri;

    @NonNull
    private String address;

    private String[] applicationTypeId;

    @NonNull
    private RegistryStatus status;

    public static ChainRegistry fromTuple(Tuple4<String, byte[], List<byte[]>,
            BigInteger> val) {
        return ChainRegistry.builder()
                .uri(val.getValue1())
                .address(bytesToString(val.getValue2()))
                .applicationTypeId(bytesToStrings(val.getValue3()))
                .status(RegistryStatus.valueOf(val.getValue4().intValue()))
                .build();
    }

    @AllArgsConstructor
    @Getter
    @ToString
    public enum RegistryStatus {
        NULL("NULL"),
        ACTIVE("ACTIVE"),
        OFFLINE("OFF-LINE"),
        DECOMMISSIONED("DECOMMISSIONED");

        @NonNull
        private String name;

        public static RegistryStatus valueOf(int ordinal) {
            return RegistryStatus.values()[ordinal];
        }
    }
}
