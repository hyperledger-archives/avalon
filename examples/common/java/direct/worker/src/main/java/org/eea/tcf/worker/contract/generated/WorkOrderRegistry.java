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

import io.reactivex.Flowable;
import io.reactivex.functions.Function;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.Callable;
import org.web3j.abi.EventEncoder;
import org.web3j.abi.TypeReference;
import org.web3j.abi.datatypes.Address;
import org.web3j.abi.datatypes.Event;
import org.web3j.abi.datatypes.Type;
import org.web3j.abi.datatypes.Utf8String;
import org.web3j.abi.datatypes.generated.Bytes32;
import org.web3j.abi.datatypes.generated.Uint256;
import org.web3j.crypto.Credentials;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.response.Log;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.tuples.generated.Tuple7;
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
public class WorkOrderRegistry extends Contract {
    private static final String BINARY = "0x608060405234801561001057600080fd5b50610b0b806100206000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c8063224b269a1461004657806336e30f1a146101915780633714b6c4146102c1575b600080fd5b61017f6004803603608081101561005c57600080fd5b81359160208101359181019060608101604082013564010000000081111561008357600080fd5b82018360208201111561009557600080fd5b803590602001918460018302840111640100000000831117156100b757600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600092019190915250929594936020810193503591505064010000000081111561010a57600080fd5b82018360208201111561011c57600080fd5b8035906020019184600183028401116401000000008311171561013e57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600092019190915250929550610381945050505050565b60408051918252519081900360200190f35b6101ae600480360360208110156101a757600080fd5b50356104e6565b6040518088815260200187815260200186815260200180602001856001600160a01b03166001600160a01b0316815260200184815260200180602001838103835287818151815260200191508051906020019080838360005b8381101561021f578181015183820152602001610207565b50505050905090810190601f16801561024c5780820380516001836020036101000a031916815260200191505b50838103825284518152845160209182019186019080838360005b8381101561027f578181015183820152602001610267565b50505050905090810190601f1680156102ac5780820380516001836020036101000a031916815260200191505b50995050505050505050505060405180910390f35b61017f600480360360a08110156102d757600080fd5b8135916020810135918101906060810160408201356401000000008111156102fe57600080fd5b82018360208201111561031057600080fd5b8035906020019184600183028401116401000000008311171561033257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600092019190915250929550506001600160a01b038335169350505060200135610667565b600084815260208190526040812060018154146103dc576040805162461bcd60e51b81526020600482015260146024820152731ddbcb585b1c9958591e4b5cdd589b5a5d1d195960621b604482015290519081900360640190fd5b6104838160040160009054906101000a90046001600160a01b031661047d8888886040516020018084815260200183815260200182805190602001908083835b6020831061043b5780518252601f19909201916020918201910161041c565b6001836020036101000a03801982511681845116808217855250505050505090500193505050506040516020818303038152906040528051906020012061080a565b8561085b565b61048c57600080fd5b600281556005810185905583516104ac9060068301906020870190610a3b565b50604051859087907f6b5ce7af51e6b46c050cbfae111000002e51e62610bbf69c6d5c59ded6fa1c2890600090a350600095945050505050565b6000818152602081815260408083208054600180830154600280850154600486015460058701546003880180548a51601f600019998316156101000299909901909116959095049687018b90048b0285018b019099528584528a998a996060998b998a998c99919891979693956001600160a01b03909416946006909301928691908301828280156105b95780601f1061058e576101008083540402835291602001916105b9565b820191906000526020600020905b81548152906001019060200180831161059c57829003601f168201915b5050845460408051602060026001851615610100026000190190941693909304601f8101849004840282018401909252818152959950869450925084019050828280156106475780601f1061061c57610100808354040283529160200191610647565b820191906000526020600020905b81548152906001019060200180831161062a57829003601f168201915b505050505090509650965096509650965096509650919395979092949650565b60008086868686866040516020018086815260200185815260200180602001846001600160a01b03166001600160a01b03168152602001838152602001828103825285818151815260200191508051906020019080838360005b838110156106d95781810151838201526020016106c1565b50505050905090810190601f1680156107065780820380516001836020036101000a031916815260200191505b5060408051601f1981840301815291815281516020928301206000818152928390529082209099509750955061073d945050505050565b815414610788576040805162461bcd60e51b81526020600482015260146024820152731ddbcb585b1c9958591e4b5cdd589b5a5d1d195960621b604482015290519081900360640190fd5b60018155600181018890556002810187905585516107af9060038301906020890190610a3b565b506004810180546001600160a01b0319166001600160a01b0387161790556040518790899084907fbd5c6340fc472cf6c189199cce4ef4e0dba09752d406232d46632f9f0d65a13e90600090a4506000979650505050505050565b604080517f19457468657265756d205369676e6564204d6573736167653a0a333200000000602080830191909152603c8083019490945282518083039094018452605c909101909152815191012090565b6000610868848484610954565b8061094a575060408051630b135d3f60e11b815260048101858152602482019283528451604483015284516001600160a01b03881693631626ba7e938893889390929160640190602085019080838360005b838110156108d25781810151838201526020016108ba565b50505050905090810190601f1680156108ff5780820380516001836020036101000a031916815260200191505b50935050505060206040518083038186803b15801561091d57600080fd5b505afa158015610931573d6000803e3d6000fd5b505050506040513d602081101561094757600080fd5b50515b90505b9392505050565b600080600080845160411461096f576000935050505061094d565b50505060208201516040830151606084015160001a601b81101561099157601b015b8060ff16601b141580156109a957508060ff16601c14155b156109ba576000935050505061094d565b6040805160008152602080820180845289905260ff8416828401526060820186905260808201859052915160019260a0808401939192601f1981019281900390910190855afa158015610a11573d6000803e3d6000fd5b505050602060405103516001600160a01b0316876001600160a01b03161493505050509392505050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f10610a7c57805160ff1916838001178555610aa9565b82800160010185558215610aa9579182015b82811115610aa9578251825591602001919060010190610a8e565b50610ab5929150610ab9565b5090565b610ad391905b80821115610ab55760008155600101610abf565b9056fea265627a7a723058208a2af1653f44a9047f6f3d3c5bbfd629d32b5063b09bb34db3637194fe8e66d064736f6c634300050a0032";

