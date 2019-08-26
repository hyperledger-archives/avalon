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
public class WorkerRegistryList extends Contract {
    private static final String BINARY = "0x608060405234801561001057600080fd5b50610952806100206000396000f3fe608060405234801561001057600080fd5b50600436106100625760003560e01c806350e08fc514610067578063894fa0e51461008f5780639740e6051461008f578063be370e3b1461015c578063ccba7a5714610293578063e1ec891e1461037d575b600080fd5b61008d6004803603604081101561007d57600080fd5b508035906020013560ff1661039a565b005b61008d600480360360808110156100a557600080fd5b813591908101906040810160208201356401000000008111156100c757600080fd5b8201836020820111156100d957600080fd5b803590602001918460018302840111640100000000831117156100fb57600080fd5b9193909282359260408101906020013564010000000081111561011d57600080fd5b82018360208201111561012f57600080fd5b8035906020019184602083028401116401000000008311171561015157600080fd5b5090925090506103bf565b6101d36004803603604081101561017257600080fd5b8135919081019060408101602082013564010000000081111561019457600080fd5b8201836020820111156101a657600080fd5b803590602001918460018302840111640100000000831117156101c857600080fd5b509092509050610416565b604051808481526020018060200180602001838103835285818151815260200191508051906020019080838360005b8381101561021a578181015183820152602001610202565b50505050905090810190601f1680156102475780820380516001836020036101000a031916815260200191505b508381038252845181528451602091820191808701910280838360005b8381101561027c578181015183820152602001610264565b505050509050019550505050505060405180910390f35b6102b0600480360360208110156102a957600080fd5b5035610466565b6040518080602001858152602001806020018460ff1660ff168152602001838103835287818151815260200191508051906020019080838360005b838110156103035781810151838201526020016102eb565b50505050905090810190601f1680156103305780820380516001836020036101000a031916815260200191505b508381038252855181528551602091820191808801910280838360005b8381101561036557818101518382015260200161034d565b50505050905001965050505050505060405180910390f35b6101d36004803603602081101561039357600080fd5b5035610582565b600091825260208290526040909120600301805460ff191660ff909216919091179055565b6103c8866105d0565b60008681526020819052604090206103e1818787610828565b50600181018490556103f76002820184846108a6565b5060038101805460ff1916905561040d87610635565b50505050505050565b6000838152600160205260408120606090819061043290610695565b600087815260016020526040902061044990610699565b604080516020810190915260008152919891975095509350505050565b600081815260208181526040808320600180820154600383015483548551601f60026000199684161561010002969096019092168590049182018890048802810188019096528086526060979688968896958695949086019360ff909116928691908301828280156105195780601f106104ee57610100808354040283529160200191610519565b820191906000526020600020905b8154815290600101906020018083116104fc57829003601f168201915b505050505093508180548060200260200160405190810160405280929190818152602001828054801561056b57602002820191906000526020600020905b815481526020019060010190808311610557575b505050505091509450945094509450509193509193565b6000818152600160205260408120606090819061059e90610695565b60008581526001602052604090206105b590610699565b60408051602081019091526000815291969195509350915050565b6000818152602081905260408120600201905b815481101561063057610627836001600085858154811061060057fe5b906000526020600020015481526020019081526020016000206106f590919063ffffffff16565b506001016105e3565b505050565b6000818152602081905260408120600201905b81548110156106305761068c836001600085858154811061066557fe5b906000526020600020015481526020019081526020016000206107b490919063ffffffff16565b50600101610648565b5490565b6060816000018054806020026020016040519081016040528092919081815260200182805480156106e957602002820191906000526020600020905b8154815260200190600101908083116106d5575b50505050509050919050565b600061070183836107fd565b61070d575060006107ae565b60006107198484610812565b9050600061072685610695565b905080821461078557600085600001600183038154811061074357fe5b906000526020600020015490508086600001600185038154811061076357fe5b6000918252602080832090910192909255918252600187019052604090208290555b60008481526001860160205260408120558454600019016107a686826108e0565b506001925050505b92915050565b60006107c083836107fd565b156107cd575060006107ae565b50815460018082018085556000858152602080822090940185905593845293810190915260409091209190915590565b60006108098383610812565b15159392505050565b6000908152600191909101602052604090205490565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106108695782800160ff19823516178555610896565b82800160010185558215610896579182015b8281111561089657823582559160200191906001019061087b565b506108a2929150610900565b5090565b828054828255906000526020600020908101928215610896579160200282018281111561089657823582559160200191906001019061087b565b815481835581811115610630576000838152602090206106309181019083015b61091a91905b808211156108a25760008155600101610906565b9056fea265627a7a723058202c616de88d5659604ca097b7fdec0a207b814bbfe8dca872d8ccc17975ca88a564736f6c634300050a0032";

