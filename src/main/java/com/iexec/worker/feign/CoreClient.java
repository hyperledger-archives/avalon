package com.iexec.worker.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

import feign.FeignException;

@FeignClient(
    name = "CoreClient",
    url = "http://${core.host}:${core.port}"
)
public interface CoreClient {

    @GetMapping("/version")
    String getCoreVersion() throws FeignException;
}