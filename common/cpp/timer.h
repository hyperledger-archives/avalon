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

#include <stdint.h>
#include <string>
#include <vector>

#include "tcf_error.h"

extern uint64_t GetTimer(void);
extern void Log(int level, const char* fmt, ...);

namespace tcf {
    namespace utility {

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class Timer {
        private:
            const std::string key_;
            uint64_t start_time_;

        public:
            Timer(const std::string& key) : key_(key) {
                start_time_ = GetTimer();
            }

            ~Timer(void) {
                Log(TCF_LOG_INFO, "%s: %lu", key_.c_str(), GetTimer() - start_time_);
            }
        };
    }  // namespace utility
}  // namespace tcf

#if DEBUG
#define __TIMEIT__() tcf::utility::Timer __ignore__(__FUNCTION__)
#else
#define __TIMEIT__() {}
#endif
