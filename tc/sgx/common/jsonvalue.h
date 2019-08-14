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
#include "packages/parson/parson.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class JsonValue {
public:
    JsonValue(JSON_Value* value = nullptr) {
        this->value = value;
    }  // JsonValue

    virtual ~JsonValue() {
        if (this->value) {
            json_value_free(this->value);
        }
    }  // ~JsonValue

    operator JSON_Value* () {
        return value;
    }  // operator JSON_Value*

    operator const JSON_Value* () const {
        return value;
    }  // operator JSON_Value*

    JSON_Value* value;
};  // JsonValue
