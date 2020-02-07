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

class SimpleWalletLedger {
private:
    static SimpleWalletLedger* instance;
public:
    static SimpleWalletLedger* GetInstance();

    // Placeholder to store all ledger entries. Useful when updating
    // given account in the ledger.
    std::string ledger_details;

    // Symmetric encryption key to encrypt/decrypt ledger file
    std::string ledger_encryption_key;

};  // class SimpleWalletLedger

class SimpleWalletIoExecutor {

public:
    SimpleWalletIoExecutor(void);

    bool CreateLedgerEncryptionKey();

    void CreateWalletLedger();

    uint32_t ExecuteFileRead(std::string& ledger_data, size_t ledger_data_size);

    uint32_t ExecuteFileWrite(std::string file_data);

    std::string GetWalletBalanceFromLedger(std::string ledger_data,
        std::string account_name);

    std::string UpdateLedger(std::string ledger_data, std::string account_name,
        std::string amount);

    std::string ReadWalletBalance(std::string account_name);

    std::string UpdateWalletBalance(std::string account_name, std::string amount);
};
