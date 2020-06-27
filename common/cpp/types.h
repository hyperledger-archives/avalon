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

/**
 * @file
 * Basic storage types used by Avalon.
 * Avalon string utilities,
 * including base 64, hex, and byte array conversion.
 */

#pragma once

#include <stdint.h>
#include <string>
#include <vector>
#include <list>

/** Vector type for binary unformatted data. */
typedef std::vector<uint8_t> ByteArray;

/** Vector type for containing printable characters. */
class StringArray : public std::vector<char> {
public:
    StringArray(const std::string& value) {
        assign(value);
    }

    StringArray(const size_t size) {
        resize(size);
        std::vector<char>::assign(size, '\0');
    }

    void assign(const std::string& value) {
        std::vector<char>::assign(value.begin(), value.end());
    }

    std::string str() {
        return std::string(this->data());
    }
};  /* class StringArray */

/**
 * Type for printable base64 encoded string.
 * May include '=' padding characters.
 * No whitespace, header line, or footer line. For example,
 * SHlwZXJsZWRnZXI=
 */
typedef std::string Base64EncodedString;

/**
 * Type for printable hex encoded string. For example,
 * 2D81454D9C59D73867D65C0FCC98143D4B6F1B0BDB7EB04EFED72697F462309C
 */
typedef std::string HexEncodedString;

// Simple conversion from ByteArray to String
std::string ByteArrayToString(const ByteArray& inArray);

// Conversion from byte array to string array
StringArray ByteArrayToStringArray(const ByteArray& inArray);

// Simple conversion from ByteArray to Base64EncodedString
Base64EncodedString ByteArrayToBase64EncodedString(const ByteArray& buf);

// Simple conversion from Base64EncodedString to ByteArray
ByteArray Base64EncodedStringToByteArray(const Base64EncodedString& encoded);

// Simple conversion from ByteArray to HexEncodedString
HexEncodedString ByteArrayToHexEncodedString(const ByteArray& buf);

// Simple conversion from HexEncodedString to ByteArray.
// Throws ValueError
ByteArray HexEncodedStringToByteArray(const HexEncodedString& encoded);
