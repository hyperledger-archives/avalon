  /*****************************************************************************
  * Copyright 2019 iExec Blockchain Tech
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
  *****************************************************************************/
package org.eea.tcf.worker.chain.services;

import org.eea.tcf.worker.chain.model.ChainWorker;
import org.eea.tcf.worker.config.WorkerConfigurationService;
import lombok.extern.slf4j.Slf4j;
import org.eea.tcf.worker.contract.generated.WorkerRegistry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.web3j.ens.EnsResolutionException;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.tuples.generated.Tuple3;
import org.web3j.tuples.generated.Tuple5;
import org.web3j.tx.gas.ContractGasProvider;
import org.web3j.tx.gas.DefaultGasProvider;

import java.math.BigInteger;
import java.util.List;
import java.util.Optional;

import static org.eea.tcf.worker.utils.BytesUtils.*;

@Slf4j
@Service
public class WorkerRegistryService {

    private final CredentialsService credentialsService;
    private org.web3j.protocol.Web3jService web3jService;
    private final Web3j web3j;
    private final Web3jService web3JService;
    private final String registryAddress;

    @Autowired
    public WorkerRegistryService(CredentialsService credentialsService,
                                 Web3jService web3JService,
                                 WorkerConfigurationService workerConfigurationService) {
        this.credentialsService = credentialsService;
        this.web3j = web3JService.getWeb3j();
        this.web3JService = web3JService;
        this.registryAddress =  workerConfigurationService.getRegistryAddress();
    }

    public WorkerRegistry getWorkerRegistryContract(ContractGasProvider contractGasProvider) {
        ExceptionInInitializerError exceptionInInitializerError =
                new ExceptionInInitializerError("Failed to load WorkerRegistry contract from address "
                        + registryAddress);

        if (registryAddress != null && !registryAddress.isEmpty()) {
            try {
                return WorkerRegistry.load(
                        registryAddress, web3j,
                        credentialsService.getCredentials(),
                        contractGasProvider);
            } catch (EnsResolutionException e) {
                throw exceptionInInitializerError;
            }
        } else {
            throw exceptionInInitializerError;
        }
    }

    public WorkerRegistry getWorkerRegistryContract() {
        return getWorkerRegistryContract(new DefaultGasProvider());
    }

    public boolean workerRegister(ChainWorker worker) {
        return workerRegister(
                worker.getWorkerId(),
                worker.getType(),
                worker.getOrganizationId(),
                worker.getApplicationTypeId(),
                worker.getDetails()
        );
    }

    public boolean workerRegister(String workerId,
                                  ChainWorker.WorkerType workerType,
                                  String organizationId,
                                  String[] applicationTypeId,
                                  String details) {
        byte[] workerIdBytes = stringToBytes32(workerId);
        byte[] orgIdBytes = stringToBytes32(organizationId);
        List<byte[]> appTypeIdBytes = stringsToBytes32(applicationTypeId);

        TransactionReceipt registerReceipt;
        RemoteCall<TransactionReceipt> registerCall =
                getWorkerRegistryContract().workerRegister(
                workerIdBytes,
                BigInteger.valueOf(workerType.ordinal()),
                orgIdBytes,
                appTypeIdBytes,
                details);

        try {
            registerReceipt = registerCall.send();
            log.info("Registered [workerId:{}, workerType:{}, gasUsed:{}]",
                    workerId, workerType, registerReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to register [workerId:{}, exception:{}]",
                    workerId, e.getMessage());
        }

        return false;
    }

    public boolean workerUpdate(ChainWorker worker) {
        return workerUpdate(worker.getWorkerId(), worker.getDetails());
    }

    public boolean workerUpdate(String workerId, String details) {
        byte[] workerIdBytes = stringToBytes32(workerId);

        TransactionReceipt updateReceipt;
        RemoteCall<TransactionReceipt> updateCall =
                getWorkerRegistryContract().workerUpdate(
                workerIdBytes,
                details);

        try {
            updateReceipt = updateCall.send();
            log.info("Updated [workerId:{}, details:{}, gasUsed:{}]", workerId,
                    details, updateReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to update[workerId:{}, exception:{}]",
                    workerId, e.getMessage());
        }

        return false;
    }

