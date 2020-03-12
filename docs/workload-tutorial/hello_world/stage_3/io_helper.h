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

#include <string>

class IoHelper {
public:
    IoHelper(std::string file_name);

    std::string GenerateKey();
    void SetKey(std::string hex_key);
    uint32_t WriteFile(std::string data);
    uint32_t ReadFile(std::string& read_data);
    uint32_t DeleteFile();

    std::string file_name;
    std::string hex_key;
};  // class IoHelper
