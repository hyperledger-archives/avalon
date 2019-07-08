package com.iexec.worker.pubsub;

import com.iexec.common.chain.ContributionAuthorization;
import com.iexec.common.notification.TaskNotification;
import com.iexec.common.notification.TaskNotificationType;
import com.iexec.worker.config.CoreConfigurationService;
import com.iexec.worker.config.WorkerConfigurationService;
import com.iexec.worker.executor.TaskExecutorService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.Nullable;
import org.springframework.messaging.converter.MappingJackson2MessageConverter;
import org.springframework.messaging.simp.SimpMessageType;
import org.springframework.messaging.simp.stomp.*;
import org.springframework.scheduling.concurrent.ConcurrentTaskScheduler;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.socket.client.WebSocketClient;
import org.springframework.web.socket.client.standard.StandardWebSocketClient;
import org.springframework.web.socket.messaging.WebSocketStompClient;
import org.springframework.web.socket.sockjs.client.RestTemplateXhrTransport;
import org.springframework.web.socket.sockjs.client.SockJsClient;
import org.springframework.web.socket.sockjs.client.Transport;
import org.springframework.web.socket.sockjs.client.WebSocketTransport;

import javax.annotation.PostConstruct;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;


@Slf4j
@Service
public class SubscriptionService extends StompSessionHandlerAdapter {

    private RestTemplate restTemplate;
    // external services
    private TaskExecutorService taskExecutorService;
    private CoreConfigurationService coreConfigurationService;
    private WorkerConfigurationService workerConfigurationService;

    // internal components
    private StompSession session;
    private Map<String, StompSession.Subscription> chainTaskIdToSubscription;
    private WebSocketStompClient stompClient;
    private String url;

    public SubscriptionService(CoreConfigurationService coreConfigurationService,
                               WorkerConfigurationService workerConfigurationService,
                               TaskExecutorService taskExecutorService,
                               RestTemplate restTemplate) {
        this.taskExecutorService = taskExecutorService;
        this.restTemplate = restTemplate;
        this.coreConfigurationService = coreConfigurationService;
        this.workerConfigurationService = workerConfigurationService;
        chainTaskIdToSubscription = new ConcurrentHashMap<>();

    }

    @PostConstruct
    void init() {
        String coreHost = coreConfigurationService.getHost();
        int corePort = coreConfigurationService.getPort();
        this.url = "http://" + coreHost + ":" + corePort + "/connect";

        this.restartStomp();
    }

    void restartStomp() {
        log.info("Starting STOMP");
        if (isConnectEndpointUp()) {
            WebSocketClient webSocketClient = new StandardWebSocketClient();
            List<Transport> webSocketTransports = Arrays.asList(new WebSocketTransport(webSocketClient),
                    new RestTemplateXhrTransport(restTemplate));
            SockJsClient sockJsClient = new SockJsClient(webSocketTransports);
            this.stompClient = new WebSocketStompClient(sockJsClient);//without SockJS: new WebSocketStompClient(webSocketClient);
            this.stompClient.setAutoStartup(true);
            this.stompClient.setMessageConverter(new MappingJackson2MessageConverter());
            this.stompClient.setTaskScheduler(new ConcurrentTaskScheduler());
            this.stompClient.connect(url, this);
            log.info("Started STOMP");
        }
    }

    private boolean isConnectEndpointUp() {
        ResponseEntity<String> checkConnectionEntity = restTemplate.getForEntity(url, String.class);
        if (checkConnectionEntity.getStatusCode().is2xxSuccessful()) {
            return true;
        }
        log.error("isConnectEndpointUp failed (will retry) [url:{}, status:{}]", url, checkConnectionEntity.getStatusCode());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return isConnectEndpointUp();
    }

    private void reSubscribeToTopics() {
        List<String> chainTaskIds = new ArrayList<>(chainTaskIdToSubscription.keySet());
        log.info("ReSubscribing to topics [chainTaskIds: {}]", chainTaskIds.toString());
        for (String chainTaskId : chainTaskIds) {
            chainTaskIdToSubscription.remove(chainTaskId);
            subscribeToTopic(chainTaskId);
        }
        log.info("ReSubscribed to topics [chainTaskIds: {}]", chainTaskIds.toString());
    }

