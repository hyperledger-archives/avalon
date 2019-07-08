package com.iexec.worker.chain;

import com.iexec.common.chain.*;
import com.iexec.common.contract.generated.IexecHubABILegacy;
import com.iexec.common.utils.HashUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.Optional;

@Slf4j
@Service
public class RevealService {

    private IexecHubService iexecHubService;
    private CredentialsService credentialsService;
    private Web3jService web3jService;

    public RevealService(IexecHubService iexecHubService,
                         CredentialsService credentialsService,
                         Web3jService web3jService) {
        this.iexecHubService = iexecHubService;
        this.credentialsService = credentialsService;
        this.web3jService = web3jService;
    }

    public boolean canReveal(String chainTaskId, String determinismHash) {

        Optional<ChainTask> optionalChainTask = iexecHubService.getChainTask(chainTaskId);
        if (!optionalChainTask.isPresent()) {
            log.error("Task couldn't be retrieved [chainTaskId:{}]", chainTaskId);
            return false;
        }
        ChainTask chainTask = optionalChainTask.get();

        boolean isChainTaskRevealing = iexecHubService.isChainTaskRevealing(chainTaskId);
        boolean isRevealDeadlineReached = chainTask.getRevealDeadline() < new Date().getTime();

        Optional<ChainContribution> optionalContribution = iexecHubService.getChainContribution(chainTaskId);
        if (!optionalContribution.isPresent()) {
            log.error("Contribution couldn't be retrieved [chainTaskId:{}]", chainTaskId);
            return false;
        }
        ChainContribution chainContribution = optionalContribution.get();
        boolean isChainContributionStatusContributed = chainContribution.getStatus().equals(ChainContributionStatus.CONTRIBUTED);
        boolean isContributionResultHashConsensusValue = chainContribution.getResultHash().equals(chainTask.getConsensusValue());

        boolean isContributionResultHashCorrect = false;
        boolean isContributionResultSealCorrect = false;

        if (!determinismHash.isEmpty()) {
            isContributionResultHashCorrect = chainContribution.getResultHash().equals(HashUtils.concatenateAndHash(chainTaskId, determinismHash));

            String walletAddress = credentialsService.getCredentials().getAddress();
            isContributionResultSealCorrect = chainContribution.getResultSeal().equals(
                    HashUtils.concatenateAndHash(walletAddress, chainTaskId, determinismHash)
            );
        }

        boolean ret = isChainTaskRevealing && !isRevealDeadlineReached &&
                isChainContributionStatusContributed && isContributionResultHashConsensusValue &&
                isContributionResultHashCorrect && isContributionResultSealCorrect;

        if (ret) {
            log.info("All the conditions are valid for the reveal to happen [chainTaskId:{}]", chainTaskId);
        } else {
            log.warn("One or more conditions are not met for the reveal to happen [chainTaskId:{}, " +
                            "isChainTaskRevealing:{}, isRevealDeadlineReached:{}, " +
                            "isChainContributionStatusContributed:{}, isContributionResultHashConsensusValue:{}, " +
                            "isContributionResultHashCorrect:{}, isContributionResultSealCorrect:{}]", chainTaskId,
                    isChainTaskRevealing, isRevealDeadlineReached,
                    isChainContributionStatusContributed, isContributionResultHashConsensusValue,
                    isContributionResultHashCorrect, isContributionResultSealCorrect);
        }

        return ret;
    }

    public boolean isConsensusBlockReached(String chainTaskId, long consensusBlock) {
        if (web3jService.isBlockAvailable(consensusBlock)) return true;

        log.warn("Chain sync issues, consensus block not reached yet [chainTaskId:{}, latestBlock:{}, consensusBlock:{}]",
                chainTaskId, web3jService.getLatestBlockNumber(), consensusBlock);
        return false;
    }

    // returns the ChainReceipt of the reveal if successful, empty otherwise
    public Optional<ChainReceipt> reveal(String chainTaskId, String determinismHash) {

        if (determinismHash.isEmpty()) {
            return Optional.empty();
        }

        IexecHubABILegacy.TaskRevealEventResponse revealResponse = iexecHubService.reveal(chainTaskId, determinismHash);
        if (revealResponse == null) {
            log.error("RevealTransactionReceipt received but was null [chainTaskId:{}]", chainTaskId);
            return Optional.empty();
        }

        ChainReceipt chainReceipt = ChainUtils.buildChainReceipt(revealResponse.log,
                chainTaskId, iexecHubService.getLatestBlockNumber());

        return Optional.of(chainReceipt);
    }
}
