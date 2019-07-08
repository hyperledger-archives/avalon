package com.iexec.worker.chain;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.web3j.crypto.CipherException;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;

import java.io.IOException;

@Slf4j
@Service
public class CredentialsService {

    private Credentials credentials;

    public CredentialsService(WalletDetails walletDetails) throws IOException, CipherException {
        try {
            credentials = WalletUtils.loadCredentials(walletDetails.getPassword(), walletDetails.getPath());
            log.info("Load wallet credentials [address:{}] ", credentials.getAddress());
        } catch (IOException | CipherException e) {
            log.error("Credentials cannot be loaded [exception:{}] ", e);
            throw e;
        }
    }

    public Credentials getCredentials() {
        return credentials;
    }
}