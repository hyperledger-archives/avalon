package com.iexec.worker.config;

import com.iexec.worker.chain.CredentialsService;
import com.iexec.worker.utils.FileHelper;

import org.apache.http.HttpHost;
import org.apache.http.impl.client.HttpClientBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.File;

import static java.lang.management.ManagementFactory.getOperatingSystemMXBean;

@Service
public class WorkerConfigurationService {

    private CredentialsService credentialsService;

    @Value("${worker.name}")
    private String workerName;

    @Value("${worker.workerBaseDir}")
    private String workerBaseDir;

    @Value("${worker.gasPriceMultiplier}")
    private float gasPriceMultiplier;

    @Value("${worker.gasPriceCap}")
    private long gasPriceCap;

    @Value("${worker.teeEnabled}")
    private boolean isTeeEnabled;

    @Value("${worker.overrideBlockchainNodeAddress}")
    private String overrideBlockchainNodeAddress;

    public WorkerConfigurationService(CredentialsService credentialsService) {
        this.credentialsService = credentialsService;
    }

    public String getWorkerName() {
        return workerName;
    }

    public String getWorkerWalletAddress() {
        return credentialsService.getCredentials().getAddress();
    }

    public String getWorkerBaseDir() {
        return workerBaseDir + File.separator + workerName;
    }

    public String getTaskBaseDir(String chainTaskId) {
        return getWorkerBaseDir() + File.separator + chainTaskId;
    }

    public String getTaskInputDir(String chainTaskId) {
        return getWorkerBaseDir() + File.separator + chainTaskId + FileHelper.SLASH_INPUT;
    }

    public String getTaskOutputDir(String chainTaskId) {
        return getWorkerBaseDir() + File.separator + chainTaskId + FileHelper.SLASH_OUTPUT;
    }

    public String getTaskIexecOutDir(String chainTaskId) {
        return getWorkerBaseDir() + File.separator + chainTaskId + FileHelper.SLASH_OUTPUT
                + FileHelper.SLASH_IEXEC_OUT;
    }

    public String getTaskSconeDir(String chainTaskId) {
        return getWorkerBaseDir() + File.separator + chainTaskId + FileHelper.SLASH_SCONE;
    }

    public String getOS() {
        return System.getProperty("os.name").trim();
    }

    public String getCPU() {
        return System.getProperty("os.arch");
    }

    public int getNbCPU() {
        return Runtime.getRuntime().availableProcessors();
    }

    public int getMemorySize() {
        com.sun.management.OperatingSystemMXBean os = (com.sun.management.OperatingSystemMXBean) getOperatingSystemMXBean();
        return new Long(os.getTotalPhysicalMemorySize() / (1024 * 1024 * 1024)).intValue();//in GB
    }

    public float getGasPriceMultiplier() {
        return gasPriceMultiplier;
    }

    public long getGasPriceCap() {
        return gasPriceCap;
    }

    public boolean isTeeEnabled() {
        return isTeeEnabled;
    }

    public String getOverrideBlockchainNodeAddress() {
        return overrideBlockchainNodeAddress;
    }

    public String getHttpProxyHost() {
        return System.getProperty("http.proxyHost");
    }

    public Integer getHttpProxyPort() {
        String proxyPort = System.getProperty("http.proxyPort");
        return proxyPort != null && !proxyPort.isEmpty() ? Integer.valueOf(proxyPort) : null;
    }

    @Bean
    private RestTemplate restTemplate() {
        HttpClientBuilder clientBuilder = HttpClientBuilder.create();
        if (getHttpProxyHost() != null && getHttpProxyPort() != null) {
            HttpHost myProxy = new HttpHost(getHttpProxyHost(), getHttpProxyPort());
            clientBuilder.setProxy(myProxy);
        }
        HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
        factory.setHttpClient(clientBuilder.build());
        return new RestTemplate(factory);
    }
}
