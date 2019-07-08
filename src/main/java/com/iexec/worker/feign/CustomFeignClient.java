package com.iexec.worker.feign;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.config.PublicConfiguration;
import com.iexec.common.config.WorkerConfigurationModel;
import com.iexec.common.notification.TaskNotification;
import com.iexec.common.replicate.ReplicateDetails;
import com.iexec.common.replicate.ReplicateStatus;
import com.iexec.worker.config.CoreConfigurationService;
import com.iexec.worker.security.TokenService;
import feign.FeignException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;


@Service
@Slf4j
public class CustomFeignClient {

    private static final int RETRY_TIME = 5000;
    private final String coreURL;
    private TokenService tokenService;
    private CoreClient coreClient;
    private WorkerClient workerClient;
    private ReplicateClient replicateClient;

    public CustomFeignClient(CoreClient coreClient,
                             WorkerClient workerClient,
                             ReplicateClient replicateClient,
                             CoreConfigurationService coreConfigurationService,
                             TokenService tokenService) {
        this.coreClient = coreClient;
        this.workerClient = workerClient;
        this.replicateClient = replicateClient;
        this.coreURL = coreConfigurationService.getUrl();
        this.tokenService = tokenService;
    }

    //TODO: Make a generic method for REST API calls (Unauthorized, Retry, ..)
    public String ping() {
        try {
            return workerClient.ping(tokenService.getToken());
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to ping (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return ping();
        }
    }

    public PublicConfiguration getPublicConfiguration() {
        try {
            return workerClient.getPublicConfiguration();
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to getPublicConfiguration (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return getPublicConfiguration();
        }
    }

    public String getCoreVersion() {
        try {
            return coreClient.getCoreVersion();
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to getCoreVersion (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return getCoreVersion();
        }
    }

    //TODO: Make registerWorker return Worker
    public void registerWorker(WorkerConfigurationModel model) {
        try {
            workerClient.registerWorker(tokenService.getToken(), model);
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to registerWorker (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            registerWorker(model);
        }
    }

    public List<TaskNotification> getMissedTaskNotifications(long lastAvailableBlockNumber) {
        try {
            return replicateClient.getMissedTaskNotifications(lastAvailableBlockNumber, tokenService.getToken());
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to getMissedTaskNotifications (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return getMissedTaskNotifications(lastAvailableBlockNumber);
        }
    }

    public List<String> getTasksInProgress() {
        try {
            return workerClient.getCurrentTasks(tokenService.getToken());
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to getTasksInProgress (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return getTasksInProgress();
        }
    }

    public Optional<ContributionAuthorization> getAvailableReplicate(long lastAvailableBlockNumber) {
        try {
            ContributionAuthorization contributionAuth = replicateClient.getAvailableReplicate(lastAvailableBlockNumber, tokenService.getToken());
            return contributionAuth == null ? Optional.empty() : Optional.of(contributionAuth);
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to getAvailableReplicate (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            return getAvailableReplicate(lastAvailableBlockNumber);
        }
    }

    public void updateReplicateStatus(String chainTaskId, ReplicateStatus status) {
        updateReplicateStatus(chainTaskId, status, ReplicateDetails.builder().build());
    }

    public void updateReplicateStatus(String chainTaskId, ReplicateStatus status, ReplicateDetails details) {
        try {
            replicateClient.updateReplicateStatus(chainTaskId, status, tokenService.getToken(), details);
            log.info(status.toString() + " [chainTaskId:{}]", chainTaskId);
        } catch (FeignException e) {
            if (HttpStatus.valueOf(e.status()).equals(HttpStatus.UNAUTHORIZED)) {
                tokenService.expireToken();
            } else {
                log.error("Failed to updateReplicateStatus (will retry) [instance:{}, status:{}]", coreURL, e.status());
            }
            sleep();
            updateReplicateStatus(chainTaskId, status, details);
        }
    }

    private void sleep() {
        try {
            Thread.sleep(RETRY_TIME);
        } catch (InterruptedException e) {
        }
    }

}
