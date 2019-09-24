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
package org.eea.tcf.worker.chain.model;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eea.tcf.worker.utils.FileHelper;
import lombok.*;
import lombok.extern.slf4j.Slf4j;
import org.web3j.tuples.generated.Tuple7;

import java.io.IOException;
import java.math.BigInteger;
import java.net.MalformedURLException;
import java.net.URL;

import static org.eea.tcf.worker.utils.BytesUtils.bytesToString;

/**
 * !! requesterId and senderAddress can be different
 */
@Data
@Slf4j
@Builder
public class ChainWorkOrder {

    private WorkOrderStatus status;
    private String workerId;
    private String workOrderId;
    private String requesterId;
    private String verifierAddress;
    private int returnCode;
    private String response;

    private String request;
    private WorkOrderParams params;

    private WorkOrderResult result;

    public static ChainWorkOrder fromTuple(String id, Tuple7<BigInteger, byte[],
            byte[], String, String, BigInteger, String> val) {
        return ChainWorkOrder.builder()
                .workOrderId(id)
                .status(WorkOrderStatus.valueOf(val.getValue1().intValue()))
                .workerId(bytesToString(val.getValue2()))
                .requesterId(bytesToString(val.getValue3()))
                .request(val.getValue4())
                .verifierAddress(val.getValue5())
                .returnCode(val.getValue6().intValue())
                .response(val.getValue7())
                .build();
    }

    public WorkOrderParams getParams() {
        if(params == null)
            parseParams();

        return params;
    }

    private void parseParams() {
        String jsonString = request;

        try {
            URL jsonUrl = new URL(request);
            jsonString = FileHelper.downloadFileInString(jsonUrl);
        } catch (MalformedURLException ignored) {}

        if(jsonString == null) {
            log.error("Could not download WorkOrderParams file [workOrderId:{}, url:{}]",
                    workOrderId, request);
            return;
        }

        try {
            params = new ObjectMapper().readValue(jsonString,
                    WorkOrderParams.class);
           } catch (IOException e) {
            log.error("Could not parse WorkOrderParams JSON [workOrderId:{}, exception:{}]",
                    workOrderId, e.getMessage());
        }
    }

    public WorkOrderResult parseResult(@NonNull String json) {
        try {
            result = new ObjectMapper().readValue(json, WorkOrderResult.class);
        } catch (IOException e) {
            log.error("Could not parse WorkOrderResult JSON [workOrderId:{}, exception:{}]",
                    workOrderId, e.getMessage());
        }

        return result;
    }

    public WorkOrderResult getResult() {
        return result;
    }

    @AllArgsConstructor
    @Getter
    public static enum WorkOrderStatus {
        NULL("NULL"),
        ACTIVE("ACTIVE"),
        COMPLETED("COMPLETED");

        @NonNull
        private String name;

        public static WorkOrderStatus valueOf(int ordinal) {
            return WorkOrderStatus.values()[ordinal];
        }

        public String toString() {
            return name;
        }
    }

    @Data
    @Builder
    @AllArgsConstructor
    @NoArgsConstructor
    public static class WorkOrderParams {
        private String appUri;
        private String cmd;
        private String[] args;
        private String inputFiles; // URLs
        private long maxExecutionTime;
    }

    @Data
    @Builder
    @AllArgsConstructor
    @NoArgsConstructor
    public static class WorkOrderResult {
        private String result;
        private String resultHash;
        private String resultSalt;
        private String signature;
    }
}



