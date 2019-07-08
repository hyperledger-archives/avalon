package com.iexec.worker.chain;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
@Getter
@AllArgsConstructor
@NoArgsConstructor
class WalletDetails {

    @Value("${wallet.encryptedFilePath}")
    private String path;

    @Value("${wallet.password}")
    private String password;
}
