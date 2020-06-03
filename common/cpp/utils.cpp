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
/**
split the string based on delimeter
*/
template<typename Out>
void split(const std::string &str, char delim, Out result) {
        std::size_t current, previous = 0;

        current = str.find(delim);
        while (current != std::string::npos) {
                std::string item = str.substr(previous, current - previous);
                if (item.compare("") != 0)
                        *(result++) = item;
                previous = current + 1;
                current = str.find(delim, previous);
        }

        std::string item = str.substr(previous, current - previous);
        if (item.compare("") != 0)
                *(result++) = item;
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, std::back_inserter(elems));
    return elems;
}
