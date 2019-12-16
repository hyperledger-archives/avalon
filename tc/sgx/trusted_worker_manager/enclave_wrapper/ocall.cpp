/* Copyright 2018 Intel Corporation
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

#include <stdint.h>
#include <stdio.h>
#include <iostream>
#include <chrono>

#include "log.h"
#include "timer.h"

std::string g_enclaveError;

extern "C" {

    void ocall_Print(
        const char *str) {
        /* Proxy/Bridge will check the length and null-terminate
        * the input string to prevent buffer overflow.
        */
        std::cout << str;
    }  // ocall_Print

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void ocall_Log(
        int level,
        const char *str) {
        tcf::Log((tcf_log_level_t)level, str);
    }  // ocall_Log

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void ocall_GetTimer(uint64_t* value) {
        (*value) = tcf::GetTimer();
    }

    void ocall_SetErrorMessage(
        const char* message) {
        if (message) {
            g_enclaveError.assign(message);
        } else {
            g_enclaveError.clear();
        }
    }  // ocall_SetErrorMessage

}  // extern "C"
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