    public static final String FUNC_WORKORDERSUBMIT = "workOrderSubmit";

    public static final String FUNC_WORKORDERCOMPLETE = "workOrderComplete";

    public static final String FUNC_WORKORDERGET = "workOrderGet";

    public static final Event WORKORDERSUBMITTED_EVENT = new Event("workOrderSubmitted", 
            Arrays.<TypeReference<?>>asList(new TypeReference<Bytes32>(true) {}, new TypeReference<Bytes32>(true) {}, new TypeReference<Bytes32>(true) {}));
    ;

    public static final Event WORKORDERCOMPLETED_EVENT = new Event("workOrderCompleted", 
            Arrays.<TypeReference<?>>asList(new TypeReference<Bytes32>(true) {}, new TypeReference<Uint256>(true) {}));
    ;

    protected static final HashMap<String, String> _addresses;

    static {
        _addresses = new HashMap<String, String>();
    }

    @Deprecated
    protected WorkOrderRegistry(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected WorkOrderRegistry(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected WorkOrderRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected WorkOrderRegistry(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public List<WorkOrderSubmittedEventResponse> getWorkOrderSubmittedEvents(TransactionReceipt transactionReceipt) {
        List<Contract.EventValuesWithLog> valueList = extractEventParametersWithLog(WORKORDERSUBMITTED_EVENT, transactionReceipt);
        ArrayList<WorkOrderSubmittedEventResponse> responses = new ArrayList<WorkOrderSubmittedEventResponse>(valueList.size());
        for (Contract.EventValuesWithLog eventValues : valueList) {
            WorkOrderSubmittedEventResponse typedResponse = new WorkOrderSubmittedEventResponse();
            typedResponse.log = eventValues.getLog();
            typedResponse.workOrderID = (byte[]) eventValues.getIndexedValues().get(0).getValue();
            typedResponse.workerID = (byte[]) eventValues.getIndexedValues().get(1).getValue();
            typedResponse.requesterID = (byte[]) eventValues.getIndexedValues().get(2).getValue();
            responses.add(typedResponse);
        }
        return responses;
    }

    public Flowable<WorkOrderSubmittedEventResponse> workOrderSubmittedEventFlowable(EthFilter filter) {
        return web3j.ethLogFlowable(filter).map(new Function<Log, WorkOrderSubmittedEventResponse>() {
            @Override
            public WorkOrderSubmittedEventResponse apply(Log log) {
                Contract.EventValuesWithLog eventValues = extractEventParametersWithLog(WORKORDERSUBMITTED_EVENT, log);
                WorkOrderSubmittedEventResponse typedResponse = new WorkOrderSubmittedEventResponse();
                typedResponse.log = log;
                typedResponse.workOrderID = (byte[]) eventValues.getIndexedValues().get(0).getValue();
                typedResponse.workerID = (byte[]) eventValues.getIndexedValues().get(1).getValue();
                typedResponse.requesterID = (byte[]) eventValues.getIndexedValues().get(2).getValue();
                return typedResponse;
            }
        });
    }

    public Flowable<WorkOrderSubmittedEventResponse> workOrderSubmittedEventFlowable(DefaultBlockParameter startBlock, DefaultBlockParameter endBlock) {
        EthFilter filter = new EthFilter(startBlock, endBlock, getContractAddress());
        filter.addSingleTopic(EventEncoder.encode(WORKORDERSUBMITTED_EVENT));
        return workOrderSubmittedEventFlowable(filter);
    }

    public List<WorkOrderCompletedEventResponse> getWorkOrderCompletedEvents(TransactionReceipt transactionReceipt) {
        List<Contract.EventValuesWithLog> valueList = extractEventParametersWithLog(WORKORDERCOMPLETED_EVENT, transactionReceipt);
        ArrayList<WorkOrderCompletedEventResponse> responses = new ArrayList<WorkOrderCompletedEventResponse>(valueList.size());
        for (Contract.EventValuesWithLog eventValues : valueList) {
            WorkOrderCompletedEventResponse typedResponse = new WorkOrderCompletedEventResponse();
            typedResponse.log = eventValues.getLog();
            typedResponse.workOrderID = (byte[]) eventValues.getIndexedValues().get(0).getValue();
            typedResponse.workOrderReturnCode = (BigInteger) eventValues.getIndexedValues().get(1).getValue();
            responses.add(typedResponse);
        }
        return responses;
    }

    public Flowable<WorkOrderCompletedEventResponse> workOrderCompletedEventFlowable(EthFilter filter) {
        return web3j.ethLogFlowable(filter).map(new Function<Log, WorkOrderCompletedEventResponse>() {
            @Override
            public WorkOrderCompletedEventResponse apply(Log log) {
                Contract.EventValuesWithLog eventValues = extractEventParametersWithLog(WORKORDERCOMPLETED_EVENT, log);
                WorkOrderCompletedEventResponse typedResponse = new WorkOrderCompletedEventResponse();
                typedResponse.log = log;
                typedResponse.workOrderID = (byte[]) eventValues.getIndexedValues().get(0).getValue();
                typedResponse.workOrderReturnCode = (BigInteger) eventValues.getIndexedValues().get(1).getValue();
                return typedResponse;
            }
        });
    }

    public Flowable<WorkOrderCompletedEventResponse> workOrderCompletedEventFlowable(DefaultBlockParameter startBlock, DefaultBlockParameter endBlock) {
        EthFilter filter = new EthFilter(startBlock, endBlock, getContractAddress());
        filter.addSingleTopic(EventEncoder.encode(WORKORDERCOMPLETED_EVENT));
        return workOrderCompletedEventFlowable(filter);
    }

    public RemoteCall<TransactionReceipt> workOrderSubmit(byte[] _workerID, byte[] _requesterID, String _workOrderRequest, String _verifier, byte[] _salt) {
        final org.web3j.abi.datatypes.Function function = new org.web3j.abi.datatypes.Function(
                FUNC_WORKORDERSUBMIT, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(_workerID), 
                new org.web3j.abi.datatypes.generated.Bytes32(_requesterID), 
                new org.web3j.abi.datatypes.Utf8String(_workOrderRequest), 
                new org.web3j.abi.datatypes.Address(_verifier), 
                new org.web3j.abi.datatypes.generated.Bytes32(_salt)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<TransactionReceipt> workOrderComplete(byte[] _workOrderID, BigInteger _workOrderReturnCode, String _workOrderResponse, byte[] _workOrderSignature) {
        final org.web3j.abi.datatypes.Function function = new org.web3j.abi.datatypes.Function(
                FUNC_WORKORDERCOMPLETE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(_workOrderID), 
                new org.web3j.abi.datatypes.generated.Uint256(_workOrderReturnCode), 
                new org.web3j.abi.datatypes.Utf8String(_workOrderResponse), 
                new org.web3j.abi.datatypes.DynamicBytes(_workOrderSignature)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<Tuple7<BigInteger, byte[], byte[], String, String, BigInteger, String>> workOrderGet(byte[] _workOrderID) {
        final org.web3j.abi.datatypes.Function function = new org.web3j.abi.datatypes.Function(FUNC_WORKORDERGET, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(_workOrderID)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Uint256>() {}, new TypeReference<Bytes32>() {}, new TypeReference<Bytes32>() {}, new TypeReference<Utf8String>() {}, new TypeReference<Address>() {}, new TypeReference<Uint256>() {}, new TypeReference<Utf8String>() {}));
        return new RemoteCall<Tuple7<BigInteger, byte[], byte[], String, String, BigInteger, String>>(
                new Callable<Tuple7<BigInteger, byte[], byte[], String, String, BigInteger, String>>() {
                    @Override
                    public Tuple7<BigInteger, byte[], byte[], String, String, BigInteger, String> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple7<BigInteger, byte[], byte[], String, String, BigInteger, String>(
                                (BigInteger) results.get(0).getValue(), 
                                (byte[]) results.get(1).getValue(), 
                                (byte[]) results.get(2).getValue(), 
                                (String) results.get(3).getValue(), 
                                (String) results.get(4).getValue(), 
                                (BigInteger) results.get(5).getValue(), 
                                (String) results.get(6).getValue());
                    }
                });
    }

    @Deprecated
    public static WorkOrderRegistry load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkOrderRegistry(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static WorkOrderRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkOrderRegistry(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static WorkOrderRegistry load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new WorkOrderRegistry(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static WorkOrderRegistry load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new WorkOrderRegistry(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static RemoteCall<WorkOrderRegistry> deploy(Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkOrderRegistry.class, web3j, credentials, contractGasProvider, BINARY, "");
    }

    public static RemoteCall<WorkOrderRegistry> deploy(Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkOrderRegistry.class, web3j, transactionManager, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkOrderRegistry> deploy(Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkOrderRegistry.class, web3j, credentials, gasPrice, gasLimit, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkOrderRegistry> deploy(Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkOrderRegistry.class, web3j, transactionManager, gasPrice, gasLimit, BINARY, "");
    }

    protected String getStaticDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static String getPreviouslyDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static class WorkOrderSubmittedEventResponse {
        public Log log;

        public byte[] workOrderID;

        public byte[] workerID;

        public byte[] requesterID;
    }

    public static class WorkOrderCompletedEventResponse {
        public Log log;

        public byte[] workOrderID;

        public BigInteger workOrderReturnCode;
    }
}
