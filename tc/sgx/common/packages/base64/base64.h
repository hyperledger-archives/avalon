//
//  base64 encoding and decoding with C++.
//  Version: 1.01.00
//

/*
    The original source code has been modified to be used with Trusted Compute Framework (TCFs).
*/

#pragma once

#include <string>
#include <vector>

std::string base64_encode(
    const std::vector<uint8_t>& raw_buffer);

std::vector<uint8_t> base64_decode(
    const std::string& encoded_string);
