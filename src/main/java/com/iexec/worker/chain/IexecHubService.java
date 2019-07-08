package com.iexec.worker.chain;


import com.iexec.common.chain.*;
import com.iexec.common.contract.generated.IexecHubABILegacy;
import com.iexec.common.security.Signature;
import com.iexec.common.utils.BytesUtils;
import com.iexec.worker.config.PublicConfigurationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.TransactionReceipt;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.function.Function;

import static com.iexec.common.chain.ChainContributionStatus.CONTRIBUTED;
import static com.iexec.common.chain.ChainContributionStatus.REVEALED;
import static com.iexec.common.utils.BytesUtils.stringToBytes;


@Slf4j
@Service
public class IexecHubService extends IexecHubAbstractService {

    private final CredentialsService credentialsService;
    private final ThreadPoolExecutor executor;
    private Web3jService web3jService;

    @Autowired
    public IexecHubService(CredentialsService credentialsService,
                           Web3jService web3jService,
                           PublicConfigurationService publicConfigurationService) {
        super(credentialsService.getCredentials(), web3jService, publicConfigurationService.getIexecHubAddress());
        this.credentialsService = credentialsService;
        this.web3jService = web3jService;
        this.executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(1);
    }

    IexecHubABILegacy.TaskContributeEventResponse contribute(ContributionAuthorization contribAuth,
                                                             String resultHash,
                                                             String resultSeal,
                                                             Signature enclaveSignature) {
        try {
            return CompletableFuture.supplyAsync(() -> {
                log.info("Requested  contribute [chainTaskId:{}, waitingTxCount:{}]",
                        contribAuth.getChainTaskId(), getWaitingTransactionCount());
                return sendContributeTransaction(contribAuth, resultHash, resultSeal, enclaveSignature);
            }, executor).get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
        return null;
    }

    private IexecHubABILegacy.TaskContributeEventResponse sendContributeTransaction(ContributionAuthorization contribAuth,
                                                                                    String resultHash,
                                                                                    String resultSeal,
                                                                                    Signature enclaveSignature) {
        TransactionReceipt contributeReceipt;
        String chainTaskId = contribAuth.getChainTaskId();

        byte[] enclaveSign = BytesUtils.stringToBytes(enclaveSignature.getValue());
        byte[] workerPoolSign = BytesUtils.stringToBytes(contribAuth.getSignature().getValue());

        RemoteCall<TransactionReceipt> contributeCall = getHubContract(web3jService.getWritingContractGasProvider()).contribute(
                stringToBytes(chainTaskId),
                stringToBytes(resultHash),
                stringToBytes(resultSeal),
                contribAuth.getEnclaveChallenge(),
                enclaveSign,
                workerPoolSign);
        log.info("Sent contribute [chainTaskId:{}, resultHash:{}]", chainTaskId, resultHash);

        try {
            contributeReceipt = contributeCall.send();
        } catch (Exception e) {
            log.error("Failed to contribute [chainTaskId:{}, exception:{}]", chainTaskId, e.getMessage());
            e.printStackTrace();
            return null;
        }

        List<IexecHubABILegacy.TaskContributeEventResponse> contributeEvents = getHubContract().getTaskContributeEvents(contributeReceipt);

        IexecHubABILegacy.TaskContributeEventResponse contributeEvent = null;
        if (contributeEvents != null && !contributeEvents.isEmpty()) {
            contributeEvent = contributeEvents.get(0);
        }

        if (contributeEvent != null && contributeEvent.log != null &&
                isStatusValidOnChainAfterPendingReceipt(chainTaskId, CONTRIBUTED, this::isContributionStatusValidOnChain)) {
            log.info("Contributed [chainTaskId:{}, resultHash:{}, gasUsed:{}, log:{}]",
                    chainTaskId, resultHash, contributeReceipt.getGasUsed(), contributeEvent.log);
            return contributeEvent;
        }

        log.error("Failed to contribute [chainTaskId:{}]", chainTaskId);
        return null;
    }

    IexecHubABILegacy.TaskRevealEventResponse reveal(String chainTaskId, String resultDigest) {
        try {
            return CompletableFuture.supplyAsync(() -> {
                log.info("Requested  reveal [chainTaskId:{}, waitingTxCount:{}]", chainTaskId, getWaitingTransactionCount());
                return sendRevealTransaction(chainTaskId, resultDigest);
            }, executor).get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
        return null;
    }

    private IexecHubABILegacy.TaskRevealEventResponse sendRevealTransaction(String chainTaskId, String resultDigest) {
        TransactionReceipt revealReceipt;
        RemoteCall<TransactionReceipt> revealCall = getHubContract(web3jService.getWritingContractGasProvider()).reveal(
                stringToBytes(chainTaskId),
                stringToBytes(resultDigest));

        log.info("Sent reveal [chainTaskId:{}, resultDigest:{}]", chainTaskId, resultDigest);
        try {
            revealReceipt = revealCall.send();
        } catch (Exception e) {
            log.error("Failed to reveal [chainTaskId:{}, exception:{}]", chainTaskId, e.getMessage());
            e.printStackTrace();
            return null;
        }

        List<IexecHubABILegacy.TaskRevealEventResponse> revealEvents = getHubContract().getTaskRevealEvents(revealReceipt);

        IexecHubABILegacy.TaskRevealEventResponse revealEvent = null;
        if (revealEvents != null && !revealEvents.isEmpty()) {
            revealEvent = revealEvents.get(0);
        }

        if (revealEvent != null && revealEvent.log != null &&
                isStatusValidOnChainAfterPendingReceipt(chainTaskId, REVEALED, this::isContributionStatusValidOnChain)) {
            log.info("Revealed [chainTaskId:{}, resultDigest:{}, gasUsed:{}, log:{}]",
                    chainTaskId, resultDigest, revealReceipt.getGasUsed(), revealEvent.log);
            return revealEvent;
        }

        log.error("Failed to reveal [chainTaskId:{}]", chainTaskId);
        return null;
    }

    private long getWaitingTransactionCount() {
        return executor.getTaskCount() - 1 - executor.getCompletedTaskCount();
    }

    Optional<ChainContribution> getChainContribution(String chainTaskId) {
        return getChainContribution(chainTaskId, credentialsService.getCredentials().getAddress());
    }

    Optional<ChainAccount> getChainAccount() {
        return getChainAccount(credentialsService.getCredentials().getAddress());
    }

    public boolean hasEnoughGas() {
        return web3jService.hasEnoughGas(credentialsService.getCredentials().getAddress());
    }

    public long getLatestBlockNumber() {
        return web3jService.getLatestBlockNumber();
    }

    public long getMaxWaitingTimeWhenNotSync() {
        return web3jService.getMaxWaitingTimeWhenPendingReceipt();
    }

    private Boolean isContributionStatusValidOnChain(String chainTaskId, ChainStatus chainContributionStatus) {
        if (chainContributionStatus instanceof ChainContributionStatus) {
            Optional<ChainContribution> chainContribution = getChainContribution(chainTaskId);
            return chainContribution.isPresent() && chainContribution.get().getStatus().equals(chainContributionStatus);
        }
        return false;
    }

    private boolean isBlockchainReadTrueWhenNodeNotSync(String chainTaskId, Function<String, Boolean> booleanBlockchainReadFunction) {
        long maxWaitingTime = web3jService.getMaxWaitingTimeWhenPendingReceipt();
        long startTime = System.currentTimeMillis();

        for(long duration = 0L; duration < maxWaitingTime; duration = System.currentTimeMillis() - startTime) {
            try {
                if (booleanBlockchainReadFunction.apply(chainTaskId)) {
                    return true;
                }

                Thread.sleep(500L);
            } catch (InterruptedException e) {
                log.error("Error in checking the latest block number [chainTaskId:{}, maxWaitingTime:{}]",
                        chainTaskId, maxWaitingTime);
            }
        }

        return false;
    }

    Boolean isChainTaskActive(String chainTaskId){
        Optional<ChainTask> chainTask = getChainTask(chainTaskId);
        if (chainTask.isPresent()){
            switch (chainTask.get().getStatus()){
                case UNSET:
                    break;//Could happen if node not synchronized. Should wait.
                case ACTIVE:
                    return true;
                case REVEALING:
                    return  false;
                case COMPLETED:
                    return false;
                case FAILLED:
                    return false;
            }
        }
        return false;
    }

    public Boolean isChainTaskRevealing(String chainTaskId){
        Optional<ChainTask> chainTask = getChainTask(chainTaskId);
        if (chainTask.isPresent()){
            switch (chainTask.get().getStatus()){
                case UNSET:
                    break;//Should not happen
                case ACTIVE:
                    break;//Could happen if node not synchronized. Should wait.
                case REVEALING:
                    return  true;
                case COMPLETED:
                    return false;
                case FAILLED:
                    return false;
            }
        }
        return false;
    }

}
