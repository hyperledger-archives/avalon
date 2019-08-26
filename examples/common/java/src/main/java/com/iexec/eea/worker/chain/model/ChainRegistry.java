package com.iexec.eea.worker.chain.model;

import lombok.*;
import lombok.extern.slf4j.Slf4j;
import org.web3j.tuples.generated.Tuple4;

import java.math.BigInteger;
import java.util.List;

import static com.iexec.eea.worker.utils.BytesUtils.bytesToString;
import static com.iexec.eea.worker.utils.BytesUtils.bytesToStrings;

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

    public static ChainRegistry fromTuple(Tuple4<String, byte[], List<byte[]>, BigInteger> val) {
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
