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
public class WorkerRegistry extends Contract {
    private static final String BINARY = "0x608060405234801561001057600080fd5b50610b89806100206000396000f3fe608060405234801561001057600080fd5b50600436106100625760003560e01c80632092b3d1146100675780636dc536271461008c5780637f6a1ae31461017557806383c17736146102ae578063b044138f14610359578063bb3fdd7114610410575b600080fd5b61008a6004803603604081101561007d57600080fd5b50803590602001356104ff565b005b6100b5600480360360608110156100a257600080fd5b5080359060208101359060400135610533565b604051808481526020018060200180602001838103835285818151815260200191508051906020019080838360005b838110156100fc5781810151838201526020016100e4565b50505050905090810190601f1680156101295780820380516001836020036101000a031916815260200191505b508381038252845181528451602091820191808701910280838360005b8381101561015e578181015183820152602001610146565b505050509050019550505050505060405180910390f35b61008a600480360360a081101561018b57600080fd5b81359160208101359160408201359190810190608081016060820135600160201b8111156101b857600080fd5b8201836020820111156101ca57600080fd5b803590602001918460208302840111600160201b831117156101eb57600080fd5b9190808060200260200160405190810160405280939291908181526020018383602002808284376000920191909152509295949360208101935035915050600160201b81111561023a57600080fd5b82018360208201111561024c57600080fd5b803590602001918460018302840111600160201b8311171561026d57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600092019190915250929550610562945050505050565b61008a600480360360408110156102c457600080fd5b81359190810190604081016020820135600160201b8111156102e557600080fd5b8201836020820111156102f757600080fd5b803590602001918460018302840111600160201b8311171561031857600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600092019190915250929550610888945050505050565b6100b56004803603608081101561036f57600080fd5b81359160208101359160408201359190810190608081016060820135600160201b81111561039c57600080fd5b8201836020820111156103ae57600080fd5b803590602001918460018302840111600160201b831117156103cf57600080fd5b91908080601f0160208091040260200160405190810160405280939291908181526020018383808284376000920191909152509295506108c8945050505050565b61042d6004803603602081101561042657600080fd5b5035610956565b604051808681526020018581526020018481526020018060200180602001838103835285818151815260200191508051906020019060200280838360005b8381101561048357818101518382015260200161046b565b50505050905001838103825284818151815260200191508051906020019080838360005b838110156104bf5781810151838201526020016104a7565b50505050905090810190601f1680156104ec5780820380516001836020036101000a031916815260200191505b5097505050505050505060405180910390f35b60008281526020819052604090205461051757600080fd5b8061052157600080fd5b60009182526020829052604090912055565b6000606080610553868686604051806020016040528060008152506108c8565b92509250925093509350939050565b600085815260208190526040902080541561057c57600080fd5b60018155600181018590556002810184905582516105a39060038301906020860190610a7f565b5081516105b99060048301906020850190610aca565b50846105c457600080fd5b836105ce57600080fd5b7fbe593d8b7f6ac28ac35d4114e04e958aef4d3972690d6be9b07e9713a462df02805460018181019092557ff33c1b862ffd3128ed890404e704ca37858bb36fa75966ca95d4335dcf48d50e01879055600086815260208281526040808320838052808352818420835281842080548087018255908552838520018b90558884527fa6eef7e35abe7026729641147f7915573c7e97b47efa546f5f6e3230263bcb498352818420848052835281842080548087018255908552838520018b905588845282528083208380528252822080549384018155825281209091018790555b835181101561087f576000801b8482815181106106c857fe5b602002602001015114156106db57600080fd5b60008080527fa6eef7e35abe7026729641147f7915573c7e97b47efa546f5f6e3230263bcb4960205284517fe5d06582d467054dda5404b9e1ec93f72b608a4970ba970773776c69ca5664f7919086908490811061073557fe5b60209081029190910181015182528181019290925260409081016000908120805460018181018355918352848320018b905589825283528181208180529092528120855190919086908490811061078857fe5b602090810291909101810151825281810192909252604090810160009081208054600181018255908252838220018a90558781527fa6eef7e35abe7026729641147f7915573c7e97b47efa546f5f6e3230263bcb49909252812085519091908690849081106107f357fe5b60209081029190910181015182528181019290925260409081016000908120805460018181018355918352848320018b905589825283528181208882529092528120855190919086908490811061084657fe5b602090810291909101810151825281810192909252604001600090812080546001818101835591835292909120909101889055016106af565b50505050505050565b6000828152602081905260409020546108a057600080fd5b60008281526020818152604090912082516108c392600490920191840190610aca565b505050565b600084815260016020908152604080832086845282528083208584528252808320805482518085018452858152835182860281018601909452818452606094859484918290859083018282801561093e57602002820191906000526020600020905b81548152602001906001019080831161092a575b50505050509050935093509350509450945094915050565b6000806000606080600080600088815260200190815260200160002090508060000154816001015482600201548360030184600401818054806020026020016040519081016040528092919081815260200182805480156109d657602002820191906000526020600020905b8154815260200190600101908083116109c2575b5050845460408051602060026001851615610100026000190190941693909304601f810184900484028201840190925281815295975086945092508401905082828015610a645780601f10610a3957610100808354040283529160200191610a64565b820191906000526020600020905b815481529060010190602001808311610a4757829003601f168201915b50505050509050955095509550955095505091939590929450565b828054828255906000526020600020908101928215610aba579160200282015b82811115610aba578251825591602001919060010190610a9f565b50610ac6929150610b37565b5090565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f10610b0b57805160ff1916838001178555610aba565b82800160010185558215610aba5791820182811115610aba578251825591602001919060010190610a9f565b610b5191905b80821115610ac65760008155600101610b3d565b9056fea265627a7a72305820b947ef3b74e5fcef23d73138b593dfb29558d4b2b181ae014d139447457bfe8964736f6c634300050a0032";

