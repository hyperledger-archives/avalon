//
//  base64 encoding and decoding with C++.
//  Version: 1.01.00
//  Copyright (C) 2004-2017 René Nyffenegger
//  Copyright 2020 Intel Corporation
//

/**
 * @file
 * Base64 encode and decode functions.
 * Used to encode/decode between binary data into a printable character format.
 */

/*
 * The original source code has been modified to be used with
 * Hyperledger Avalon. Added function base64_decoded_length().
 */

#pragma once

#include <string>
#include <vector>

std::string base64_encode(
    const std::vector<uint8_t>& raw_buffer);

std::vector<uint8_t> base64_decode(
    const std::string& encoded_string);

unsigned int base64_decoded_length(const char *encoded_string,
    unsigned int encoded_len);
