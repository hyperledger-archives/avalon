package com.iexec.eea.worker.utils;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class WaitUtils {

    private WaitUtils() {
        throw new UnsupportedOperationException();
    }

    public static void sleep(int seconds) {
        try {
            Thread.sleep(seconds * 1000);
        } catch (InterruptedException e) {
            log.error("Interrupted [duration:{}]", seconds);
        }
    }

}
