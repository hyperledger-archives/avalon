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

%module db_store

%include <std_vector.i>
%include <std_map.i>
%include <std_string.i>

namespace std {
    %template(StringVector) vector<string>;
    %template(StringMap) map<string, string>;
}

%include <exception.i>

%exception {
    try
    {
        $function
    }
    catch (db_error::MemoryError& e)
    {
        SWIG_exception(SWIG_MemoryError, e.what());
    }
    catch (db_error::IOError& e)
    {
        SWIG_exception(SWIG_IOError, e.what());
    }
    catch (db_error::RuntimeError& e)
    {
        SWIG_exception(SWIG_ValueError, e.what());
    }
    catch (db_error::DivisionByZero& e)
    {
        SWIG_exception(SWIG_DivisionByZero, e.what());
    }
    catch (db_error::UnknownError& e) {
        SWIG_exception(SWIG_UnknownError, e.what());
    }
    catch (...)
    {
        SWIG_exception(SWIG_RuntimeError,"Unknown exception");
    }
}

%{
#include "swig_utils.h"
#include "db_store.h"
#include "db_store_error.h"
%}


%include "db_store.h"

