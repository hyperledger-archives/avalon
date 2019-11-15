/* Copyright 2019 Banco Santander S.A.
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

#pragma once

#include <string>
#include <vector>

struct Client {
    std::string clientId;
    std::string fullName;
};

struct Transaction {
    std::string from;
    std::string to;
    int amount;
    int fraction;
    std::string currency;
    std::string date;
};

struct countryInfo{
    int maxClients;
    int actClients;
    int maxTransactions;
    int actTransactions;
    std::vector<Client> clientList;
    std::vector<Transaction> transactionList;
};


class AmlResultLogic{
private:
    std::vector<std::string> allCountries;
    std::vector<std::string> loadedCountries;
    int numberTotalCountries;
    std::vector<countryInfo> infoPerCountry;
    std::string participatingCountries;
    int alreadyLoaded;
    bool clientInit = false;
    bool checkValidCountriesDeclaration(std::vector<std::string> cliData);
    bool checkUserBelongsToValidCountry(std::vector<std::string> cliData);
    bool checkTransactionBelongsToValidCountries(std::vector<std::string> cliData);

    std::string getNameFromId(std::string id);
    std::string findSuspects();
    bool findNextSuspect(int *traveledCountriesSize, std::vector<std::string> &traveledCountries,
        std::vector<std::string> &suspectIds, std::string lastId, std::string nextId, int amount);


public:
    AmlResultLogic(void);
    ~AmlResultLogic(void);
    std::string executeWorkOrder(std::string str_in);

};

