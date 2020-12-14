/* Copyright 2020 Intel Corporation
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

#include <string>

// Verifies signature of the message by extracting public key from certificate
bool verify_dcap_quote_signature(
    const std::string& dcap_attestation_signing_cert_pem,
    const std::string& dcap_quote, const std::string& dcap_signature);

// Verifies certificate against IAS CA certificate
bool verify_dcap_quote(const std::string& dcap_quote);
