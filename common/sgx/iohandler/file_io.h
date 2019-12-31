/* Copyright 2019 Intel Corporation
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

#include <string>
#include <stdint.h>

class FileIoExecutor {
private:
    uint32_t handler_id;
    std::string file_name;

public:
    FileIoExecutor() {}

    void SetIoHandlerId(uint32_t handler_id) {
        this->handler_id = handler_id;
    }

    void SetFileName(std::string file_name) {
        this->file_name = file_name;
    }

    uint32_t GetIoHandlerId(const char* handlerName);

    size_t GetMaxFileSize();

    size_t GetMaxIoResultSize();

    uint32_t FileOpen(uint8_t *result, size_t result_size);

    uint32_t FileClose(uint8_t *result, size_t result_size);

    uint32_t FileRead(uint8_t *result, size_t result_size, uint8_t *out_buf,
        size_t out_buf_size);

    uint32_t FileWrite(uint8_t *result, size_t result_size,
        const uint8_t *in_buf, size_t in_buf_size);

    uint32_t FileTell(uint8_t *result, size_t result_size, uint8_t *out_buf,
        size_t out_buf_size);

    uint32_t FileSeek(size_t position, uint8_t *result, size_t result_size);
};
