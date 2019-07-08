package com.iexec.worker.utils.version;

import com.iexec.common.utils.VersionUtils;
import org.springframework.stereotype.Service;

@Service
public class VersionService {

    private String version = Version.PROJECT_VERSION;

    public String getVersion() {
        return version;
    }

    public boolean isSnapshot() {
        return VersionUtils.isSnapshot(version);
    }

}
