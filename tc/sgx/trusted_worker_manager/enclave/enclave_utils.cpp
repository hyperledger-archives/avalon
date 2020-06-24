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

#include "enclave_common_t.h"

#include <stdarg.h>
#include <stdio.h>
#include<mbusafecrt.h>

#include "enclave_utils.h"
#include "error.h"
#include "tcf_error.h"
#include "c11_support.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void printf(const char* fmt, ...) {
    char buf[BUFSIZ] = {'\0'};
    va_list ap;
    va_start(ap, fmt);
    vsnprintf_s(buf, BUFSIZ, fmt, ap);
    va_end(ap);
    ocall_Print(buf);
}  // printf

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void Log(int level, const char* fmt, ...) {
    char buf[BUFSIZ] = {'\0'};
    va_list ap;
    va_start(ap, fmt);
    vsnprintf_s(buf, BUFSIZ, fmt, ap);
    va_end(ap);
#ifdef TCF_DEBUG_BUILD
    ocall_Log(level, buf);
#endif
}  // Log

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
uint64_t GetTimer(void) {
    uint64_t value = 0;
#ifdef TCF_DEBUG_BUILD
    ocall_GetTimer(&value);
#endif

    return value;
}  // GetTimer
