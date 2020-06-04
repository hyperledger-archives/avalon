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

/**
 * @file
 * Avalon ByteArray and String conversion utilities.
 */

#include <string>
#include <algorithm>

#include "types.h"
#include "utils.h"

/**
 * Convert a C++ string to a ByteArray vector.
 */
ByteArray StrToByteArray(std::string str) {
        ByteArray ba;
        std::copy(str.begin(), str.end(), std::back_inserter(ba));
        return ba;
}

/**
 * Convert a ByteArray vector to a C++ string.
 */
std::string ByteArrayToStr(ByteArray ba) {
        std::string str(ba.begin(), ba.end());
        return str;
}
