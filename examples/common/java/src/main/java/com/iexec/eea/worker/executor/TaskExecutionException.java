package com.iexec.eea.worker.executor;

import com.iexec.eea.worker.chain.model.ChainWorkOrder;
import lombok.NonNull;

public class TaskExecutionException extends Exception {
    private String workOrderId;

    public TaskExecutionException(@NonNull String workOrderId, String message) {
        this(workOrderId, message, null);
    }

    public TaskExecutionException(@NonNull String workOrderId, Throwable cause) {
        this(workOrderId, null, cause);
    }

    public TaskExecutionException(@NonNull String workOrderId, String message, Throwable cause) {
        super(message, cause);
        this.workOrderId = workOrderId;
    }

    public String toString() {
        return String.format("TaskExecutionException [workOrderId: %s, message: \"%s\"]\nCaused by: %s",
                workOrderId, super.getMessage(), getCause());
    }
}