    @Override
    public void afterConnected(StompSession session, StompHeaders connectedHeaders) {
        log.info("SubscriptionService set up [session: {}, isConnected: {}]", session.getSessionId(), session.isConnected());
        this.session = session;
        this.reSubscribeToTopics();
    }

    @Override
    public void handleException(StompSession session, @Nullable StompCommand command,
                                StompHeaders headers, byte[] payload, Throwable exception) {
        SimpMessageType messageType = null;
        if (command != null) {
            messageType = command.getMessageType();
        }
        log.error("Received handleException [session: {}, isConnected: {}, command: {}, exception: {}]",
                session.getSessionId(), session.isConnected(), messageType, exception.getMessage());
        exception.printStackTrace();
        this.restartStomp();
    }

    @Override
    public void handleTransportError(StompSession session, Throwable exception) {
        log.info("Received handleTransportError [session: {}, isConnected: {}, exception: {}]",
                session.getSessionId(), session.isConnected(), exception.getMessage());
        exception.printStackTrace();
        this.restartStomp();
    }

    public void subscribeToTopic(String chainTaskId) {
        if (!chainTaskIdToSubscription.containsKey(chainTaskId)) {
            StompSession.Subscription subscription = session.subscribe(getTaskTopicName(chainTaskId), new StompFrameHandler() {
                @Override
                public Type getPayloadType(StompHeaders headers) {
                    return TaskNotification.class;
                }

                @Override
                public void handleFrame(StompHeaders headers, @Nullable Object payload) {
                    if (payload != null) {
                        TaskNotification taskNotification = (TaskNotification) payload;
                        handleTaskNotification(taskNotification);
                    } else {
                        log.info("Payload of TaskNotification is null [chainTaskId:{}]", chainTaskId);
                    }
                }
            });
            chainTaskIdToSubscription.put(chainTaskId, subscription);
            log.info("Subscribed to topic [chainTaskId:{}, topic:{}]", chainTaskId, getTaskTopicName(chainTaskId));
        } else {
            log.info("Already subscribed to topic [chainTaskId:{}, topic:{}]", chainTaskId, getTaskTopicName(chainTaskId));
        }
    }

    public void unsubscribeFromTopic(String chainTaskId) {
        if (chainTaskIdToSubscription.containsKey(chainTaskId)) {
            chainTaskIdToSubscription.get(chainTaskId).unsubscribe();
            chainTaskIdToSubscription.remove(chainTaskId);
            log.info("Unsubscribed from topic [chainTaskId:{}]", chainTaskId);
        } else {
            log.info("Already unsubscribed from topic [chainTaskId:{}]", chainTaskId);
        }
    }

    public void handleTaskNotification(TaskNotification notif) {
        if (notif.getWorkersAddress().contains(workerConfigurationService.getWorkerWalletAddress())
                || notif.getWorkersAddress().isEmpty()) {
            log.info("Received notification [notification:{}]", notif);

            TaskNotificationType type = notif.getTaskNotificationType();
            String chainTaskId = notif.getChainTaskId();

            switch (type) {
                case PLEASE_CONTRIBUTE:
                    ContributionAuthorization contribAuth = notif.getTaskNotificationExtra().getContributionAuthorization();
                    if (contribAuth != null){
                        taskExecutorService.computeOrContribute(contribAuth);
                    } else {
                        log.error("Empty contribAuth for PLEASE_CONTRIBUTE [chainTaskId:{}]", chainTaskId);
                    }
                    break;
                case PLEASE_ABORT_CONTRIBUTION_TIMEOUT:
                    unsubscribeFromTopic(chainTaskId);
                    taskExecutorService.abortContributionTimeout(chainTaskId);
                    break;
                case PLEASE_ABORT_CONSENSUS_REACHED:
                    unsubscribeFromTopic(chainTaskId);
                    taskExecutorService.abortConsensusReached(chainTaskId);
                    break;

                case PLEASE_REVEAL:
                    taskExecutorService.reveal(chainTaskId, notif.getTaskNotificationExtra().getBlockNumber());
                    break;

                case PLEASE_UPLOAD:
                    taskExecutorService.uploadResult(chainTaskId);
                    break;

                case PLEASE_COMPLETE:
                    unsubscribeFromTopic(chainTaskId);
                    taskExecutorService.completeTask(chainTaskId);
                    break;

                default:
                    break;
            }
        }
    }




    private String getTaskTopicName(String chainTaskId) {
        return "/topic/task/" + chainTaskId;
    }
}