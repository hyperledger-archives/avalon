<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# EEA Token Execution Example Hyperledger Avalon Application

The EEA Token Execution application demonstrates running
EEA execution logic based on token requests.
See also
https://github.com/EntEthAlliance/Trusted-Token token_validation.cpp

This application is for execution on the SCONE platform.
For other Intel SGX frameworks, please directly call the method
`string token_valid_procedure(string input)` in `execution_logic.cpp`.

## Input Format

- Issue/burn tokens input format

  `issue_burn_tokens[]: [org_ID, [member_employee_ID, requested_EEA_activity, activity_realized]]`

- Redeem tokens input format

  `redeem[]:[org_ID, redeem_token_number]`

- Share tokens input format

  `share[]: [ord_ID, share_to_amount[share_token_number, share_to]]`

## Input Example

```
issue_burn_tokens[]:[{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741368,{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741361,3,true},{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741364,2,true},{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741364,3,true}},{did:ethr:111d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741301,{did:ethr:111d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb841311,3,true},{did:ethr:111d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb841312,2,false}}]

redeem[]:[{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741368,100},{did:ethr:111d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741301,90}]

share[]:[{did:ethr:8a5d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741368,{100, did:ethr:aaad93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741301},{200, did:ethr:bbbd93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741301}},{did:ethr:111d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb741301,{400, did:ethr:222d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb841301},{500, did:ethr:333d93cc5613ab0ace80a282029ff721923325ce276db5cadcb62537bb841301}}]
```

## Output Format

- `request_type`
  This line is a type number:
  1 for issue/burn tokens, 2 for redeem tokens, and  3 for share
- `return_code`
  This line is the application return number:
  return 0 for Success or another code for failure
  (see details in doc or `execution_logic.h`)
- `request_result`
  This is the request result: 2 lines are used for Issue/burn request and
  1 line is used for the redeem and share request

## Output Examples

These examples are based on the above input data.

### Issue/burn Tokens Result

```
1
0
did:ethr:8a5d9...68||105, did:ethr:8a5d9...60||95
did:ethr:8a5d9...61||100, did:ethr:8a5d9...64||105, did:ethr:111d9...11||100, did:ethr:111d9...12||-5
```

- Line 1 is the request type (issue/burn tokens)
- Line 2 is the return code (success)
- Line 3 is the issue/burn token
- Line 4 is the issue/burn individual reputation

### Redeem Rokens Result

```
2
0
did:ethr:8a5d9...68||100, did:ethr:111d9...01||90
```

### Share Tokens Result

```
3
0
did:ethr:8a5d9...68||100||did:ethr:aaad9...01, did:ethr:8a5d9...68||200||did:ethr:bbbd9...01, did:ethr:111d9...01||400||did:ethr:222d9...01, did:ethr:111d9...01||500||did:ethr:333d9...01
```

**NOTE:** This output format has to be converted to conform with the
smart contract API
(i.e., feed to onchain smart contracts).
Please check https://github.com/EntEthAlliance/Trusted-Token
