/* Copyright 2019 iExec Blockchain Tech
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

#include <iostream>
#include <algorithm>
#include <sstream>
#include <vector>
#include "execution_logic.h"

using namespace std;

/* Helper methods
*
*  helper methods for string operations
*/

vector<string> splitString (string input, string delimiter)
{
    vector<string> outputs;
    size_t pos = 0;
    string token;
    while ((pos = input.find(delimiter)) != string::npos) {
        outputs.push_back(input.substr(0, pos));
        input.erase(0, pos + delimiter.length());
    }
    outputs.push_back(input);
    return outputs;
}

bool stringConversion (string input, int& output)
{
    stringstream convertor;
    convertor << input;
    convertor >> output;
    if(convertor.fail()) {
        return false;
    }
    return true;
}

bool stringConversion (string input, bool& output)
{
    transform(input.begin(), input.end(), input.begin(),::tolower);
    if((input.compare("true") == 0) || (input.compare("false") == 0)
        || (input.compare("1") == 0) || (input.compare("0") == 0)) {
        if ((input.compare("true") == 0) || (input.compare("1") == 0)) {
            output = true;
        }
        else {
            output = false;
        }
        return true;
    }

    return false;
}


// std::to_string is not supported for some C++ compiler

string toString(int number)
{
    std::stringstream ss;
    ss << number;
    return ss.str();    
}

/* get_issue_burn_tokens_number
*
*  Issue/Burn tokens based on business rules
*/

int get_issue_burn_tokens_number (int activityType, bool realized)
{
    int token = 0;
    switch(activityType) {
        case ACTIVITY_PARTICIPATION_MEETING:
            token = 10;
            break;
        case ACTIVITY_CHAIR_MEETING:
            token = 5;
            break;
        case ACTIVITY_CONTRIBUTE_DELIVERABLE:
            token = 100;
            break;
        case ACTIVITY_EDITOR_DELIVERABLE:
            token = 200;
            break;
        case ACTIVITY_CONTRIBUTE_EEA_PROJECT_REGULAR:
            token = 1000;
            break;
        case ACTIVITY_CONTRIBUTE_EEA_PROJECT_MANAGER:
            token = 2000;
            break;
        case ACTIVITY_CONTRIBUTE_EEA_PROJECT_SPONSOR:
            token = 10000;
            break;
        }
    if (!realized) {
        token = -token;
    }
    return token;
}

void removeBrackets(string& str)
{
    str.erase(remove(str.begin(), str.end(), '{'), str.end());
    str.erase(remove(str.begin(), str.end(), '}'), str.end());
    str.erase(remove(str.begin(), str.end(), '['), str.end());
    str.erase(remove(str.begin(), str.end(), ']'), str.end());
}

/* issue_burn_tokens
*
*  Execution logic for issue/burn tokens
*
*  Return: string on results of issue/burn token
*
*  and individual reputation
*/

string issue_burn_tokens (string input)
{
    int RETURN_CODE = 0;
    string resultString;
    vector<issue_burn_token> issue_burn_v;
    vector<individual_reputation> individual_reputation_v;
    // remove header 'issue_burn_tokens[]:'
    input.erase(0, 20);
    // split the string by '}},', get a list of org activity
    vector<string> orgActivities = splitString(input, "}},");
    unsigned int orgActivitiesLen = orgActivities.size();
    for (unsigned int i = 0; i < orgActivitiesLen; ++i) {
        // per organisation ID activities
        /* remove the chars '{','}','[', ']'*/
        string orgActivity = orgActivities[i];
        removeBrackets(orgActivity);
        vector<string> sub_strings = splitString(orgActivity, ",");
        unsigned int sub_strings_len = sub_strings.size();
        if ((sub_strings_len - 1) % 3 != 0) {
            RETURN_CODE = ERROR_ISSUE_BURN_TOKENS;
            break;
        }
        issue_burn_token issue_burn;
        issue_burn.name = sub_strings[0];
        issue_burn.number = 0;
        int activityArray[8] = {0};
        // employeeID/activity/realized loop
        for (unsigned int j = 1; j < sub_strings_len;) {
            string employeeId = sub_strings[j++];
            int activityType;
            bool activityRealized;
            if (stringConversion(sub_strings[j++], activityType)
                && (stringConversion(sub_strings[j++], activityRealized))) {
                int issue_burn_tokens_number = get_issue_burn_tokens_number(activityType, activityRealized);
                // calculate the issue_burn token number if this activity have not been checked
                if (activityArray[activityType] != 1) {
                    issue_burn.number += issue_burn_tokens_number;
                    activityArray[activityType] = 1;
                }
                // accumulate individuals reputation
                unsigned int k;
                for (k = 0; k < individual_reputation_v.size(); ++k) {
                    if (employeeId.compare(individual_reputation_v[k].name) == 0) {
                        individual_reputation_v[k].number += issue_burn_tokens_number;
                        break;
                    }
                }
                if (k == individual_reputation_v.size()) {
                    individual_reputation rep = {employeeId, issue_burn_tokens_number};
                    individual_reputation_v.push_back(rep);
                }
            }
            else {
                RETURN_CODE = ERROR_ISSUE_BURN_TOKENS;
                break;
            }
        }
        if (RETURN_CODE != 0)
            break;
        issue_burn_v.push_back(issue_burn);
    }

    // prepare result for issue_burn_token
    string issue_burn_token_str = "";
    for (unsigned int i = 0; i < issue_burn_v.size(); ++i) {
        string separate = "";
        if (i < issue_burn_v.size() - 1)
            separate = ",";
        issue_burn_token_str = issue_burn_token_str + issue_burn_v[i].name + "||" + toString(issue_burn_v[i].number) + separate;
    }
    // prepare result for individual_reputation
    string individual_reputation_str = "";
    for (unsigned int i = 0; i < individual_reputation_v.size(); ++i) {
        string separate = "";
        if (i < individual_reputation_v.size() - 1)
            separate = ",";
        individual_reputation_str = individual_reputation_str + individual_reputation_v[i].name + "||" + toString(individual_reputation_v[i].number) + separate;
    }
    resultString = toString(TYPE_ISSUE_BURN_TOKEN) + "\n"
                   + toString(RETURN_CODE) + "\n"
                   + issue_burn_token_str + "\n"
                   + individual_reputation_str;
    return resultString;
}

