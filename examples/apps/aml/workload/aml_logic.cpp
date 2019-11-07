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

#include "aml_logic.h"

AmlResultLogic::AmlResultLogic() {}

AmlResultLogic::~AmlResultLogic() {}

template<typename Out>

void splot(const std::string &str, char delim, Out result)
{
    std::size_t current, previous = 0;

    current = str.find(delim);
    while (current != std::string::npos) 
    {
        std::string item = str.substr(previous, current - previous);
        if (item.compare("") != 0)
            *(result++) = item; 
        previous = current + 1;
        current = str.find(delim, previous);
    }
    
    std::string item = str.substr(previous, current - previous);
    if (item.compare("") != 0)
        *(result++) = item;
}

std::vector<std::string> splot(const std::string &s, char delim)
{
    std::vector<std::string> elems;
    splot(s, delim, std::back_inserter(elems));
    return elems;
}

std::string AmlResultLogic::getNameFromId(std::string id) {
    std::string country = id.substr(0,2); 
    int i;
    for(i = 0; i < numberTotalCountries; i++){
        if(allCountries[i] == country){
            break;
        }
    }

    if(i < numberTotalCountries){
        for (int j = 0; j < infoPerCountry[i].actClients; j++) {
            if (infoPerCountry[i].clientList[j].clientId == id) {
                return infoPerCountry[i].clientList[j].fullName;
            }
        }
    }

    return "unknown id " + id;
}

std::string AmlResultLogic::findSuspects() {
    std::string wholeSuspectList = "Do not trust these people:";
    int traveledCountriesSize = 0;
    std::vector<std::string> traveledCountries;
    std::vector<std::string> suspectIds;
    std::string lastId;
    std::string nextId;
    int amount;
    bool found;
    int numFound=0;

    for(int i = 0; i < infoPerCountry[0].actTransactions; i++){
        if(infoPerCountry[0].transactionList[i].from.substr(0,2) != infoPerCountry[0].transactionList[i].to.substr(0,2)){
            nextId = infoPerCountry[0].transactionList[i].to;
            lastId = infoPerCountry[0].transactionList[i].from;
            amount = infoPerCountry[0].transactionList[i].amount;
            traveledCountriesSize++;
            traveledCountries.resize(traveledCountriesSize, infoPerCountry[0].transactionList[i].from.substr(0,2));
            suspectIds.resize(traveledCountriesSize, infoPerCountry[0].transactionList[i].from);
            found = findNextSuspect(&traveledCountriesSize, traveledCountries, suspectIds, lastId, nextId, amount);
        }
        if(found){
            if(numFound>0){
                wholeSuspectList += ";";
            }
            wholeSuspectList += " (";
            for(int k = 0; k < suspectIds.size(); k++){
                wholeSuspectList += getNameFromId(suspectIds[k]);
                if(k < suspectIds.size() - 1) {
                    wholeSuspectList += ", ";
                }
                else {
                    wholeSuspectList += ")";
                }
            }
            wholeSuspectList += ", suspicious of moving " + std::to_string(infoPerCountry[0].transactionList[i].amount)
                + " " + infoPerCountry[0].transactionList[i].currency + " in cycles " ;
            numFound++;
        }
        traveledCountriesSize = 0;
        traveledCountries.resize(0);
        suspectIds.resize(0);
        found = false;

    }


    return wholeSuspectList;
}

bool newCountry(std::string from, std::string to, std::vector<std::string> traveledCountries){
    bool newCountry = true;
    if(from != to){
        for(int i = 0; i < traveledCountries.size();i++){
            if(to.substr(0,2) == traveledCountries[i]){
                newCountry = false;
            }
        }
    }
    else{
        newCountry = false;
    }
    return newCountry;
}

bool AmlResultLogic::findNextSuspect(int *traveledCountriesSize, std::vector<std::string> &traveledCountries,
    std::vector<std::string> &suspectIds, std::string lastId, std::string nextId, int amount){
    bool found = false;
    if(*traveledCountriesSize < numberTotalCountries - 1){
        std::string country = nextId.substr(0,2);
        int i;
        for(i = 0; i < numberTotalCountries; i++){
            if(allCountries[i] == country){
                break;
            }
        }
        int j = 0;
        while (!found && j < infoPerCountry[i].actTransactions){
            if(newCountry(infoPerCountry[i].transactionList[j].from,infoPerCountry[i].transactionList[j].to,traveledCountries)
                && infoPerCountry[i].transactionList[j].amount == amount){
                std::string nextId_n = infoPerCountry[i].transactionList[j].to;
                int amount_n = infoPerCountry[i].transactionList[j].amount;
                (*traveledCountriesSize)++;
                traveledCountries.resize(*traveledCountriesSize, infoPerCountry[i].transactionList[j].from.substr(0,2));
                suspectIds.resize(*traveledCountriesSize, infoPerCountry[i].transactionList[j].from);
                found = findNextSuspect(traveledCountriesSize, traveledCountries, suspectIds, lastId, nextId_n, amount_n);
            }
            j++;
        }
    }
    else if(*traveledCountriesSize == numberTotalCountries - 1){
        std::string country = nextId.substr(0,2);
        int i;
        for(i = 0; i < numberTotalCountries; i++){
            if(allCountries[i] == country){
                break;
            }
        }
        int j = 0;
        while (!found && j < infoPerCountry[i].actTransactions){
            if(infoPerCountry[i].transactionList[j].from == nextId && infoPerCountry[i].transactionList[j].to
                == lastId && infoPerCountry[i].transactionList[j].amount == amount){
                (*traveledCountriesSize)++;
                suspectIds.resize(*traveledCountriesSize);
                suspectIds[(*traveledCountriesSize) - 1] = infoPerCountry[i].transactionList[j].from;
                found = true;
            }
            j++;
        }
    }
    return found;
}

