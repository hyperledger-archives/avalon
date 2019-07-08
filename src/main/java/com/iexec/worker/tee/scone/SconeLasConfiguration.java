package com.iexec.worker.tee.scone;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * LAS: local attestation service.
 * Local service used to perform SGX specific operations to attest the enclave
 * (eg compute enclave measurement - MREnclave - and attest it through Intel
 * Attestation Service).
 * It must be on the same machine as the attested program/enclave.
 * 
 * MREnclave: an enclave identifier, created by hashing all its
 * code. It guarantees that a code behaves exactly as expected.
 */
@Component
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class SconeLasConfiguration {

    @Value("${scone.las.host}")
    private String host;

    @Value("${scone.las.port}")
    private String port;

    public String getURL() {
        return host + ":" + port;
    }
}