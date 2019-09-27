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

#include <string>

// Verifies signature of the message by extracting public key from certificate
bool verify_ias_report_signature(const std::string& ias_attestation_signing_cert_pem,
                                   const std::string& ias_report,
                                   const std::string& ias_signature);

// Verifies certificate against IAS CA certificate
bool verify_quote(const std::string& ias_report, int group_out_of_date_is_ok);

