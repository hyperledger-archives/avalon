#!/bin/bash
#
# Copyright IBM Corp All Rights Reserved
#
# SPDX-License-Identifier: Apache-2.0
#

# This script extracts Avalon Fabric chaincode from Avalon github repository.
git init avalon && cd avalon
git remote add origin https://github.com/hyperledger/avalon
git config core.sparsecheckout true
echo "sdk/avalon_sdk/fabric/chaincode" >> .git/info/sparse-checkout
git pull --depth=1 origin master
sudo cp -r sdk/avalon_sdk/fabric/chaincode ../vars
cd .. && rm -rf avalon
./minifab install,approve,instantiate -n worker
./minifab install,approve,instantiate -n order
./minifab install,approve,instantiate -n receipt
./minifab install,approve,instantiate -n registry
