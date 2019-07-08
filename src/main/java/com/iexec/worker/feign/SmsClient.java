package com.iexec.worker.feign;

import com.iexec.common.sms.SmsRequest;
import com.iexec.common.sms.scone.SconeSecureSessionResponse;
import com.iexec.common.sms.secrets.SmsSecretResponse;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import feign.FeignException;


@FeignClient(
    name = "SmsClient",
    url = "#{publicConfigurationService.smsURL}"
)
public interface SmsClient {

    @PostMapping("/secure")
    SmsSecretResponse getTaskSecretsFromSms(@RequestBody SmsRequest smsRequest) throws FeignException;

    @PostMapping("/secure")
    SconeSecureSessionResponse generateSecureSession(@RequestBody SmsRequest smsRequest) throws FeignException;
}