    public static final String FUNC_WORKERREGISTER = "workerRegister";

    public static final String FUNC_WORKERUPDATE = "workerUpdate";

    public static final String FUNC_WORKERSETSTATUS = "workerSetStatus";

    public static final String FUNC_WORKERLOOKUP = "workerLookUp";

    public static final String FUNC_WORKERLOOKUPNEXT = "workerLookUpNext";

    public static final String FUNC_WORKERRETRIEVE = "workerRetrieve";

    protected static final HashMap<String, String> _addresses;

    static {
        _addresses = new HashMap<String, String>();
        _addresses.put("1564389941067", "0x79ede703f6e4FFbb50a3b7798CfEBF792581E830");
    }

    @Deprecated
    protected WorkerRegistry(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected WorkerRegistry(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected WorkerRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected WorkerRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public RemoteCall<TransactionReceipt> workerRegister(byte[] workerID, BigInteger workerType, byte[] organizationId, List<byte[]> appTypeIds, String details) {
        final Function function = new Function(
                FUNC_WORKERREGISTER, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID), 
                new org.web3j.abi.datatypes.generated.Uint256(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.DynamicArray<org.web3j.abi.datatypes.generated.Bytes32>(
                        org.web3j.abi.datatypes.generated.Bytes32.class,
                        org.web3j.abi.Utils.typeMap(appTypeIds, org.web3j.abi.datatypes.generated.Bytes32.class)), 
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
                new org.web3j.abi.datatypes.generated.Uint256(status)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> workerLookUp(BigInteger workerType, byte[] organizationId, byte[] appTypeId) {
        final Function function = new Function(FUNC_WORKERLOOKUP, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Uint256(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.generated.Bytes32(appTypeId)), 
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

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> workerLookUpNext(BigInteger workerType, byte[] organizationId, byte[] appTypeId, String param3) {
        final Function function = new Function(FUNC_WORKERLOOKUPNEXT, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Uint256(workerType), 
                new org.web3j.abi.datatypes.generated.Bytes32(organizationId), 
                new org.web3j.abi.datatypes.generated.Bytes32(appTypeId), 
                new org.web3j.abi.datatypes.Utf8String(param3)), 
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

    public RemoteCall<Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String>> workerRetrieve(byte[] workerID) {
        final Function function = new Function(FUNC_WORKERRETRIEVE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(workerID)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Uint256>() {}, new TypeReference<Uint256>() {}, new TypeReference<Bytes32>() {}, new TypeReference<DynamicArray<Bytes32>>() {}, new TypeReference<Utf8String>() {}));
        return new RemoteCall<Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String>>(
                new Callable<Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String>>() {
                    @Override
                    public Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple5<BigInteger, BigInteger, byte[], List<byte[]>, String>(
                                (BigInteger) results.get(0).getValue(), 
                                (BigInteger) results.get(1).getValue(), 
                                (byte[]) results.get(2).getValue(), 
                                convertToNative((List<Bytes32>) results.get(3).getValue()), 
                                (String) results.get(4).getValue());
                    }
                });
    }

    @Deprecated
    public static WorkerRegistry load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkerRegistry(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static WorkerRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkerRegistry(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static WorkerRegistry load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new WorkerRegistry(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static WorkerRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new WorkerRegistry(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static RemoteCall<WorkerRegistry> deploy(Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkerRegistry.class, web3j, credentials, contractGasProvider, BINARY, "");
    }

    public static RemoteCall<WorkerRegistry> deploy(Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkerRegistry.class, web3j, transactionManager, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkerRegistry> deploy(Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkerRegistry.class, web3j, credentials, gasPrice, gasLimit, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkerRegistry> deploy(Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkerRegistry.class, web3j, transactionManager, gasPrice, gasLimit, BINARY, "");
    }

    protected String getStaticDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static String getPreviouslyDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }
}
