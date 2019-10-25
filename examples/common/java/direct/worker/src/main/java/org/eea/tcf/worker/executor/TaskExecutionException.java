  /*****************************************************************************
  * Copyright 2019 iExec Blockchain Tech
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  *     http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *****************************************************************************/
package org.eea.tcf.worker.executor;

import lombok.NonNull;

public class TaskExecutionException extends Exception {
    private String workOrderId;

    public TaskExecutionException(@NonNull String workOrderId, String message) {
        this(workOrderId, message, null);
    }

    public TaskExecutionException(@NonNull String workOrderId, Throwable cause) {
        this(workOrderId, null, cause);
    }

    public TaskExecutionException(@NonNull String workOrderId, String message,
                                  Throwable cause) {
        super(message, cause);
        this.workOrderId = workOrderId;
    }

    public String toString() {
        return String.format("TaskExecutionException [workOrderId: %s, message: \"%s\"]\nCaused by: %s",
                workOrderId, super.getMessage(), getCause());
    }
}
