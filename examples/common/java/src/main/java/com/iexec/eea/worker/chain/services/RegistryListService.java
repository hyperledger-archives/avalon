package com.iexec.eea.worker.chain.services;

import com.iexec.eea.worker.chain.model.ChainRegistry;
import com.iexec.eea.worker.config.WorkerConfigurationService;
import lombok.extern.slf4j.Slf4j;
import com.iexec.eea.worker.contract.generated.WorkerRegistryList;
import org.web3j.ens.EnsResolutionException;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.tuples.generated.Tuple3;
import org.web3j.tuples.generated.Tuple4;
import org.web3j.tx.gas.ContractGasProvider;
import org.web3j.tx.gas.DefaultGasProvider;

import java.math.BigInteger;
import java.util.List;

import static com.iexec.eea.worker.utils.BytesUtils.*;

@Slf4j
//@Service
public class RegistryListService {

    private final CredentialsService credentialsService;
    private org.web3j.protocol.Web3jService web3jService;
    private final Web3j web3j;
    private final Web3jService web3JService;
    private final String registryListAddress;

    //@Autowired
    public RegistryListService(CredentialsService credentialsService, Web3jService web3JService,
                               WorkerConfigurationService workerConfigurationService) {
        this.credentialsService = credentialsService;
        this.web3j = web3JService.getWeb3j();
        this.web3JService = web3JService;
        this.registryListAddress = workerConfigurationService.getRegistryListAddress();
    }

    public WorkerRegistryList getWorkerRegistryListContract(ContractGasProvider contractGasProvider) {
        ExceptionInInitializerError exceptionInInitializerError =
                new ExceptionInInitializerError("Failed to load WorkerRegistryList contract from address "
                        + registryListAddress);

        if (registryListAddress != null && !registryListAddress.isEmpty()) {
            try {
                return WorkerRegistryList.load(
                        registryListAddress, web3j, credentialsService.getCredentials(), contractGasProvider);
            } catch (EnsResolutionException e) {
                throw exceptionInInitializerError;
            }
        } else {
            throw exceptionInInitializerError;
        }
    }

    public WorkerRegistryList getWorkerRegistryListContract() {
        return getWorkerRegistryListContract(new DefaultGasProvider());
    }


