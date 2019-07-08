package com.iexec.worker.tee.scone;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SconeConfig {

    String sconeCasAddress;
    String sconeLasAddress;
    String sconeConfigId;

    @Builder.Default String sconeHeap = "1G";
    @Builder.Default int sconeLog = 7;
    @Builder.Default int sconeVersion = 1;

    public SconeConfig(String sconeCasAddress, String sconeLasAddress, String sconeConfigId) {
        this.sconeCasAddress = sconeCasAddress;
        this.sconeLasAddress = sconeLasAddress;
        this.sconeConfigId = sconeConfigId;
        this.sconeHeap = "1G";
        this.sconeLog = 7;
        this.sconeVersion = 1;
    }

    public ArrayList<String> toDockerEnv() {
        List<String> list = Arrays.asList(
            "SCONE_CAS_ADDR="   + sconeCasAddress,
            "SCONE_LAS_ADDR="   + sconeLasAddress,
            "SCONE_CONFIG_ID="  + sconeConfigId,
            "SCONE_HEAP="       + sconeHeap,
            "SCONE_LOG="        + sconeLog,
            "SCONE_VERSION="    + sconeVersion
        );

        return new ArrayList<String>(list);
    }
}