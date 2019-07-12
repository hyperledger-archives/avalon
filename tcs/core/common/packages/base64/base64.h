//
//  base64 encoding and decoding with C++.
//  Version: 1.01.00
//

/*
    The original source code has been modified to be used with Trusted Compute Framework (TCFs).
*/

#pragma once

#include "types.h"

#define BASE64_SIZE(x) (static_cast<size_t>(((((x) - 1) / 3) * 4 + 4) + 1))

Base64EncodedString base64_encode(
    const ByteArray& raw_buffer);

ByteArray base64_decode(
    const Base64EncodedString& encoded_string);
