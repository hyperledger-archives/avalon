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

#include <stdarg.h>
#include <stdio.h>
#include <chrono>

#include "c11_support.h"
#include "log.h"

namespace tcf {

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    // XX Declaration of static helper functions                 XX
    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    static void LogStdOut(
        tcf_log_level_t,
        const char* msg);

    static tcf_log_t g_LogFunction = LogStdOut;

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void Log(
        tcf_log_level_t logLevel,
        const char* message);

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    // XX External interface                                     XX
    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void SetLogFunction(
        tcf_log_t logFunction) {
        if (logFunction) {
            g_LogFunction = logFunction;
        }
    }  // SetLogFunction

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void Log(
        tcf_log_level_t logLevel,
        const char* message,
        ...) {
        if (g_LogFunction) {
            const size_t BUFFER_SIZE = 2048;
            char msg[BUFFER_SIZE] = { '\0' };
            va_list ap;
            va_start(ap, message);
            vsnprintf_s(msg, BUFFER_SIZE, message, ap);
            va_end(ap);

            g_LogFunction(logLevel, msg);
        }
    }  // Log

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    // XX Internal helper functions                              XX
    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    static void LogStdOut(
        tcf_log_level_t logLevel,
        const char* message) {
        printf("%s\n", message);
        // Flush the logs to stdout.
        // Without flushing, messages are not seen in stdout.
        fflush(stdout);
    }  // LogStdOut

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    void Log(
        tcf_log_level_t logLevel,
        const char* message) {
        if (g_LogFunction) {
            g_LogFunction(logLevel, message);
        }
    }  // Log

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    uint64_t GetTimer() {
        uint64_t value;

        std::chrono::time_point<std::chrono::high_resolution_clock> now = std::chrono::high_resolution_clock::now();
        value = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
        return value;
    }

}  // namespace tcf
