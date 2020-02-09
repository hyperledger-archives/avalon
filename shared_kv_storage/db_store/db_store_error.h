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

#pragma once

#include <stdexcept>
#include <string>

#include "tcf_error.h"

namespace db_error {

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class Error : public std::runtime_error {
        private:
            tcf_err_t _error_code;
        public:
            Error(
                tcf_err_t in_error,
                const std::string& msg
                ) :
                runtime_error(msg) {
                    _error_code = in_error;
                }
            virtual ~Error() throw() {}

            tcf_err_t error_code()  { return _error_code; }
    }; // class Error

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class MemoryError : public Error {
        public:
            explicit MemoryError(
                const std::string& msg
                ) :
                Error(TCF_ERR_MEMORY, msg) {}
    }; // class MemoryError

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class IOError : public Error {
        public:
            explicit IOError(
                const std::string& msg
                ) :
                Error(TCF_ERR_IO, msg) {}
    }; // class IOError

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class RuntimeError : public Error {
        public:
            explicit RuntimeError(
                const std::string& msg
                ) :
                Error(TCF_ERR_RUNTIME, msg) {}
    }; // class RuntimeError

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class DivisionByZero : public Error {
        public:
            explicit DivisionByZero(
                const std::string& msg
                ) : Error(TCF_ERR_DIVIDE_BY_ZERO, msg) {}
    }; // class DivisionByZero

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    class UnknownError : public Error {
        public:
            explicit UnknownError(
                const std::string& msg
                ) : Error(TCF_ERR_UNKNOWN, msg) {}
    }; // class UnknownError

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    template <typename except>
        inline void ThrowIf(
        bool condition,
        const char* msg
        ) {
        if (condition) {
            throw except(msg);
        }
    } // ThrowIf

}

