package com.iexec.worker.chain;

import org.junit.Test;
import org.web3j.crypto.CipherException;

import java.io.FileNotFoundException;
import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;

public class CredentialsServiceTests {

    @Test
    public void shouldLoadCorrectAddress() throws IOException, CipherException {
        WalletDetails walletDetails = new WalletDetails("./src/main/resources/wallet/encrypted-wallet_worker1.json", "whatever");
        CredentialsService service = new CredentialsService(walletDetails);

        // adress of wallet1
        assertThat(service.getCredentials().getAddress()).isEqualTo("0x1a69b2eb604db8eba185df03ea4f5288dcbbd248");
    }

    @Test(expected = FileNotFoundException.class)
    public void shouldThrowFileNotFoundException() throws IOException, CipherException {
        WalletDetails walletDetails = new WalletDetails("./dummy/path.json", "whatever");
        new CredentialsService(walletDetails);
    }

    @Test(expected = CipherException.class)
    public void shouldThrowCipherException() throws IOException, CipherException {
        WalletDetails walletDetails = new WalletDetails("./src/main/resources/wallet/encrypted-wallet_worker1.json", "wrongPassword");
        new CredentialsService(walletDetails);
    }
}
