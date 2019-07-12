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

#pragma once

#include <stdlib.h>

typedef enum {
    TCF_SUCCESS = 0,
    TCF_ERR_UNKNOWN = -1,
    TCF_ERR_MEMORY = -2,
    TCF_ERR_IO = -3,
    TCF_ERR_RUNTIME = -4,
    TCF_ERR_INDEX = -5,
    TCF_ERR_DIVIDE_BY_ZERO = -6,
    TCF_ERR_OVERFLOW = -7,
    TCF_ERR_VALUE = -8,
    TCF_ERR_SYSTEM = -9,
    TCF_ERR_CRYPTO = -11,
    TCF_ERR_SYSTEM_BUSY = -10   /*
                                  Indicates that the system is busy and
                                  the operation may be retried again.  If
                                  retries fail this should be converted to
                                  a TCF_ERR_SYSTEM for reporting.
                                */
} tcf_err_t;

typedef enum {
    TCF_LOG_DEBUG = 0,
    TCF_LOG_INFO = 1,
    TCF_LOG_WARNING = 2,
    TCF_LOG_ERROR = 3,
    TCF_LOG_CRITICAL = 4,
} tcf_log_level_t;

typedef void (*tcf_log_t)(
    tcf_log_level_t,
    const char* message);