    public boolean setStatus(ChainWorker worker) {
        return workerSetStatus(worker.getWorkerId(), worker.getStatus().ordinal());
    }

    public boolean workerSetStatus(String workerId, int status) {
        byte[] workerIdBytes = stringToBytes32(workerId);

        TransactionReceipt setStatusReceipt;
        RemoteCall<TransactionReceipt> setStatusCall = getWorkerRegistryContract().workerSetStatus(
                workerIdBytes,
                BigInteger.valueOf(status));

        try {
            setStatusReceipt = setStatusCall.send();
            log.info("Set status [workerId:{}, status:{}, gasUsed:{}]",
                    workerId, status, setStatusReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to setStatus[workerId:{}, exception:{}]", workerId, e.getMessage());
        }

        return false;
    }

    public String[] workerLookUp(int workerType, String organizationId, String appTypeId) {
        // TODO this ignores lookupTag
        byte[] orgIdBytes = stringToBytes32(organizationId);
        byte[] appTypeIdBytes = stringToBytes(appTypeId);

        Tuple3<BigInteger, String, List<byte[]>> lookupResult;
        RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> lookupCall =
                getWorkerRegistryContract().workerLookUp(
                BigInteger.valueOf(workerType),
                orgIdBytes,
                appTypeIdBytes);

        try {
            lookupResult = lookupCall.send();
            log.info("workerLookUp [workerType:{}, organizationId:{}, appTypeId{}, nbResults:{}/{}]",
                    workerType, organizationId, appTypeId,
                    lookupResult.getValue1(), lookupResult.getValue3().size());
        } catch (Exception e) {
            log.error("Failed to lookUpWorkers[workerType:{}, organizationId:{}, appTypeId:{}, exception:{}]",
                    workerType, organizationId, appTypeId, e.getMessage());
            return null;
        }

        return bytesToStrings(lookupResult.getValue3());
    }

    public String[] workerLookUpNext(int workerType, String organizationId,
                                     String appTypeId, String lookupTag) {
        byte[] orgIdBytes = stringToBytes32(organizationId);
        byte[] appTypeIdBytes = stringToBytes32(appTypeId);

        Tuple3<BigInteger, String, List<byte[]>> lookupResult;
        RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> lookupCall =
                getWorkerRegistryContract().workerLookUpNext(
                BigInteger.valueOf(workerType),
                orgIdBytes,
                appTypeIdBytes,
                lookupTag);

        try {
            lookupResult = lookupCall.send();
            log.info("workerLookUp [workerType:{}, organizationId:{}, appTypeId{}, nbResults:{}/{}]",
                    workerType, organizationId, appTypeId, lookupResult.getValue1(), lookupResult.getValue3().size());
        } catch (Exception e) {
            log.error("Failed to workerLookUp[workerType:{}, organizationId:{}, appTypeId:{}, exception:{}]",
                    workerType, organizationId, appTypeId, e.getMessage());
            return null;
        }

        return bytesToStrings(lookupResult.getValue3());
    }

    public Optional<ChainWorker> workerRetrieve(String workerId) {
        byte[] workerIdBytes = stringToBytes32(workerId);

        Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String> chainWorker;
        RemoteCall<Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String>>
                retrieveCall = getWorkerRegistryContract().workerRetrieve(workerIdBytes);

        try {
            chainWorker = retrieveCall.send();
        } catch (Exception e) {
            log.error("Failed to retrieve [workerId:{}, exception:{}]",
                    workerId, e.getMessage());
            return Optional.empty();
        }

        if(chainWorker.getValue1().equals(BigInteger.ZERO))
            return Optional.empty();

        return Optional.of(ChainWorker.fromTuple(workerId, chainWorker));
    }
}
