#! /bin/bash

for f in ../TCF-contracts/build/contracts/*.json; do
	web3j truffle generate "$f" -o src/main/java/ -p org.eea.tcf.worker.contract.generated
done
