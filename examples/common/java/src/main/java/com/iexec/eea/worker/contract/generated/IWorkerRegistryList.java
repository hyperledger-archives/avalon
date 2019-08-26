package com.iexec.eea.worker.contract.generated;

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
import org.web3j.tuples.generated.Tuple4;
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
public class IWorkerRegistryList extends Contract {
    private static final String BINARY = "0x";

    public static final String FUNC_REGISTRYADD = "registryAdd";

    public static final String FUNC_REGISTRYUPDATE = "registryUpdate";

    public static final String FUNC_REGISTRYSETSTATUS = "registrySetStatus";

    public static final String FUNC_REGISTRYLOOKUP = "registryLookUp";

    public static final String FUNC_REGISTRYLOOKUPNEXT = "registryLookUpNext";

    public static final String FUNC_REGISTRYRETRIEVE = "registryRetrieve";

    protected static final HashMap<String, String> _addresses;

    static {
        _addresses = new HashMap<String, String>();
    }

    @Deprecated
    protected IWorkerRegistryList(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected IWorkerRegistryList(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected IWorkerRegistryList(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected IWorkerRegistryList(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public RemoteCall<TransactionReceipt> registryAdd(byte[] orgID, String uri, byte[] scAddr, List<byte[]> appTypeIds) {
        final Function function = new Function(
                FUNC_REGISTRYADD, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(orgID), 
                new org.web3j.abi.datatypes.Utf8String(uri), 
                new org.web3j.abi.datatypes.generated.Bytes32(scAddr), 
                new org.web3j.abi.datatypes.DynamicArray<org.web3j.abi.datatypes.generated.Bytes32>(
                        org.web3j.abi.datatypes.generated.Bytes32.class,
                        org.web3j.abi.Utils.typeMap(appTypeIds, org.web3j.abi.datatypes.generated.Bytes32.class))), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<TransactionReceipt> registryUpdate(byte[] orgID, String uri, byte[] scAddr, List<byte[]> appTypeIds) {
        final Function function = new Function(
                FUNC_REGISTRYUPDATE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(orgID), 
                new org.web3j.abi.datatypes.Utf8String(uri), 
                new org.web3j.abi.datatypes.generated.Bytes32(scAddr), 
                new org.web3j.abi.datatypes.DynamicArray<org.web3j.abi.datatypes.generated.Bytes32>(
                        org.web3j.abi.datatypes.generated.Bytes32.class,
                        org.web3j.abi.Utils.typeMap(appTypeIds, org.web3j.abi.datatypes.generated.Bytes32.class))), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<TransactionReceipt> registrySetStatus(byte[] orgID, BigInteger status) {
        final Function function = new Function(
                FUNC_REGISTRYSETSTATUS, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(orgID), 
                new org.web3j.abi.datatypes.generated.Uint8(status)), 
                Collections.<TypeReference<?>>emptyList());
        return executeRemoteCallTransaction(function);
    }

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> registryLookUp(byte[] appTypeId) {
        final Function function = new Function(FUNC_REGISTRYLOOKUP, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(appTypeId)), 
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

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> registryLookUpNext(byte[] applTypeId, String lookUpTag) {
        final Function function = new Function(FUNC_REGISTRYLOOKUPNEXT, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(applTypeId), 
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

    public RemoteCall<Tuple4<String, byte[], List<byte[]>, BigInteger>> registryRetrieve(byte[] orgID) {
        final Function function = new Function(FUNC_REGISTRYRETRIEVE, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(orgID)), 
                Arrays.<TypeReference<?>>asList(new TypeReference<Utf8String>() {}, new TypeReference<Bytes32>() {}, new TypeReference<DynamicArray<Bytes32>>() {}, new TypeReference<Uint8>() {}));
        return new RemoteCall<Tuple4<String, byte[], List<byte[]>, BigInteger>>(
                new Callable<Tuple4<String, byte[], List<byte[]>, BigInteger>>() {
                    @Override
                    public Tuple4<String, byte[], List<byte[]>, BigInteger> call() throws Exception {
                        List<Type> results = executeCallMultipleValueReturn(function);
                        return new Tuple4<String, byte[], List<byte[]>, BigInteger>(
                                (String) results.get(0).getValue(), 
                                (byte[]) results.get(1).getValue(), 
                                convertToNative((List<Bytes32>) results.get(2).getValue()), 
                                (BigInteger) results.get(3).getValue());
                    }
                });
    }

    @Deprecated
    public static IWorkerRegistryList load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new IWorkerRegistryList(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static IWorkerRegistryList load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new IWorkerRegistryList(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static IWorkerRegistryList load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new IWorkerRegistryList(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static IWorkerRegistryList load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new IWorkerRegistryList(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static RemoteCall<IWorkerRegistryList> deploy(Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(IWorkerRegistryList.class, web3j, credentials, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<IWorkerRegistryList> deploy(Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(IWorkerRegistryList.class, web3j, credentials, gasPrice, gasLimit, BINARY, "");
    }

    public static RemoteCall<IWorkerRegistryList> deploy(Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(IWorkerRegistryList.class, web3j, transactionManager, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<IWorkerRegistryList> deploy(Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(IWorkerRegistryList.class, web3j, transactionManager, gasPrice, gasLimit, BINARY, "");
    }

    protected String getStaticDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static String getPreviouslyDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }
}
