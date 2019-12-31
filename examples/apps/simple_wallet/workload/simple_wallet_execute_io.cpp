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
#include <string.h>

#include "types.h"
#include "jsonvalue.h"
#include "json_utils.h"
#include "crypto_utils.h"
#include "error.h"
#include "tcf_error.h"
#include "enclave_utils.h"
#include <parson.h>

#include "simple_wallet_execute_io.h"
#include "file_io.h"
//#include "workload_crypto_utils.h"

#define LEDGER_FILE "/tmp/account_ledger.json"

SimpleWalletLedger* SimpleWalletLedger::instance = 0;

SimpleWalletIoExecutor::SimpleWalletIoExecutor() {}

// Create encryption key used for encrypting or decrypting
// ledger having all wallet details
bool SimpleWalletIoExecutor::CreateLedgerEncryptionKey() {
    std::string enc_key = tcf::crypto::CreateHexEncodedEncryptionKey();
    if (enc_key.empty()) {
        return false;
    }
    SimpleWalletLedger* ledger = SimpleWalletLedger::GetInstance();
    ledger->ledger_encryption_key = enc_key;
    return true;
}

SimpleWalletLedger* SimpleWalletLedger::GetInstance() {
    if(!SimpleWalletLedger::instance) {
        SimpleWalletLedger::instance = new SimpleWalletLedger();
    }
    return SimpleWalletLedger::instance;
}

// Create Wallet ledger file to store details of transactions in encrypted format
void SimpleWalletIoExecutor::CreateWalletLedger() {
    uint32_t status = ExecuteFileWrite("");
    if (status == 0) {
        Log(TCF_LOG_INFO, "Successfully created wallet ledger file %s",
            LEDGER_FILE);
    } else {
        Log(TCF_LOG_INFO, "Failed to create wallet ledger file %s",
            LEDGER_FILE);
    }
}

// Get wallet balance for given account from json serialized ledger
std::string SimpleWalletIoExecutor::GetWalletBalanceFromLedger(std::string ledger_data,
    std::string account_name) {
    // Parse account_ledger.json data
    JsonValue parsed(json_parse_string(ledger_data.c_str()));
    tcf::error::ThrowIfNull(parsed.value,
        "failed to parse the work order request, badly formed JSON");

    JSON_Object* ledger_object = json_value_get_object(parsed);
    tcf::error::ThrowIfNull(ledger_object, "Missing JSON object in ledger");
    Log(TCF_LOG_INFO, "Getting balance for the account from ledger object: %s",
        account_name);
    std::string balance = GetJsonStr(ledger_object, account_name.c_str(),
        nullptr);
    Log(TCF_LOG_INFO, "GetWalletBalanceFromLedger::Got balance for account %s",
        account_name);
    return balance;
}

std::string SimpleWalletIoExecutor::UpdateLedger(std::string ledger_data,
    std::string account_name, std::string amount) {
    JSON_Value* ledger_val;
    if (ledger_data.empty()) {
        Log(TCF_LOG_INFO, "Creating first wallet in ledger");
        ledger_val = json_value_init_object();
    } else {
        // Parse account_ledger.json data
        ledger_val = json_parse_string(ledger_data.c_str());
        tcf::error::ThrowIfNull(
        ledger_val, "failed to parse wallet ledger. Poorly formatted json");
    }

    JSON_Object* ledger_obj = json_value_get_object(ledger_val);
    tcf::error::ThrowIfNull(ledger_obj, "Missing JSON object in ledger");

    JsonSetStr(ledger_obj, account_name.c_str(), amount.c_str(),
        "failed to serialize wallet details");
    // Serialize the resulting json
    size_t serialized_size = json_serialization_size(ledger_val);
    ByteArray serialized_response;
    serialized_response.resize(serialized_size);

    JSON_Status jret = json_serialize_to_buffer(ledger_val,
        reinterpret_cast<char*>(&serialized_response[0]),
        serialized_response.size());
    tcf::error::ThrowIf<tcf::error::RuntimeError>(
        jret != JSONSuccess, "Wallet serialization failed");

    return std::string(serialized_response.begin(), serialized_response.end());

}

