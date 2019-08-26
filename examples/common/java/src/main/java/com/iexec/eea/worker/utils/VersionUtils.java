package com.iexec.common.utils;

public class VersionUtils {

    private VersionUtils() {
        throw new UnsupportedOperationException();
    }

    public static boolean isSnapshot(String version) {
        return version.contains("SNAPSHOT");
    }

}
