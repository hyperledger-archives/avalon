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

import org.eea.tcf.worker.config.WorkerConfigurationService;
import lombok.extern.slf4j.Slf4j;
import org.eea.tcf.worker.utils.WaitUtils;
import org.eea.tcf.worker.chain.ChainUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.response.EthBlock;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.gas.ContractGasProvider;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.Optional;

@Service
@Slf4j
public class Web3jService {

    private final static long GAS_LIMIT_CAP = 500000;
    private final Web3j web3j;
    private final float gasPriceMultiplier;
    private final long gasPriceCap;

    @Autowired
    public Web3jService(WorkerConfigurationService workerConfService) {
        this(workerConfService.getBlockchainNodeAddress(),
                workerConfService.getGasPriceMultiplier(),
                workerConfService.getGasPriceCap());
    }

    public Web3jService(String chainNodeAddress,
                        float gasPriceMultiplier,
                        long gasPriceCap) {
        this.web3j = getWeb3j(chainNodeAddress);
        this.gasPriceMultiplier = gasPriceMultiplier;
        this.gasPriceCap = gasPriceCap;
    }

    public static BigInteger getMaxTxCost(long gasPriceCap) {
        return BigInteger.valueOf(GAS_LIMIT_CAP * gasPriceCap);
    }

    private Web3j getWeb3j(String chainNodeAddress) {
        Web3j web3j = Web3j.build(new HttpService(chainNodeAddress));
        try {
            if (web3j.web3ClientVersion().send().getWeb3ClientVersion() != null) {
                log.info("Connected to Ethereum node [address:{}, version:{}]",
                        chainNodeAddress,
                        web3j.web3ClientVersion().send().getWeb3ClientVersion());
                return web3j;
            }
        } catch (IOException ignored) {
        }

        int fewSeconds = 5;
        WaitUtils.sleep(fewSeconds);
        log.error("Failed to connect to ethereum node (will retry) [chainNodeAddress:{}, retryIn:{}]",
                chainNodeAddress, fewSeconds);
        return getWeb3j(chainNodeAddress);
    }

    public Web3j getWeb3j() {
        return web3j;
    }

    public EthBlock.Block getLatestBlock() throws IOException {
        return web3j.ethGetBlockByNumber(DefaultBlockParameterName.LATEST,
                false).send().getBlock();
    }

    public long getLatestBlockNumber() {
        try {
            return getLatestBlock().getNumber().longValue();
        } catch (IOException e) {
            log.error("GetLastBlock failed");
        }
        return 0;
    }

    private EthBlock.Block getBlock(long blockNumber) throws IOException {
        return web3j.ethGetBlockByNumber(DefaultBlockParameter.valueOf(BigInteger.valueOf(blockNumber)),
                false).send().getBlock();
    }

    // check if the blockNumber is already available for the scheduler
    // blockNumber is different than 0 only for status the require a check on the blockchain, so the scheduler should
    // already have this block, otherwise it should wait for a maximum of 10 blocks.
    public boolean isBlockAvailable(long blockNumber) {
        // if the blockNumber is already available then simply returns true
        if (blockNumber <= getLatestBlockNumber())
            return true;

        // otherwise we wait for a maximum of 10 blocks to see if the block will be available
        try {
            long maxBlockNumber = blockNumber + 10;
            long currentBlockNumber = getLatestBlockNumber();
            while (currentBlockNumber <= maxBlockNumber) {
                if (blockNumber <= currentBlockNumber) {
                    return true;
                } else {
                    log.warn("Chain is NOT synchronized yet [blockNumber:{}, currentBlockNumber:{}]", blockNumber, currentBlockNumber);
                    Thread.sleep(500);
                }
                currentBlockNumber = getLatestBlockNumber();
            }
        } catch (InterruptedException e) {
            log.error("Error in checking the latest block number [execption:{}]",
                    e.getMessage());
        }

        return false;
    }

    public long getMaxWaitingTimeWhenPendingReceipt() {
        long maxWaitingTime = 2 * 60 * 1000L; // 2min

        // max waiting Time should be roughly the time of 10 blocks
        try {
            EthBlock.Block latestBlock = getLatestBlock();

            long latestBlockNumber = latestBlock.getNumber().longValue();

            BigInteger latestBlockTimestamp = latestBlock.getTimestamp();
            BigInteger tenBlocksAgoTimestamp = getBlock(latestBlockNumber - 10).getTimestamp();

            maxWaitingTime = (latestBlockTimestamp.longValue() -
                    tenBlocksAgoTimestamp.longValue()) * 1000;

            log.info(" [latestBlockTimestamp:{}, tenBlocksAgoTimestamp:{}, maxWaitingTime:{}]",
                    latestBlockTimestamp, tenBlocksAgoTimestamp, maxWaitingTime);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return maxWaitingTime;
    }

    public boolean hasEnoughGas(String address) {
        Optional<BigInteger> optionalBalance = getBalance(address);
        if (!optionalBalance.isPresent()) {
            return false;
        }

        BigInteger weiBalance = optionalBalance.get();
        BigInteger estimateTxNb = weiBalance.divide(getMaxTxCost(gasPriceCap));
        BigDecimal balanceToShow = ChainUtils.weiToEth(weiBalance);

        if (estimateTxNb.compareTo(BigInteger.ONE) < 0) {
            log.error("ETH balance is empty, please refill gas now [balance:{}, estimateTxNb:{}]",
                    balanceToShow, estimateTxNb);
            return false;
        } else if (estimateTxNb.compareTo(BigInteger.TEN) < 0) {
            log.warn("ETH balance very low, should refill gas now [balance:{}, estimateTxNb:{}]",
                    balanceToShow, estimateTxNb);
        } else {
            log.info("ETH balance is fine [balance:{}, estimateTxNb:{}]",
                    balanceToShow, estimateTxNb);
        }
        return true;
    }

    public Optional<BigInteger> getBalance(String address) {
        try {
            return Optional.of(web3j.ethGetBalance(address,
                    DefaultBlockParameterName.LATEST).send().getBalance());
        } catch (IOException e) {
            return Optional.empty();
        }
    }

    public Optional<BigInteger> getNetworkGasPrice() {
        try {
            BigInteger gasPrice = web3j.ethGasPrice().send().getGasPrice();
            return Optional.of(gasPrice);
        } catch (IOException e) {
            log.error("getNetworkGasPrice failed");
            return Optional.empty();
        }
    }

    public BigInteger getUserGasPrice(float gasPriceMultiplier,
                                      long gasPriceCap) {
        Optional<BigInteger> networkGasPrice = getNetworkGasPrice();
        if (!networkGasPrice.isPresent()) {
            return BigInteger.valueOf(gasPriceCap);
        }
        long wishedGasPrice = (long) (networkGasPrice.get().floatValue() *
                gasPriceMultiplier);

        return BigInteger.valueOf(Math.min(wishedGasPrice, gasPriceCap));
    }

    /*
     * This is just a dummy stub for contract reader:
     * gas price & gas limit is not required when querying (read) an eth node
     *
     */
    public ContractGasProvider getReadingContractGasProvider() {
        return new ContractGasProvider() {
            @Override
            public BigInteger getGasPrice(String contractFunc) {
                return null;
            }

            @Override
            public BigInteger getGasPrice() {
                return null;
            }

            @Override
            public BigInteger getGasLimit(String contractFunc) {
                return null;
            }

            @Override
            public BigInteger getGasLimit() {
                return null;
            }
        };
    }
}