    public static final String FUNC_REGISTRYADD = "registryAdd";

    public static final String FUNC_REGISTRYUPDATE = "registryUpdate";

    public static final String FUNC_REGISTRYSETSTATUS = "registrySetStatus";

    public static final String FUNC_REGISTRYLOOKUP = "registryLookUp";

    public static final String FUNC_REGISTRYLOOKUPNEXT = "registryLookUpNext";

    public static final String FUNC_REGISTRYRETRIEVE = "registryRetrieve";

    protected static final HashMap<String, String> _addresses;

    static {
        _addresses = new HashMap<String, String>();
        _addresses.put("1564389941067", "0x9B04867c5551EC3b5aa9EB1496DdC79EE0e95ECb");
    }

    @Deprecated
    protected WorkerRegistryList(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    protected WorkerRegistryList(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        super(BINARY, contractAddress, web3j, credentials, contractGasProvider);
    }

    @Deprecated
    protected WorkerRegistryList(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        super(BINARY, contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    protected WorkerRegistryList(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
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

    public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> registryLookUpNext(byte[] appTypeId, String param1) {
        final Function function = new Function(FUNC_REGISTRYLOOKUPNEXT, 
                Arrays.<Type>asList(new org.web3j.abi.datatypes.generated.Bytes32(appTypeId), 
                new org.web3j.abi.datatypes.Utf8String(param1)), 
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
    public static WorkerRegistryList load(String contractAddress, Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkerRegistryList(contractAddress, web3j, credentials, gasPrice, gasLimit);
    }

    @Deprecated
    public static WorkerRegistryList load(String contractAddress, Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return new WorkerRegistryList(contractAddress, web3j, transactionManager, gasPrice, gasLimit);
    }

    public static WorkerRegistryList load(String contractAddress, Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return new WorkerRegistryList(contractAddress, web3j, credentials, contractGasProvider);
    }

    public static WorkerRegistryList load(String contractAddress, Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return new WorkerRegistryList(contractAddress, web3j, transactionManager, contractGasProvider);
    }

    public static RemoteCall<WorkerRegistryList> deploy(Web3j web3j, Credentials credentials, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkerRegistryList.class, web3j, credentials, contractGasProvider, BINARY, "");
    }

    public static RemoteCall<WorkerRegistryList> deploy(Web3j web3j, TransactionManager transactionManager, ContractGasProvider contractGasProvider) {
        return deployRemoteCall(WorkerRegistryList.class, web3j, transactionManager, contractGasProvider, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkerRegistryList> deploy(Web3j web3j, Credentials credentials, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkerRegistryList.class, web3j, credentials, gasPrice, gasLimit, BINARY, "");
    }

    @Deprecated
    public static RemoteCall<WorkerRegistryList> deploy(Web3j web3j, TransactionManager transactionManager, BigInteger gasPrice, BigInteger gasLimit) {
        return deployRemoteCall(WorkerRegistryList.class, web3j, transactionManager, gasPrice, gasLimit, BINARY, "");
    }

    protected String getStaticDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }

    public static String getPreviouslyDeployedAddress(String networkId) {
        return _addresses.get(networkId);
    }
}
