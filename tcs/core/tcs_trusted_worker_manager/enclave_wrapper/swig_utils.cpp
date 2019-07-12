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

#include <stdlib.h>
#include <stdio.h>
#include <string>

#include <Python.h>

#include <iostream>

#include "c11_support.h"
#include "tcf_error.h"

#include "base.h"

#include "swig_utils.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void ThrowTCFError(
    tcf_err_t ret) {
    if (ret == TCF_SUCCESS)
        return;

    std::string message = tcf::enclave_api::base::GetLastError();

    switch (ret) {
    case TCF_ERR_UNKNOWN:
        throw tcf::error::UnknownError(message);

    case TCF_ERR_MEMORY:
        throw tcf::error::MemoryError(message);

    case TCF_ERR_IO:
        throw tcf::error::IOError(message);

    case TCF_ERR_RUNTIME:
        throw tcf::error::RuntimeError(message);

    case TCF_ERR_INDEX:
        throw tcf::error::IndexError(message);

    case TCF_ERR_DIVIDE_BY_ZERO:
        throw tcf::error::DivisionByZero(message);

    case TCF_ERR_OVERFLOW:
        throw tcf::error::OverflowError(message);

    case TCF_ERR_VALUE:
        throw tcf::error::ValueError(message);

    case TCF_ERR_SYSTEM:
        throw tcf::error::SystemError(message);

    case TCF_ERR_SYSTEM_BUSY:
        throw tcf::error::SystemBusyError(message);

    default:
        throw std::runtime_error(message);
    }

}  // ThrowTCFError

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
static PyObject* glogger = NULL;
void _SetLogger(
    PyObject* inLogger) {
    if (glogger) {
        Py_DECREF(glogger);
    }
    glogger = inLogger;
    if (glogger) {
        Py_INCREF(glogger);
    }
}  // _SetLogger

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void InitializeTCFEnclaveModule() {
    // Intentionally left blank
}  // InitializeTCFEnclaveModule

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void TerminateInternal() {
    _SetLogger(NULL);
}  // TerminateInternal
