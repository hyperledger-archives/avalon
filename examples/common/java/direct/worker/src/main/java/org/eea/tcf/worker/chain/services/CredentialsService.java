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

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.web3j.crypto.CipherException;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;

import java.io.IOException;

@Slf4j
@Service
public class CredentialsService {

    private Credentials credentials;

    public CredentialsService(WalletDetails walletDetails) throws IOException,
            CipherException {
        try {
            credentials = WalletUtils.loadCredentials(walletDetails.getPassword(),
                    walletDetails.getPath());
            log.info("Load wallet credentials [address:{}] ", credentials.getAddress());
        } catch (IOException | CipherException e) {
            log.error("Credentials cannot be loaded [exception:{}] ", e);
            throw e;
        }
    }

    public Credentials getCredentials() {
        return credentials;
    }
}
