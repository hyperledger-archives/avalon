/*
*
* EEA Token Execution Logic
* Lei.zhang@iex.ec
* iExec Blockchain Tech
*
*/

#include <string.h>

std::string token_valid_procedure(std::string input);

#define TYPE_UNKNOWN                                0
#define TYPE_ISSUE_BURN_TOKEN                       1
#define TYPE_REDEEM_TOKEN                           2
#define TYPE_SHARE_TOKEN                            3
#define TYPE_REGISTRATION                           4

#define SUCCESS                                     0
#define ERROR_REQUEST_TYPE                          1
#define ERROR_ISSUE_BURN_TOKENS                     2
#define ERROR_REDEEM_TOKENS                         3
#define ERROR_SHARE_TOKENS                          4

#define ACTIVITY_PARTICIPATION_MEETING              1
#define ACTIVITY_CHAIR_MEETING                      2
#define ACTIVITY_CONTRIBUTE_DELIVERABLE             3
#define ACTIVITY_EDITOR_DELIVERABLE                 4
#define ACTIVITY_CONTRIBUTE_EEA_PROJECT_REGULAR     5
#define ACTIVITY_CONTRIBUTE_EEA_PROJECT_MANAGER     6
#define ACTIVITY_CONTRIBUTE_EEA_PROJECT_SPONSOR     7
#define ACTIVITY_NUMBER                             7

struct issue_burn_token
{
    std::string name;
    int number;
};

struct individual_reputation
{
    std::string name;
    int number;
};

struct redeem_token
{
    std::string name;
    int number;
};

struct share_token
{
    std::string from;
    int number;
    std::string to;
};