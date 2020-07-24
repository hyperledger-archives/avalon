/* Copyright 2020 Intel Corporation
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
*/
#pragma once

#include "ssd_od.h"

class ProcessWorkOrder {
private:
    std::string in_image_dir;
    std::string out_image_dir;
    std::string process_work_order_ov();
    SSDObjectDetection ssd;
public:
    ProcessWorkOrder(const std::string in_image_dir, 
                     const std::string out_image_dir);
    int load_model(const std::string &modelFile);
    std::string process_work_order(std::string &msg);
};

