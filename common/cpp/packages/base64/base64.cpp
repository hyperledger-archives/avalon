/*
   base64.cpp and base64.h

   base64 encoding and decoding with C++.

   Version: 1.01.00

   Copyright (C) 2004-2017 René Nyffenegger
   Copyright 2020 Intel Corporation

   This source code is provided 'as-is', without any express or implied
   warranty. In no event will the author be held liable for any damages
   arising from the use of this software.

   Permission is granted to anyone to use this software for any purpose,
   including commercial applications, and to alter it and redistribute it
   freely, subject to the following restrictions:

   1. The origin of this source code must not be misrepresented; you must not
      claim that you wrote the original source code. If you use this source code
      in a product, an acknowledgment in the product documentation would be
      appreciated but is not required.

   2. Altered source versions must be plainly marked as such, and must not be
      misrepresented as being the original source code.

   3. This notice may not be removed or altered from any source distribution.

   René Nyffenegger rene.nyffenegger@adp-gmbh.ch

*/

/**
 * @file
 * Base64 encode and decode functions.
 * Used to encode/decode between binary data into a printable character format.
 */

/*
 * The original source code has been modified to be used with
 * Hyperledger Avalon. Added function base64_decoded_length().
 */


#include <ctype.h>
#include "base64.h"

/*
 * Used to adjust the decoded length of a base64 string.
 * Check if the base64 string is padded at the end with '='
 * and adjust the output length.
 */
#define ADJUST_DECODE_LENGTH(in, in_len) \
    ((((in)[(in_len) - 1] == '=') ? -1 : 0) + \
     (((in)[(in_len) - 2] == '=') ? -1 : 0))

static const std::string base64_chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";

// Return true if this is a base64 character (excluding '=' padding)
static inline bool is_base64(unsigned char c) {
    return (isalnum(c) || (c == '+') || (c == '/'));
}


/**
 * Encode a vector of binary data to a printable base64 string.
 * 0 to 2 '=' padding characters may be appended.
 * No headers or whitespace is generated.
 *
 * @param buf Buffer containing binary data to encode
 * @returns   String containing base64 encoded data
 */
std::string base64_encode(const std::vector<uint8_t>& buf) {
    std::string ret;
    int i = 0;
    int j = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];
    int in_len = buf.size();
    unsigned char const* bytes_to_encode = buf.data();
    while (in_len--) {
        char_array_3[i++] = *(bytes_to_encode++);
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) +
                ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) +
                ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (i = 0; (i < 4); i++) {
                ret += base64_chars[char_array_4[i]];
            }
            i = 0;
        }
    }

    if (i) {
        for (j = i; j < 3; j++) {
            char_array_3[j] = '\0';
        }

        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) +
            ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) +
            ((char_array_3[2] & 0xc0) >> 6);

        for (j = 0; (j < i + 1); j++) {
            ret += base64_chars[char_array_4[j]];
        }

        // Add padding characters, if needed
        while ((i++ < 3)) {
            ret += '=';
        }
    }

    return ret;
}


/**
 * Decode a base64 encoded printable string into a vector of binary data.
 * 0 to 2 '=' padding characters may be appended.
 * Decoding stops at first non-base64 character.
 *
 * @param encoded_string Printable string containing base64 encoded data.
 *                       No embedded whitespace characters are present.
 * @returns Vector containing decoded binary data
 */
std::vector<uint8_t> base64_decode(const std::string& encoded_string) {
    int in_len = encoded_string.size();
    int i = 0;
    int j = 0;
    int in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    std::vector<uint8_t> ret;

    // Decode until a padding character or non-base64 character is found
    while (in_len-- && (encoded_string[in_] != '=') &&
            is_base64(encoded_string[in_])) {
        char_array_4[i++] = encoded_string[in_];
        in_++;

        if (i == 4) {
            for (i = 0; i < 4; i++) {
                char_array_4[i] = base64_chars.find(char_array_4[i]);
            }

            char_array_3[0] = (char_array_4[0] << 2) +
                ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) +
                ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) +
                char_array_4[3];

            for (i = 0; (i < 3); i++) {
                ret.push_back(char_array_3[i]);
            }
            i = 0;
        }
    }

    if (i) {
        for (j = 0; j < i; j++) {
            char_array_4[j] = base64_chars.find(char_array_4[j]);
        }

        char_array_3[0] = (char_array_4[0] << 2) +
            ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) +
            ((char_array_4[2] & 0x3c) >> 2);

        for (j = 0; (j < i - 1); j++) {
            ret.push_back(char_array_3[j]);
        }
    }

    return ret;
}


/**
 * Calculate the length of a base 64 encoded string after decoding.
 *
 * @param encoded_string Printable string containing base64 encoded data.
 *                       No embedded whitespace characters are present
 * @param encoded_length Length of encoded_string
 * @returns Length of encoded_string after decoding
 */
unsigned int base64_decoded_length(const char *encoded_string,
    unsigned int encoded_len)
{
    if (encoded_string == nullptr || encoded_len == 0) {
        return 0;
    }

    unsigned int len = (encoded_len / 4) * 3;

    if (encoded_len > 3)
        len += ADJUST_DECODE_LENGTH(encoded_string, encoded_len);
    return (len);
}