// Read ledger file and store the data in ledger_data buffer
uint32_t SimpleWalletIoExecutor::ExecuteFileRead(std::string& ledger_data,
    size_t ledger_data_size) {
    std::string out_buf;
    std::string result;

    FileIoExecutor file_io;
    uint32_t file_handler_id = file_io.GetIoHandlerId("tcf-base-file-io");
    file_io.SetIoHandlerId(file_handler_id);
    file_io.SetFileName(LEDGER_FILE);

    size_t result_size = file_io.GetMaxIoResultSize();
    out_buf.reserve(ledger_data_size);
    result.reserve(result_size);

    uint32_t status = file_io.FileRead((uint8_t *)result.c_str(), result_size,
        (uint8_t *)out_buf.c_str(), ledger_data_size);
    if (status == 0) {
        Log(TCF_LOG_DEBUG, "File Read operation successful. File content %s",
            out_buf.c_str());
        ledger_data = out_buf.c_str();
    }
    else {
        Log(TCF_LOG_ERROR, "File Read operation failed. File content: %s",
            out_buf.c_str());
    }
    return status;
}

// Write wallet data in ledger file
uint32_t SimpleWalletIoExecutor::ExecuteFileWrite(std::string file_data) {
    FileIoExecutor file_io;
    uint32_t file_handler_id = file_io.GetIoHandlerId("tcf-base-file-io");
    file_io.SetIoHandlerId(file_handler_id);
    file_io.SetFileName(LEDGER_FILE);

    std::string result;
    size_t result_size = file_io.GetMaxIoResultSize();
    result.reserve(result_size);

    uint32_t status = file_io.FileWrite((uint8_t *)result.c_str(), result_size,
        (const uint8_t *)file_data.c_str(), file_data.length());
    if (status == 0) {
        Log(TCF_LOG_DEBUG, "File Write operation successful");
    }
    else {
        Log(TCF_LOG_ERROR, "File Write operation Failed: %s", result.c_str());
    }
    return status;
}

// Read ledger file and get wallet balance corresponding to given account
std::string SimpleWalletIoExecutor::ReadWalletBalance(std::string account_name) {
    std::string ledger_data;
    FileIoExecutor file_io;
    size_t ledger_data_size = file_io.GetMaxFileSize();
    uint32_t status = ExecuteFileRead(ledger_data, ledger_data_size);
    SimpleWalletLedger* ledger = SimpleWalletLedger::GetInstance();
    if (status == 0) {
        if (!ledger_data.empty()) {
            // Decrypt ledger data by crypto api's
            ledger->ledger_details = tcf::crypto::DecryptData(ledger_data,
                ledger->ledger_encryption_key);
        } else {
            Log(TCF_LOG_INFO, "ledger contains no account details");
            return "";
        }
    } else {
        Log(TCF_LOG_ERROR, "Failed to read wallet balance for account %s",
        account_name.c_str());
	    return "";
    }

    std::string balance;
    // get wallet balance of given account
    try {
        balance = GetWalletBalanceFromLedger(ledger->ledger_details,
            account_name);
    } catch (tcf::error::ValueError& e) {
        Log(TCF_LOG_ERROR, "Failed to get wallet balance from ledger, %s", e.what());
        return "";
    }
    return balance;
}

// Write ledger file and update wallet balance corresponding to given account
std::string SimpleWalletIoExecutor::UpdateWalletBalance(std::string account_name,
    std::string amount) {
    SimpleWalletLedger* ledger = SimpleWalletLedger::GetInstance();
    std::string ledger_data;
    try {
        ledger_data = UpdateLedger(ledger->ledger_details,
            account_name, amount);
    } catch (tcf::error::ValueError& e) {
        Log(TCF_LOG_ERROR, "Failed to update ledger, %s", e.what());
        return "";
    }
    Log(TCF_LOG_INFO, "encrypting ledger data:: (after serialization) %s",
        ledger_data.c_str());
    std::string enc_ledger_data = tcf::crypto::EncryptData(ledger_data,
        ledger->ledger_encryption_key);
    uint32_t status = ExecuteFileWrite(enc_ledger_data);
    if (status == 0) {
        Log(TCF_LOG_DEBUG, "File Write operation successful");
        ledger->ledger_details = ledger_data;
    }
    else {
        Log(TCF_LOG_ERROR, "File Write operation Failed");
        return "";
    }
    return amount;
}
