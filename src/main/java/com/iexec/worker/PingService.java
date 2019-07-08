package com.iexec.worker;

import com.iexec.worker.config.CoreConfigurationService;
import com.iexec.worker.feign.CustomFeignClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class PingService {

    private CustomFeignClient feignClient;
    private CoreConfigurationService coreConfigurationService;
    private RestartService restartService;

    public PingService(CustomFeignClient feignClient,
                       CoreConfigurationService coreConfigurationService,
                       RestartService restartService) {
        this.feignClient = feignClient;
        this.coreConfigurationService = coreConfigurationService;
        this.restartService = restartService;
    }

    @Scheduled(fixedRate = 10000)
    public void pingScheduler() {
        log.debug("Send ping to scheduler");
        String sessionId = feignClient.ping();
        String currentSessionId = coreConfigurationService.getCoreSessionId();
        if (currentSessionId == null || currentSessionId.isEmpty()){
            log.info("First ping from the worker, setting the sessionId [coreSessionId:{}]", sessionId);
            coreConfigurationService.setCoreSessionId(sessionId);
            return;
        }

        if(sessionId != null && sessionId.equals("")){
            log.warn("The worker cannot ping the core!");
            return;
        }

        if (sessionId != null && !sessionId.equalsIgnoreCase(currentSessionId)){
            // need to reconnect to the core by restarting the worker
            log.warn("Scheduler seems to have restarted [currentSessionId:{}, coreSessionId:{}]", currentSessionId, sessionId);
            log.warn("The worker will restart now!");
            restartService.restartApp();
        }
    }
}
