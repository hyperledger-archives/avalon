package com.iexec.worker.result;

import com.iexec.common.result.ResultModel;
import com.iexec.common.result.eip712.Eip712Challenge;
import com.iexec.worker.config.PublicConfigurationService;
import com.iexec.worker.feign.ResultRepoClient;
import feign.FeignException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;

import java.util.Optional;


@Slf4j
@Service
public class ResultRepoService {

    private ResultRepoClient resultRepoClient;
    private PublicConfigurationService publicConfigurationService;

    public ResultRepoService(ResultRepoClient resultRepoClient,
                             PublicConfigurationService publicConfigurationService) {
        this.resultRepoClient = resultRepoClient;
        this.publicConfigurationService = publicConfigurationService;
    }

    @Retryable(value = FeignException.class)
    public Optional<Eip712Challenge> getChallenge() {
        return Optional.of(resultRepoClient.getChallenge(publicConfigurationService.getChainId()));
    }

    @Recover
    public Optional<Eip712Challenge> getResultRepoChallenge(FeignException e, Integer chainId) {
        log.error("Failed to getResultRepoChallenge [attempts:3]");
        e.printStackTrace();
        return Optional.empty();
    }

    @Retryable(value = FeignException.class,
            maxAttempts = 5,
            backoff = @Backoff(delay = 3000))
    public String uploadResult(String authorizationToken, ResultModel resultModel) {
        ResponseEntity<String> responseEntity =
                resultRepoClient.uploadResult(authorizationToken, resultModel);

        return responseEntity.getStatusCode().is2xxSuccessful()
                ? responseEntity.getBody()
                : "";
    }

    @Recover
    public String uploadResult(FeignException e, String authorizationToken, ResultModel resultModel) {
        log.error("Failed to upload result [attempts:5]");
        e.printStackTrace();
        return "";
    }
}