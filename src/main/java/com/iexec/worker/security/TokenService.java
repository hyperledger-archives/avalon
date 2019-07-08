package com.iexec.worker.security;

import com.iexec.common.security.Signature;
import com.iexec.common.utils.SignatureUtils;
import com.iexec.worker.chain.CredentialsService;
import com.iexec.worker.feign.WorkerClient;
import feign.FeignException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.web3j.crypto.ECKeyPair;

@Slf4j
@Service
public class TokenService {

    private static final String TOKEN_PREFIX = "Bearer ";
    private static final long RETRY_TIME = 5000;
    private final CredentialsService credentialsService;
    private final WorkerClient workerClient;
    private String currentToken;

    public TokenService(CredentialsService credentialsService,
                        WorkerClient workerClient) {
        this.credentialsService = credentialsService;
        this.workerClient = workerClient;
        expireToken();
    }

    public void expireToken() {
        currentToken = "";
    }

    public String getToken() {
        if (currentToken.isEmpty()) {
            String workerAddress = credentialsService.getCredentials().getAddress();
            ECKeyPair ecKeyPair = credentialsService.getCredentials().getEcKeyPair();
            String challenge = getChallenge(workerAddress);
            if (challenge.isEmpty()) {
                log.error("Challenge should not be empty [challenge:{}]", challenge);
            }

            Signature signature = SignatureUtils.hashAndSign(challenge, workerAddress, ecKeyPair);
            String token = getAccessToken(workerAddress, signature);
            if (!token.isEmpty()) {
                currentToken = TOKEN_PREFIX + token;
            } else {
                log.error("Access token should not be empty [token:{}]", token);
            }
        }
        return currentToken;
    }

    private String getChallenge(String workerAddress) {
        try {
            return workerClient.getChallenge(workerAddress);
        } catch (FeignException e) {
            log.error("Failed to getChallenge (will retry) [status:{}]", e.status());
            sleep();
            return getChallenge(workerAddress);
        }
    }

    private String getAccessToken(String workerAddress, Signature signature) {
        try {
            return workerClient.getAccessToken(workerAddress, signature);
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                expireToken();
            } else {
                log.error("Failed to getAccessToken (will retry) [status:{}]", e.status());
            }
            sleep();
            return getAccessToken(workerAddress, signature);
        }
    }

    private void sleep() {
        try {
            Thread.sleep(RETRY_TIME);
        } catch (InterruptedException e) {
        }
    }

}