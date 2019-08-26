package com.iexec.eea.worker.chain;

import com.iexec.eea.worker.utils.BytesUtils;
import lombok.extern.slf4j.Slf4j;
import org.bouncycastle.util.Arrays;
import org.web3j.crypto.Hash;
import org.web3j.utils.Convert;

import java.math.BigDecimal;
import java.math.BigInteger;

@Slf4j
public class ChainUtils {

    private ChainUtils() {
        throw new UnsupportedOperationException();
    }

    public static BigDecimal weiToEth(BigInteger weiAmount) {
        return Convert.fromWei(weiAmount.toString(), Convert.Unit.ETHER);
    }
}
