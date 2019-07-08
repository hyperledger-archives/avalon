package com.iexec.worker.result;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResultInfo {

    private String image;
    private String tag;
    private String cmd;
    private String deterministHash;
    private String datasetUri;

}
