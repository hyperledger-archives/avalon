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

#include "parson.h"
#include "error.h"
#include "tcf_error.h"
#include "types.h"

const char* GetJsonStr(const JSON_Object* json_object,
                       const char* name,
                       const char* err_msg) {
        const char* pvalue = json_object_dotget_string(json_object, name);

        if (!pvalue) {
            if (err_msg) {
                tcf::error::ThrowIf<tcf::error::ValueError>(!pvalue, err_msg);
            } else {
                pvalue = "";
            }
        }
        return pvalue;
}

void GetByteArray(const JSON_Object* object,
                  const char* name,
                  const char* err_msg,
                  ByteArray& dst) {
        const char* pvalue = GetJsonStr(object, name, err_msg);
        std::string str = pvalue;
        std::copy(str.begin(), str.end(), std::back_inserter(dst));
}

double GetJsonNumber(const JSON_Object* object, const char* name) {
        return json_object_dotget_number(object, name);
}

void JsonSetStr(JSON_Object* json, const char* name, const char* value, const char* err) {
        JSON_Status jret = json_object_dotset_string(json, name, value);
        tcf::error::ThrowIf<tcf::error::RuntimeError>(jret != JSONSuccess, err);
}

void JsonSetNumber(JSON_Object* json, const char* name, double value, const char* err) {
        JSON_Status jret = json_object_dotset_number(json, name, value);
        tcf::error::ThrowIf<tcf::error::RuntimeError>(jret != JSONSuccess, err);
}