bool AmlResultLogic::checkValidSize1(std::vector<std::string> cliData){
    int len = cliData[0].length();
    if(cliData[0] == "resetServer"){
        return true;
    }
    else if((len + 1)%3 == 0){
        for(int i = 2; i < (len-1); i += 3){
            if(cliData[0][i] != '_'){
                return false;
            }
        }
        return true;
    }
    return false;
}

bool AmlResultLogic::checkValidSize2(std::vector<std::string> cliData){
    std::string country = cliData[0].substr(0,2);
    for(int i = 0; i < numberTotalCountries; i++){
        if(allCountries[i] == country){
            return true;
        }
    }
    return false;
}

bool AmlResultLogic::checkValidSize5(std::vector<std::string> cliData){
    std::string country = cliData[0].substr(0,2);

    bool valid1 = false;
    for(int i = 0; i < numberTotalCountries; i++){
        if(allCountries[i] == country){
            valid1 = true;
            break;
        }
    }
    country = cliData[1].substr(0,2);
    bool valid2 = false;
    for(int j = 0; j < numberTotalCountries; j++){
        if(allCountries[j] == country){
            valid2 = true;
            break;
        }
    }
    return valid1 && valid2;
}


std::string AmlResultLogic::executeWorkOrder(std::string str_in)
{
    std::vector<std::string> data_stakes = splot(str_in, '|');
    for(std::string& s: data_stakes){

        std::vector<std::string> cliData = splot(s, ',');

        if(cliData.size() == 1) {
            if (checkValidSize1(cliData)){
                if(cliData[0] == "resetServer" && clientInit){
                    allCountries = splot(participatingCountries, '_');
                    numberTotalCountries = allCountries.size();
                    loadedCountries.clear();
                    loadedCountries.resize(numberTotalCountries, "");
                    infoPerCountry.clear();
                    infoPerCountry.resize(numberTotalCountries);
                    for(int i = 0; i < numberTotalCountries; i++){
                        infoPerCountry[i].maxClients = 4;
                        infoPerCountry[i].maxTransactions = 4;
                        infoPerCountry[i].actClients = 0;
                        infoPerCountry[i].actTransactions = 0;
                        infoPerCountry[i].clientList.resize(infoPerCountry[i].maxClients);
                        infoPerCountry[i].transactionList.resize(infoPerCountry[i].maxTransactions);
                    }
                }
                else if (!clientInit){
                    participatingCountries = cliData[0];
                    allCountries = splot(cliData[0], '_');
                    numberTotalCountries = allCountries.size();
                    loadedCountries.resize(numberTotalCountries, "");
                    infoPerCountry.resize(numberTotalCountries);
                    for(int i = 0; i < numberTotalCountries; i++){
                        infoPerCountry[i].maxClients = 4;
                        infoPerCountry[i].maxTransactions = 4;
                        infoPerCountry[i].actClients = 0;
                        infoPerCountry[i].actTransactions = 0;
                        infoPerCountry[i].clientList.resize(infoPerCountry[i].maxClients);
                        infoPerCountry[i].transactionList.resize(infoPerCountry[i].maxTransactions);
                    }
                    clientInit = true;
                }
            }
        }
        else if(cliData.size() == 2) {
            if(checkValidSize2(cliData)){
                std::string country = cliData[0].substr(0,2);
                int i;
                for(i = 0; i < numberTotalCountries; i++){
                    if(allCountries[i] == country){
                        break;
                    }
                }

                if(infoPerCountry[i].actClients == infoPerCountry[i].maxClients){
                    infoPerCountry[i].maxClients *= 2;
                    infoPerCountry[i].clientList.resize(infoPerCountry[i].maxClients);
                }
                infoPerCountry[i].clientList[infoPerCountry[i].actClients].clientId = cliData[0];
                infoPerCountry[i].clientList[infoPerCountry[i].actClients].fullName = cliData[1];
                infoPerCountry[i].actClients++;
            }
        }
        else if(cliData.size() == 5) {
            if(checkValidSize5(cliData)){
                std::vector<std::string> money =  splot(cliData[2], '.');
                std::string country = cliData[0].substr(0,2);
                int i;
                for(i = 0; i < numberTotalCountries; i++){
                    if(allCountries[i] == country){
                        loadedCountries[i] = country;
                        break;
                    }
                }
                if(infoPerCountry[i].actTransactions == infoPerCountry[i].maxTransactions){
                    infoPerCountry[i].maxTransactions *= 2;
                    infoPerCountry[i].transactionList.resize(infoPerCountry[i].maxTransactions);
                }

                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].from = cliData[0];
                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].to = cliData[1];
                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].amount = std::stoi(money[0]);
                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].fraction = std::stoi(money[1]);
                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].currency = cliData[3];
                infoPerCountry[i].transactionList[infoPerCountry[i].actTransactions].date = cliData[4];
                infoPerCountry[i].actTransactions++;
            }   
        }

        int alreadyLoaded = 0;
        for(int j = 0; j < numberTotalCountries; j++){
            if(infoPerCountry[j].actTransactions > 0){
                alreadyLoaded++;
            }
        }

        if (alreadyLoaded == numberTotalCountries) {
            return findSuspects();
        }
        else {
            std::string whichCountries = "Countries loaded: ";
            for(int i = 0; i < numberTotalCountries; i++){
                if(loadedCountries[i] != ""){
                    whichCountries = whichCountries + loadedCountries[i] + ",";
                }
            }
            return whichCountries;
        }
    }
}
