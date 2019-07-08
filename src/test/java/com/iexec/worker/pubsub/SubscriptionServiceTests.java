package com.iexec.worker.pubsub;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.notification.TaskNotification;
import com.iexec.common.notification.TaskNotificationExtra;
import com.iexec.common.notification.TaskNotificationType;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.executor.TaskExecutorService;
import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;

import java.util.Collections;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

public class SubscriptionServiceTests {

    @Mock
    private WorkerConfigurationService workerConfigurationService;
    @Mock
    private TaskExecutorService taskExecutorService;

    @InjectMocks
    SubscriptionService subscriptionService;

    private static final String WORKER_WALLET_ADDRESS = "0x1234";
    private static final String CHAIN_TASK_ID = "chaintaskid";

    private TaskNotification notifTemplate = TaskNotification.builder()
            .workersAddress(Collections.singletonList(WORKER_WALLET_ADDRESS))
            .taskNotificationExtra(TaskNotificationExtra.builder()
                    .build())
            .chainTaskId(CHAIN_TASK_ID)
            .build();

    @Before
    public void init() {
        MockitoAnnotations.initMocks(this);

        when(workerConfigurationService.getWorkerWalletAddress()).thenReturn(WORKER_WALLET_ADDRESS);


    }


    @Test
    public void shouldNotHandleNotificationSinceWorkerWalletNotInNotif() {

        TaskNotification notif = TaskNotification.builder()
                .workersAddress(Collections.singletonList("0xabcd"))
                .chainTaskId(CHAIN_TASK_ID)
                .build();

        subscriptionService.handleTaskNotification(notif);

        Mockito.verifyZeroInteractions(taskExecutorService);
    }

    @Test
    public void shouldNotContributeSinceNoContributionAuthorization() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_CONTRIBUTE);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verifyZeroInteractions(taskExecutorService);
    }

    @Test
    public void shouldTryToContribute() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_CONTRIBUTE);
        notifTemplate.setTaskNotificationExtra(TaskNotificationExtra.builder()
                        .contributionAuthorization(new ContributionAuthorization())
                        .build());

        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).computeOrContribute(any());
    }

    @Test
    public void shouldAbortOnContributionTimeout() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_ABORT_CONTRIBUTION_TIMEOUT);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).abortContributionTimeout(CHAIN_TASK_ID);
    }

    @Test
    public void shouldAbortOnConsensusReached() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_ABORT_CONSENSUS_REACHED);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).abortConsensusReached(CHAIN_TASK_ID);
    }

    @Test
    public void shouldReveal() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_REVEAL);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).reveal(eq(CHAIN_TASK_ID), anyLong());
    }

    @Test
    public void shouldUpload() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_UPLOAD);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).uploadResult(CHAIN_TASK_ID);
    }

    @Test
    public void shouldComplete() {
        notifTemplate.setTaskNotificationType(TaskNotificationType.PLEASE_COMPLETE);
        subscriptionService.handleTaskNotification(notifTemplate);

        Mockito.verify(taskExecutorService, Mockito.times(1)).completeTask(CHAIN_TASK_ID);
    }
}
