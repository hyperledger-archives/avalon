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

%module dcap_verify_report 

%{
#include "types.h"
#include "error.h"
#include "dcap_attestation_util.h"
%}

%include <exception.i>

%exception  {
    try
    {
        $function
    }
    catch (tcf::error::MemoryError& e)
    {
        SWIG_exception(SWIG_MemoryError, e.what());
    }
    catch (tcf::error::IOError& e)
    {
        SWIG_exception(SWIG_IOError, e.what());
    }
    catch (tcf::error::RuntimeError& e)
    {
        SWIG_exception(SWIG_ValueError, e.what());
    }
    catch (tcf::error::IndexError& e)
    {
        SWIG_exception(SWIG_ValueError, e.what());
    }
    catch (tcf::error::DivisionByZero& e)
    {
        SWIG_exception(SWIG_DivisionByZero, e.what());
    }
    catch (tcf::error::OverflowError& e)
    {
        SWIG_exception(SWIG_OverflowError, e.what());
    }
    catch (tcf::error::ValueError& e)
    {
        SWIG_exception(SWIG_ValueError, e.what());
    }
    catch (tcf::error::SystemError& e)
    {
        SWIG_exception(SWIG_SystemError, e.what());
    }
    catch (tcf::error::SystemBusyError& e)
    {
        SWIG_exception(SWIG_SystemError, e.what());
    }
    catch (tcf::error::UnknownError& e) {
        SWIG_exception(SWIG_UnknownError, e.what());
    }
    catch (...)
    {
        SWIG_exception(SWIG_RuntimeError,"Unknown exception");
    }
}


%include "std_string.i"
%include "stdint.i"

%include "types.h"
%include "dcap_attestation_util.h"