/* redeem_tokens
*
*  Execution logic to redeem tokens
*
*  Return: string on results of redeem token
*
*/

string redeem_tokens (string input)
{
    int RETURN_CODE = 0;
    string resultString;
    vector<redeem_token> redeem_token_v;
    // remove header 'redeem[]:'
    input.erase(0, 9);
    /* remove the brackets '{','}','[', ']'*/
    removeBrackets(input);
    vector<string> sub_strings = splitString(input, ",");
    unsigned int sub_strings_len = sub_strings.size();
    if (sub_strings_len % 2 == 0) {
        for (unsigned int i = 0; i < sub_strings_len;) {
            string redeemName = sub_strings[i++];
            int redeemNumber;
            if (stringConversion(sub_strings[i++], redeemNumber)) {
                redeem_token redeem = {redeemName, redeemNumber};
                redeem_token_v.push_back(redeem);
            }
            else {
                RETURN_CODE = ERROR_SHARE_TOKENS;
                break;
            }
        }
    }
    else {
        RETURN_CODE = ERROR_REDEEM_TOKENS;
    }

    // prepare result for redeem_tokens
    string redeem_tokens_str = "";
    for (unsigned int i = 0; i < redeem_token_v.size(); ++i) {
        string separate = "";
        if (i < redeem_token_v.size() - 1)
            separate = ",";
        redeem_tokens_str = redeem_tokens_str + redeem_token_v[i].name + "||" 
                           + toString(redeem_token_v[i].number) + separate;
    }
    resultString = toString(TYPE_REDEEM_TOKEN) + "\n"
                   + toString(RETURN_CODE) + "\n"
                   + redeem_tokens_str;
    return resultString;
}

/* share_tokens
*
*  Execution logic to share tokens
*
*  Return: string on results of share token
*
*/

string share_tokens (string input)
{
    int RETURN_CODE = 0;
    string resultString;
    vector<share_token> share_token_v;
    // remove header 'share[]:'
    input.erase(0, 8);
    // split the string by '}},', get a list of org activity
    vector<string> shareTokens = splitString(input, "}},");
    unsigned int shareTokensLen = shareTokens.size();
    for (unsigned int i = 0; i < shareTokensLen; ++i) {
        // per organisation ID activities
        /* remove the chars '{','}','[', ']'*/
        string shareToken = shareTokens[i];
        removeBrackets(shareToken);
        vector<string> sub_strings = splitString(shareToken, ",");
        unsigned int sub_strings_len = sub_strings.size();
        if ((sub_strings_len - 1) % 2 != 0) {
            RETURN_CODE = ERROR_SHARE_TOKENS;
            break;
        }
        string shareFrom = sub_strings[0];
        // fill share number and share to
        for (unsigned int j = 1; j < sub_strings_len;) {
            int shareNumber;
            if (stringConversion(sub_strings[j++], shareNumber)) {
                share_token share = {shareFrom, shareNumber, sub_strings[j++]};
                share_token_v.push_back(share);
            }
            else {
                RETURN_CODE = ERROR_SHARE_TOKENS;
                break;
            }
        }
        if (RETURN_CODE != 0)
            break;
    }

    // prepare result for share_tokens
    string share_tokens_str = "";
    for (unsigned int i = 0; i < share_token_v.size(); ++i) {
        string separate = "";
        if (i < share_token_v.size() - 1)
            separate = ",";
        share_tokens_str = share_tokens_str + share_token_v[i].from + "||" 
                           + toString(share_token_v[i].number) + "||"
                           + share_token_v[i].to + separate;
    }
    resultString = toString(TYPE_SHARE_TOKEN) + "\n"
                   + toString(RETURN_CODE) + "\n"
                   + share_tokens_str;
    return resultString;
}

/* token_valid_procedure
*
*  proceed the token validation execution logic
*
*  return 0 (success) or other code (fail, see details in doc)
*/

string token_valid_procedure(string input)
{
    string result = "";

    /* remove space and \n */
    input.erase(remove(input.begin(), input.end(), '\n'), input.end());
    input.erase(remove(input.begin(), input.end(), ' '), input.end());

    //string sub_string("issue_burn_tokens");
    if (input.find("issue_burn_tokens[]:") == 0)
    {
        result = issue_burn_tokens(input);
    }
    else if (input.find("redeem[]:") == 0) {
        result = redeem_tokens(input);
    }
    else if (input.find("share[]:") == 0) {
        result = share_tokens(input);
    }
    else {
        result = toString(TYPE_UNKNOWN)+ "\n" + toString(ERROR_REQUEST_TYPE);
    }
    cout << result << endl;
    return result;
}