    // public RemoteCall<TransactionReceipt> registryAdd(byte[] orgID, String uri, byte[] scAddr, List<byte[]> appTypeIds)
    public boolean registryAdd(String orgId, String uri, String scAddr, String[] appTypeIds) {
        byte[] orgIdBytes = stringToBytes(orgId);
        byte[] scAddrBytes = stringToBytes(scAddr);
        List<byte[]> appTypeIdsBytes = stringsToBytes(appTypeIds);

        if (!isBytes32(orgIdBytes)) {
            log.error("orgId must be valid byte32[]: " + bytesToString(orgIdBytes));
            return false;
        }

        for(byte[] b: appTypeIdsBytes) {
            if (!isBytes32(b)) {
                log.error("App id must be valid byte32[]: " + bytesToString(b));
                return false;
            }
        }

        if (!isBytes32(scAddrBytes)) {
            log.error("SC addr must be valid byte32[]: " + bytesToString(scAddrBytes));
            return false;
        }


        TransactionReceipt addReceipt;
        RemoteCall<TransactionReceipt> addCall = getWorkerRegistryListContract().registryAdd(
                orgIdBytes,
                uri,
                scAddrBytes,
                appTypeIdsBytes
        );

        try {
            addReceipt = addCall.send();
            log.error("Added registry [scAddr:{}, uri:{}, gasUsed:{}]", scAddr, uri, addReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to add registry [scAddr:{}, exception:{}]", scAddr, e.getMessage());
        }

        return false;
    }

    // public RemoteCall<TransactionReceipt> registryUpdate(byte[] orgID, String uri, byte[] scAddr, List<byte[]> appTypeIds)
    public boolean registryUpdate(String orgId, String uri, String scAddr, String[] appTypeIds) {
        byte[] orgIdBytes = stringToBytes(orgId);
        byte[] scAddrBytes = stringToBytes(scAddr);
        List<byte[]> appTypeIdsBytes = stringsToBytes(appTypeIds);

        TransactionReceipt updateReceipt;
        RemoteCall<TransactionReceipt> updateCall = getWorkerRegistryListContract().registryUpdate(
                orgIdBytes,
                uri,
                scAddrBytes,
                appTypeIdsBytes
        );

        try {
            updateReceipt = updateCall.send();
            log.error("Updated registry [orgId:{}, uri:{}, gasUsed:{}]", orgId, uri, updateReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to update registry [orgId:{}, exception:{}]", orgId, e.getMessage());
        }

        return false;
    }

    // public RemoteCall<TransactionReceipt> registrySetStatus(byte[] orgID, BigInteger status)
    public boolean registrySetStatus(String orgId, int status) {
        byte[] orgIdBytes = stringToBytes(orgId);

        TransactionReceipt setStatusReceipt;
        RemoteCall<TransactionReceipt> setStatusCall = getWorkerRegistryListContract().registrySetStatus(
                orgIdBytes,
                BigInteger.valueOf(status)
        );

        try {
            setStatusReceipt = setStatusCall.send();
            log.error("Set registry status [scAddr:{}, status:{}, gasUsed:{}]",
                    orgId, status, setStatusReceipt.getGasUsed());
            return true;
        } catch (Exception e) {
            log.error("Failed to set registry status [orgId:{}, exception:{}]", orgId, e.getMessage());
        }

        return false;
    }

    // public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> registryLookUp(byte[] appTypeId) {
    public String[] registryLookUp(String appTypeId) {
        // TODO this ignores lookupTag
        byte[] appTypeIdByte = stringToBytes(appTypeId);

        Tuple3<BigInteger, String, List<byte[]>> lookupResult;
        RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> lookupCall = getWorkerRegistryListContract().registryLookUp(
                appTypeIdByte
        );

        try {
            lookupResult = lookupCall.send();
            log.info("registryLookUp [appTypeId:{}, nbResults:{}/{}]",
                    appTypeId, lookupResult.getValue3().size(), lookupResult.getValue1());
        } catch (Exception e) {
            log.error("Failed to registryLookUp[appTypeId:{}, exception:{}", appTypeId, e.getMessage());
            return null;
        }

        return bytesToStrings(lookupResult.getValue3());
    }

    // public RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> registryLookUpNext(byte[] appTypeId, String param1)
    public String[] registryLookUpNext(String appTypeId, String lookupTag) {
       byte[] appTypeIdByte = stringToBytes(appTypeId);

        Tuple3<BigInteger, String, List<byte[]>> lookupResult;
        RemoteCall<Tuple3<BigInteger, String, List<byte[]>>> lookupCall = getWorkerRegistryListContract().registryLookUpNext(
                appTypeIdByte,
                lookupTag
        );

        try {
            lookupResult = lookupCall.send();
            log.info("registryLookUp [appTypeId:{}, nbResults:{}/{}]",
                    appTypeId, lookupResult.getValue3().size(), lookupResult.getValue1());
        } catch (Exception e) {
            log.error("Failed to registryLookUp[appTypeId:{}, exception:{}", appTypeId, e.getMessage());
            return null;
        }

        return bytesToStrings(lookupResult.getValue3());
    }


    // public RemoteCall<Tuple4<String, byte[], List<byte[]>, BigInteger>> registryRetrieve(byte[] orgID)
    public ChainRegistry registryRetrieve(String orgId) {
        byte[] orgIdBytes = stringToBytes(orgId);

        Tuple4<String, byte[], List<byte[]>, BigInteger> registry;
        RemoteCall<Tuple4<String, byte[], List<byte[]>, BigInteger>> retrieveCall =
                getWorkerRegistryListContract().registryRetrieve(orgIdBytes);

        try {
            registry = retrieveCall.send();
        } catch (Exception e) {
            log.error("Failed to retrieve registry [orgId:{}, exception:{}]", orgId, e.getMessage());
            return null;
        }

        return ChainRegistry.fromTuple(registry);
    }
}
