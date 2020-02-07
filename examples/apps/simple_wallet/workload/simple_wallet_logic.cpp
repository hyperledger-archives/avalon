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
#include <stdint.h>
#include <stdarg.h>
#include <vector>

#include "simple_wallet_logic.h"
#include "enclave_utils.h"

// Check if given number is valid positive value
bool SimpleWalletLogic::IsValidAmount(std::string num_str) {
    int num = 0;
    try {
        num = std::stoi(num_str);
    } catch (...) {
        return false;
    }
    return (num > 0) ? true : false;
}

// Create account identified by account_name if not created and
// update wallet balance
std::string SimpleWalletLogic::DepositMoney(SimpleWalletIoExecutor& sw_io,
    std::string account_name, std::string amount) {
    std::string wallet_balance = sw_io.ReadWalletBalance(account_name);
    if (wallet_balance.empty()) {
        wallet_balance = sw_io.UpdateWalletBalance(account_name, amount);
        Log(TCF_LOG_INFO, "Wallet Created for the account %s. Wallet Balance: %s",
            account_name.c_str(), amount.c_str());
    } else {
        Log(TCF_LOG_INFO, "Wallet Balance before deposit: %s",
            wallet_balance.c_str());
        std::string net_wallet_balance = std::to_string(std::stoi(wallet_balance) +
            std::stoi(amount));
        wallet_balance = sw_io.UpdateWalletBalance(account_name, net_wallet_balance);
        Log(TCF_LOG_INFO, "Updated Wallet Balance: %s",
            wallet_balance.c_str());
    }
    return account_name + "::" + wallet_balance;
}

// Deduct given balance from debitor account and credit balance to creditor account
std::string SimpleWalletLogic::TransferMoney(SimpleWalletIoExecutor& sw_io,
    std::string debitor_account, std::string creditor_account,
    std::string amount) {
    std::string debitor_balance = sw_io.ReadWalletBalance(debitor_account);

    if (debitor_balance.empty()) {
        Log(TCF_LOG_ERROR, "No debitor account %s details found in the ledger: ",
            debitor_account.c_str());
        return "Debitor wallet not found";
    }

    if (std::stoi(debitor_balance) < std::stoi(amount)) {
        Log(TCF_LOG_ERROR, "No sufficient balance in debitor's account: %s",
            debitor_account.c_str());
            return "No sufficient balance in debitor's account";
    }
    std::string creditor_balance = sw_io.ReadWalletBalance(creditor_account);
    if (creditor_balance.empty()) {
        Log(TCF_LOG_ERROR, "No creditor wallet details found for %s the ledger: ",
            creditor_account.c_str());
        return "Creditor wallet not found";
    }

    std::string net_debitor_balance = std::to_string(std::stoi(debitor_balance) -
        std::stoi(amount));
    std::string net_creditor_balance = std::to_string(std::stoi(creditor_balance) +
        std::stoi(amount));
    std::string updated_debitor_balance = sw_io.UpdateWalletBalance(debitor_account,
        net_debitor_balance);
    std::string updatedCreditorBalance = sw_io.UpdateWalletBalance(creditor_account,
        net_creditor_balance);
    return debitor_account + "::" + updated_debitor_balance + "," +
        creditor_account + "::" + updatedCreditorBalance;
}

// Deduct given amount from given account and update the wallet balance
std::string SimpleWalletLogic::WithdrawMoney(SimpleWalletIoExecutor& sw_io,
    std::string account_name, std::string amount) {
    std::string wallet_balance = sw_io.ReadWalletBalance(account_name);

    if (wallet_balance.empty()) {
        Log(TCF_LOG_ERROR, "No account %s details found in the ledger: ",
            account_name.c_str());
        return "No wallet details found";
    }

    if (std::stoi(wallet_balance) < std::stoi(amount)) {
        Log(TCF_LOG_ERROR, "No sufficient balance to withdraw fund");
        return "No sufficient balance to withdraw. Available balance: " +
            wallet_balance;
    } else {
        std::string net_wallet_balance = std::to_string(std::stoi(wallet_balance) -
            std::stoi(amount));
        wallet_balance = sw_io.UpdateWalletBalance(account_name, net_wallet_balance);
        Log(TCF_LOG_DEBUG, "Net balance after withdrawal: %s", net_wallet_balance);
    }

    return account_name + "::" + wallet_balance;
}

// Tokenize input request and call appropriate transaction processing methods
std::string SimpleWalletLogic::ProcessWalletRequest(std::string str_indata) {
    std::vector<std::string> args;
    char *saved_ptr;

    // tokenize input data
    char *token = strtok_r((char *)str_indata.c_str(), " ", &saved_ptr);
    while(token) {
         args.push_back(token);
         token = strtok_r(NULL, " ", &saved_ptr);
    }

    std::string transaction_result;
    if (args.size() > 0) {
        SimpleWalletIoExecutor sw_io;
        if (args.at(0) == "deposit") {
            if (args.size() == 3) {
                if (!IsValidAmount(args.at(2))) {
                    transaction_result = "Deposit amount should be a positive value";
                } else {
                    transaction_result = DepositMoney(sw_io, args.at(1), args.at(2));
                }
            } else {
                transaction_result = "Insufficient arguments supplied to "
                    "perform wallet operation";
            }
        } else if (args.at(0) == "transfer") {
            if (args.size() == 4) {
                if (!IsValidAmount(args.at(3))) {
                    transaction_result = "Transfer amount should be a positive value";
                } else {
                    transaction_result = TransferMoney(sw_io, args.at(1), args.at(2), args.at(3));
                }
            } else {
                transaction_result = "Insufficient arguments supplied to "
                    "perform wallet operation";
            }
        } else if (args.at(0) == "withdraw") {
            if (args.size() == 3) {
                if (!IsValidAmount(args.at(2))) {
                    transaction_result = "Withdraw amount should be a positive value";
                } else {
                    transaction_result = WithdrawMoney(sw_io, args.at(1), args.at(2));
                }
            } else {
                transaction_result = "Insufficient arguments supplied to "
                    "perform wallet operation";
            }
        }
    } else {
        transaction_result = "Insufficient arguments supplied to "
            "perform wallet operation";
    }

    return "WALLET RESULT: " + std::string(transaction_result.c_str());
}
