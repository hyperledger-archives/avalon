package com.iexec.worker.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.net.MalformedURLException;
import java.net.URL;

@Service
public class CoreConfigurationService {

    @Value("${core.host}")
    private String coreHost;

    @Value("${core.port}")
    private String corePort;

    private URL url;

    private String coreSessionId;

    @PostConstruct
    public void run() throws MalformedURLException {
        url = new URL("http://" + coreHost + ":" + corePort);
        getUrl();
    }

    public String getUrl() {
        return getProtocol() + "://" +
                getHost() + ":" +
                getPort();
    }

    public String getProtocol() {
        return url.getProtocol();
    }

    public String getHost() {
        return url.getHost();
    }

    public int getPort() {
        return url.getPort();
    }

    public String getCoreSessionId() {
        return coreSessionId;
    }

    public void setCoreSessionId(String coreSessionId) {
        this.coreSessionId = coreSessionId;
    }
}
