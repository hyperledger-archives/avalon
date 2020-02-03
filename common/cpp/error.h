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

#include <stdexcept>
#include <string>

#include "tcf_error.h"

namespace tcf {
    namespace error {
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
        class CryptoError : public Error {
        public:
            explicit CryptoError(
                const std::string& msg
                ) : Error(TCF_ERR_CRYPTO, msg) {}
        }; // class CryptoError


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
        class IndexError : public Error {
        public:
            explicit IndexError(
                const std::string& msg
                ) :
                Error(TCF_ERR_INDEX, msg) {}
        }; // class IndexError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class DivisionByZero : public Error {
        public:
            explicit DivisionByZero(
                const std::string& msg
                ) : Error(TCF_ERR_DIVIDE_BY_ZERO, msg) {}
        }; // class DivisionByZero

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class OverflowError : public Error {
        public:
            explicit OverflowError(
                const std::string& msg
                ) : Error(TCF_ERR_OVERFLOW, msg) {}
        }; // class OverflowError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class ValueError : public Error {
        public:
            explicit ValueError(
                const std::string& msg
                ) : Error(TCF_ERR_VALUE, msg) {}
        }; // class ValueError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class SystemError : public Error {
        public:
            explicit SystemError(
                const std::string& msg
                ) : Error(TCF_ERR_SYSTEM, msg) {}
        }; // class SystemError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class SystemBusyError : public Error {
        public:
            explicit SystemBusyError(
                const std::string& msg
                ) : Error(TCF_ERR_SYSTEM_BUSY, msg) {}
        }; // class SystemBusyError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class UnknownError : public Error {
        public:
            explicit UnknownError(
                const std::string& msg
                ) : Error(TCF_ERR_UNKNOWN, msg) {}
        }; // class UnknownError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        // Error checking utilities.
        template<typename PointerType>
        inline void ThrowIfNull(
            const PointerType ptr,
            const char* msg = nullptr
            ) {
            if (!ptr) {
                throw ValueError(msg ? msg : "Unexpected null parameter.");
            }
        } // ThrowIfNull

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

} // namespace tcf
