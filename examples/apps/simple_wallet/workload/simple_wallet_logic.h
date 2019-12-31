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
#include "simple_wallet_execute_io.h"

class SimpleWalletLogic {

private:
    bool IsValidAmount(std::string num_str);

    std::string DepositMoney(SimpleWalletIoExecutor& sw_io,std::string account_name,
        std::string amount);

    std::string TransferMoney(SimpleWalletIoExecutor& sw_io,
        std::string debitor_account, std::string creditor_account,
        std::string amount);

    std::string WithdrawMoney(SimpleWalletIoExecutor& sw_io,
        std::string account_name, std::string amount);

public:
    std::string ProcessWalletRequest(std::string str_indata);
};
