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
package org.eea.tcf.worker.contract.generated;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.Callable;
import org.web3j.abi.TypeReference;
import org.web3j.abi.datatypes.DynamicArray;
import org.web3j.abi.datatypes.Function;
import org.web3j.abi.datatypes.Type;
import org.web3j.abi.datatypes.Utf8String;
import org.web3j.abi.datatypes.generated.Bytes32;
import org.web3j.abi.datatypes.generated.Uint256;
import org.web3j.abi.datatypes.generated.Uint8;
import org.web3j.crypto.Credentials;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.tuples.generated.Tuple3;
import org.web3j.tuples.generated.Tuple5;
import org.web3j.tx.Contract;
import org.web3j.tx.TransactionManager;
import org.web3j.tx.gas.ContractGasProvider;

/**
 * <p>Auto generated code.
 * <p><strong>Do not modify!</strong>
 * <p>Please use the <a href="https://docs.web3j.io/command_line.html">web3j command line tools</a>,
 * or the org.web3j.codegen.SolidityFunctionWrapperGenerator in the 
 * <a href="https://github.com/web3j/web3j/tree/master/codegen">codegen module</a> to update.
 *
 * <p>Generated with web3j version 4.3.0.
 */
public class IWorkerRegistry extends Contract {
    private static final String BINARY = "0x";

    public static final String FUNC_WORKERREGISTER = "workerRegister";

    public static final String FUNC_WORKERUPDATE = "workerUpdate";

    public static final String FUNC_WORKERSETSTATUS = "workerSetStatus";

    public static final String FUNC_WORKERLOOKUP = "workerLookUp";

    public static final String FUNC_WORKERLOOKUPNEXT = "workerLookUpNext";

    public static final String FUNC_WORKERRETRIEVE = "workerRetrieve";

    protected static final HashMap<String, String> _addresses;

    static {
        _addresses = new HashMap<String, String>();
    }

    @Deprecated
    protected IWorkerRegistry(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected IWorkerRegistry(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected IWorkerRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected IWorkerRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public RemoteCall<TransactionReceipt> workerRegister(byte[] workerID, BigInteger workerType, byte[] organizationId, List<byte[]> applicationTypeId, String details) {
        final Function function = new Function(
                FUNC_WORKERREGISTER, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID), 
                new org.web3j.abi.datatypes.generated.Uint8(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.DynamicArray<org.web3j.abi.datatypes.generated.Bytes32>(
                        org.web3j.abi.datatypes.generated.Bytes32.class,
                        org.web3j.abi.Utils.typeMap(applicationTypeId, org.web3j.abi.datatypes.generated.Bytes32.class)), 
                new org.web3j.abi.datatypes.Utf8String(details)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<TransactionReceipt> workerUpdate(byte[] workerID, String details) {
        final Function function = new Function(
                FUNC_WORKERUPDATE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID), 
                new org.web3j.abi.datatypes.Utf8String(details)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<TransactionReceipt> workerSetStatus(byte[] workerID, BigInteger status) {
        final Function function = new Function(
                FUNC_WORKERSETSTATUS, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID), 
                new org.web3j.abi.datatypes.generated.Uint8(status)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> workerLookUp(BigInteger workerType, byte[] organizationId, byte[] applicationTypeId) {
        final Function function = new Function(FUNC_WORKERLOOKUP, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Uint8(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.generated.Bytes32(applicationTypeId)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Uint256>() {}, new TypeReference<Utf8String>() {}, new TypeReference<DynamicArray<Bytes32>>() {}));
        return new RemoteCall<Tuple3<BigInteger, String, List<byte[]>>>(
                new Callable<Tuple3<BigInteger, String, List<byte[]>>>() {
                    @Override
                    public Tuple3<BigInteger, String, List<byte[]>> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple3<BigInteger, String, List<byte[]>>(
                                (BigInteger) results.get(0).getValue(), 
                                (String) results.get(1).getValue(), 
                                convertToNative((List<Bytes32>) results.get(2).getValue()));
                    }
                });
    }

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> workerLookUpNext(BigInteger workerType, byte[] organizationId, byte[] applicationTypeId, String lookUpTag) {
        final Function function = new Function(FUNC_WORKERLOOKUPNEXT, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Uint8(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.generated.Bytes32(applicationTypeId), 
                new org.web3j.abi.datatypes.Utf8String(lookUpTag)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Uint256>() {}, new TypeReference<Utf8String>() {}, new TypeReference<DynamicArray<Bytes32>>() {}));
        return new RemoteCall<Tuple3<BigInteger, String, List<byte[]>>>(
                new Callable<Tuple3<BigInteger, String, List<byte[]>>>() {
                    @Override
                    public Tuple3<BigInteger, String, List<byte[]>> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple3<BigInteger, String, List<byte[]>>(
                                (BigInteger) results.get(0).getValue(), 
                                (String) results.get(1).getValue(), 
                                convertToNative((List<Bytes32>) results.get(2).getValue()));
                    }
                });
    }

    public RemoteCall<Tuple5<BigInteger, byte[], List<byte[]>, String, BigInteger>> workerRetrieve(byte[] workerID) {
        final Function function = new Function(FUNC_WORKERRETRIEVE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Uint8>() {}, new TypeReference<Bytes32>() {}, new TypeReference<DynamicArray<Bytes32>>() {}, new TypeReference<Utf8String>() {}, new TypeReference<Uint8>() {}));
        return new RemoteCall<Tuple5<BigInteger, byte[], List<byte[]>, String, BigInteger>>(
                new Callable<Tuple5<BigInteger, byte[], List<byte[]>, String, BigInteger>>() {
                    @Override
                    public Tuple5<BigInteger, byte[], List<byte[]>, String, BigInteger> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple5<BigInteger, byte[], List<byte[]>, String, BigInteger>(
                                (BigInteger) results.get(0).getValue(), 
                                (byte[]) results.get(1).getValue(), 
                                convertToNative((List<Bytes32>) results.get(2).getValue()), 
                                (String) results.get(3).getValue(), 
                                (BigInteger) results.get(4).getValue());
                    }
                });
    }

    @Deprecated
    public static IWorkerRegistry load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new IWorkerRegistry(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static IWorkerRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new IWorkerRegistry(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static IWorkerRegistry load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new IWorkerRegistry(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static IWorkerRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new IWorkerRegistry(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static RemoteCall<IWorkerRegistry> deploy(Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(IWorkerRegistry.class, web3j, credentials, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<IWorkerRegistry> deploy(Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(IWorkerRegistry.class, web3j, credentials, gasPrice, gasLimit, BINARY, "");
    }

    public static RemoteCall<IWorkerRegistry> deploy(Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(IWorkerRegistry.class, web3j, transactionManager, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<IWorkerRegistry> deploy(Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(IWorkerRegistry.class, web3j, transactionManager, gasPrice, gasLimit, BINARY, "");
    }

    protected String getStaticDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static String getPreviouslyDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }
}
