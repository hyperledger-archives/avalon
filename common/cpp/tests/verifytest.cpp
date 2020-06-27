/*
 * Copyright 2020 Intel Corporation
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
 */

/*
 * Test RSA digital signatures in verify_signature.cpp.
 *
 * Test case from /tc/sgx/trusted_worker_manager/tests/testCrypto.cpp
 * and from upstream common/tests/testCrypto.cpp in
 * https://github.com/hyperledger-labs/private-data-objects
 *
 * # Script to generate test signature
 * # Sign a message
 * openssl dgst -sha256 -sign avalon.key -out message.signature.raw message
 * openssl base64 -in message.signature.raw -out message.signature
 * # Extract public key from private key
 * openssl rsa -in avalon.key -pubout >avalon.key.public
 * # Verify message
 * openssl dgst -sha256 -verify avalon.key.public -signature message.signature
 */

#include <string.h>
#include <stdio.h>

#include "crypto_shared.h" // Sets default CRYPTOLIB_* value
#ifdef CRYPTOLIB_OPENSSL
#include <openssl/evp.h>
#endif
#include "verify_signature.h"

// Test X.509 certificate
// To dump, type: openssl x509 -noout -text <mycertfilename.pem
// RSA-4096/SHA-256 test cert valid 2020-2061
static const char test_cert[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIF7TCCA9UCFDej+FNF8O5QemWV3PIDOB7wcJZmMA0GCSqGSIb3DQEBCwUAMIGs\n"
    "MQswCQYDVQQGEwJVUzELMAkGA1UECAwCT1IxEzARBgNVBAcMCkxha2UgR3JvdmUx\n"
    "GzAZBgNVBAoMEkh5cGVybGVkZ2VyIEF2YWxvbjEQMA4GA1UECwwHVGVzdCBDQTEi\n"
    "MCAGA1UEAwwZY2EuYXZhbG9uLmh5cGVybGVkZ2VyLm9yZzEoMCYGCSqGSIb3DQEJ\n"
    "ARYZY2FAYXZhbG9uLmh5cGVybGVkZ2VyLm9yZzAgFw0yMDA0MjgyMTUxNTZaGA8y\n"
    "MDYxMDUyMjIxNTE1NlowgbYxCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJPUjETMBEG\n"
    "A1UEBwwKTGFrZSBHcm92ZTEbMBkGA1UECgwSSHlwZXJsZWRnZXIgQXZhbG9uMRAw\n"
    "DgYDVQQLDAdUZXN0IENBMScwJQYDVQQDDB50ZXN0LmNhLmF2YWxvbi5oeXBlcmxl\n"
    "ZGdlci5vcmcxLTArBgkqhkiG9w0BCQEWHnRlc3QuY2FAYXZhbG9uLmh5cGVybGVk\n"
    "Z2VyLm9yZzCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAL4lzykLaFXJ\n"
    "b39fIlg9XJusYjXouKZfpuhKTG/UTNkvvv4gtXse4qyVo2phYlrFX4fMbBYQcqv7\n"
    "Lh9b7xlpx6DxqwjTX045beq/Zgih21TG2dHk1tk1Rian3SR1qgHeglUAdET3TeJ1\n"
    "yf886+P4+9MJu7wqhLbCBaOsibKl+WnPABVG/azvzl5VRvWtO+icKpuy86Hd0lV9\n"
    "BUwtiwyOiPwitG5Tl+IAD0v/I36WWDxxUG1xEQqND8IF1yWSdhFlw5YVSBWIHyoh\n"
    "SE5V5YyKDPMadRwvRfi4bCsCtBlFX1Ow+5GBFTZle3Vh7ED1m2ntgT0pkf8PLUg0\n"
    "A7A3n34Dn/zsV1LKlnYvNxCqnv8bApGrHro47ysbZMJvzMzIWTG9+qYsnwaB1I1K\n"
    "sEoIdt4xCg+zY2sMRv87o4tfsPGuqrfT+Ll83OOIyBuLLWHKA/v1BeiYerXljJ1s\n"
    "mC33E39hHIBMHV0GyQpfM9adjeXlRz2Uoe5VQ9HrjiIYSUVcDVh1Z6EeBgCyICzp\n"
    "KhAld0Uo2YE1bgvHK3yQVLfszqYl1L/A2g/pFXQHQ3WZYBwVtivYHIr1w3oAM/OF\n"
    "j24Q60NwjDPUidtgffQkdXhv3s/8M2NBogGTgiAd9SFpN+BIXPLUyo5vH1Z11r2C\n"
    "Z1ysQAp2Hd4rKLnlANcdNflNBw52OWUdAgMBAAEwDQYJKoZIhvcNAQELBQADggIB\n"
    "ABsxX94sWIyVmCSPEQoE60hTiX3G9amV/Ut1skNpwW2aCTITZK8c6ubB6W1eI/zv\n"
    "RDHskfR1scolM5KYh8yQMmM188ASv8UOIKnbuoFPtma2bax5zBsvl18d/NnfGVbn\n"
    "RQI6Q8bWRkzTnd9AXXpGhhJ8QOPFXk8mpFx/280TBGR/XGWrWkXggMBGSOKLceqt\n"
    "Cqoo88u/YJWvnsmzZ6sXmd6CTUsNjJndzkElOITk0x+UQ27rbabSZfdqlQOJ2wbA\n"
    "+pAr/hGADHm9Ah2/nYTrGdSRvShtnhmeycUhmkHQfHIj8mVZU0DdzzHGJKFmkDGY\n"
    "mZE+iHyKl81sC21qUaBhVWK8f53OymxVlPUvnrLapmkLA31DqESAOV7ZvYD52jfJ\n"
    "Z8t4/anYO4kYXgrUIyvyBRau0Iw5fELXmMFMTWIuOhMPJvMXZp6EqQ1PKBf1MEpf\n"
    "ZOxF1ZFsSAAoGTPnz9c50ZU0uytvZbnt8uy5NxTJvxpn8JIGWFnzesa7D6D0KZVX\n"
    "aS2hV9X4I7HkCpiHYNnbE8y/OudtZLGenWUC5FRN78mMKI6spFiDNTDXqG7eBTN+\n"
    "yxcsITi2jtXJ7IOxXIifYVC/Vt8Wu7vLOFI2rR1WP7SJ204i/ilhI/p9xz7/SD+C\n"
    "97XvEDjLQsQpqVExTiuqSWdwCf3Ml9+4PJUAFMMVa3BR\n"
    "-----END CERTIFICATE-----\n";

// RSA-4096/SHA-256 test cert valid 2020-2061, issued by ca_cert
static const char test_cert2[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIF7TCCA9UCFDej+FNF8O5QemWV3PIDOB7wcJZnMA0GCSqGSIb3DQEBCwUAMIGs\n"
    "MQswCQYDVQQGEwJVUzELMAkGA1UECAwCT1IxEzARBgNVBAcMCkxha2UgR3JvdmUx\n"
    "GzAZBgNVBAoMEkh5cGVybGVkZ2VyIEF2YWxvbjEQMA4GA1UECwwHVGVzdCBDQTEi\n"
    "MCAGA1UEAwwZY2EuYXZhbG9uLmh5cGVybGVkZ2VyLm9yZzEoMCYGCSqGSIb3DQEJ\n"
    "ARYZY2FAYXZhbG9uLmh5cGVybGVkZ2VyLm9yZzAgFw0yMDA0MjkxNjI4NTVaGA8y\n"
    "MDYxMDUyMzE2Mjg1NVowgbYxCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJPUjETMBEG\n"
    "A1UEBwwKTGFrZSBHcm92ZTEbMBkGA1UECgwSSHlwZXJsZWRnZXIgQXZhbG9uMRAw\n"
    "DgYDVQQLDAdUZXN0IENBMScwJQYDVQQDDB50ZXN0LmNhLmF2YWxvbi5oeXBlcmxl\n"
    "ZGdlci5vcmcxLTArBgkqhkiG9w0BCQEWHnRlc3QuY2FAYXZhbG9uLmh5cGVybGVk\n"
    "Z2VyLm9yZzCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAL4lzykLaFXJ\n"
    "b39fIlg9XJusYjXouKZfpuhKTG/UTNkvvv4gtXse4qyVo2phYlrFX4fMbBYQcqv7\n"
    "Lh9b7xlpx6DxqwjTX045beq/Zgih21TG2dHk1tk1Rian3SR1qgHeglUAdET3TeJ1\n"
    "yf886+P4+9MJu7wqhLbCBaOsibKl+WnPABVG/azvzl5VRvWtO+icKpuy86Hd0lV9\n"
    "BUwtiwyOiPwitG5Tl+IAD0v/I36WWDxxUG1xEQqND8IF1yWSdhFlw5YVSBWIHyoh\n"
    "SE5V5YyKDPMadRwvRfi4bCsCtBlFX1Ow+5GBFTZle3Vh7ED1m2ntgT0pkf8PLUg0\n"
    "A7A3n34Dn/zsV1LKlnYvNxCqnv8bApGrHro47ysbZMJvzMzIWTG9+qYsnwaB1I1K\n"
    "sEoIdt4xCg+zY2sMRv87o4tfsPGuqrfT+Ll83OOIyBuLLWHKA/v1BeiYerXljJ1s\n"
    "mC33E39hHIBMHV0GyQpfM9adjeXlRz2Uoe5VQ9HrjiIYSUVcDVh1Z6EeBgCyICzp\n"
    "KhAld0Uo2YE1bgvHK3yQVLfszqYl1L/A2g/pFXQHQ3WZYBwVtivYHIr1w3oAM/OF\n"
    "j24Q60NwjDPUidtgffQkdXhv3s/8M2NBogGTgiAd9SFpN+BIXPLUyo5vH1Z11r2C\n"
    "Z1ysQAp2Hd4rKLnlANcdNflNBw52OWUdAgMBAAEwDQYJKoZIhvcNAQELBQADggIB\n"
    "AFFrbMhW+/aH6a2WaNy1MecFWIrzqJgKkGPZBjYETI/7Xu6MD7rqGPhPzGLSDvIS\n"
    "OrpY0i90gBxag/Zk4AE47porAmn0yIYcVjUdyOusplpOo1SzzPT4dwgUpusIao2p\n"
    "ggzZQBpMTP5r0wZj9vOZDFG9ZSA9Hteb5r2+wC0N7Nv0Vr4dEcxTtw2rnXk2WBs8\n"
    "0PGOD8oOFLpiFqhYP8S6wocIepy6CSTZyxUcJzW7PfrM5+ZdPSuLxEMtcD4zwV6u\n"
    "S1bvkRHHkGFJFsYjMg9WAdOEmHBZxQPak2b9F28RCUWhf9oLl87OwQw1qMf7Vzd7\n"
    "pEt1tROQHOfkgt/6eultQkQ8YbJJqrsQ2aOnznmpJDmzLpbHfPepCxz39gnyO4et\n"
    "YcClauIdCxNQ1ERLvdfA989HXG0yVzgjuVwIujI1ljSzyH7qVaQtbUW4xE4gBFtC\n"
    "6HhfKoafEWmkd8CMS/bcNTosVGgNVpblAGTkeIJfEo2xBm2bbvvAyKvTT2J5fJX7\n"
    "oKdyywleSdwQMOncovTjKSBKUvbQPY+dBlbzpxE6NNr7FBWjTaLIbaFwIhsozYTi\n"
    "VZdruu5D583qPEgAk/Iafrd0vksr7F5/Tjzn7wlswT4KcCN8HnEDs5VACVrULSNA\n"
    "XVfa0nrsWWrVXkBcKeSCC8ca2D/hd63h9SW4IeO2pSpa\n"
    "-----END CERTIFICATE-----\n";

static const char message[] = "Hyperledger Avalon";
    // SHA256: db684a8d3e33ef2bc1f03dd1a2cdbf4329226335f090921f24ef3d0dfe713ad4

static const char signature[] =
     // 512 byte, 4096 bit signature, b64 encoded in 684 bytes + NUL
    "AZzpz4BONyIclWHcOgm+GQ/dav5fyuXxl3vKXIZTXNLZX/dfVeGUQm5FBucrDLFy"
    "mE2RZ2ZrPpCW/RRP3SgAIPKduNNeiisBXrn2yuShiFGpqua29AYuTYG2Ut5mKUb6"
    "CNIFnWlOR3+f1eG8JXGoRefXTorwoaHkoCFttPNQG+Us4HKAeS4DifFmSkMq329M"
    "S4fGPXUYaRzibFjXksoC1R/DYdI7RNFjNE0Owmb6BC/ntBQiWB5CPcln1Rd17E41"
    "2MBRpVzPECId63rFQyCXEeMj9FxA1KoUgQgPGyif0msWdSBzxKMbET3YB/28Q8MD"
    "gR4qAyUSntuV0UrTZ82GAbhXYU4Ar7ZDZtiK8YS/et6goB6tIku0oaAbJYRs4G/+"
    "avCuLdVEy8Ndie+MeqksTuTSDYHMXW+phoKXU6qJcLs7BhZGRCqkzo+iuTcHXOjj"
    "oAK0FApiC+rBMMirgPmESR83U853tbGbUisN8Zud6R8mOBLbZQc4erMycFD9DYbB"
    "LqlG1EtBIzxKbSdzoT1/Gn9ha9ntjSM8ReO8GaXq08SxwB0TEFGe8K9Yp/UXsyXC"
    "BNZYwl4EUTGNchmhzOP/HsYt8Wb4nVbXnOVgevJK81x58nWn5Ne4j/xHAYDhP0A7"
    "cHxyJ8qv8CTlVcUZXKiYChhdZgXvrREPecK3BfT5AFM=";

// RSA-2048/SHA-256 IAS report signing cert valid 2016-2026, by ias_root_ca
static const char ias_report_signing_cert[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIEoTCCAwmgAwIBAgIJANEHdl0yo7CWMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV\n"
    "BAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV\n"
    "BAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0\n"
    "YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwHhcNMTYxMTIyMDkzNjU4WhcNMjYxMTIw\n"
    "MDkzNjU4WjB7MQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExFDASBgNVBAcMC1Nh\n"
    "bnRhIENsYXJhMRowGAYDVQQKDBFJbnRlbCBDb3Jwb3JhdGlvbjEtMCsGA1UEAwwk\n"
    "SW50ZWwgU0dYIEF0dGVzdGF0aW9uIFJlcG9ydCBTaWduaW5nMIIBIjANBgkqhkiG\n"
    "9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqXot4OZuphR8nudFrAFiaGxxkgma/Es/BA+t\n"
    "beCTUR106AL1ENcWA4FX3K+E9BBL0/7X5rj5nIgX/R/1ubhkKWw9gfqPG3KeAtId\n"
    "cv/uTO1yXv50vqaPvE1CRChvzdS/ZEBqQ5oVvLTPZ3VEicQjlytKgN9cLnxbwtuv\n"
    "LUK7eyRPfJW/ksddOzP8VBBniolYnRCD2jrMRZ8nBM2ZWYwnXnwYeOAHV+W9tOhA\n"
    "ImwRwKF/95yAsVwd21ryHMJBcGH70qLagZ7Ttyt++qO/6+KAXJuKwZqjRlEtSEz8\n"
    "gZQeFfVYgcwSfo96oSMAzVr7V0L6HSDLRnpb6xxmbPdqNol4tQIDAQABo4GkMIGh\n"
    "MB8GA1UdIwQYMBaAFHhDe3amfrzQr35CN+s1fDuHAVE8MA4GA1UdDwEB/wQEAwIG\n"
    "wDAMBgNVHRMBAf8EAjAAMGAGA1UdHwRZMFcwVaBToFGGT2h0dHA6Ly90cnVzdGVk\n"
    "c2VydmljZXMuaW50ZWwuY29tL2NvbnRlbnQvQ1JML1NHWC9BdHRlc3RhdGlvblJl\n"
    "cG9ydFNpZ25pbmdDQS5jcmwwDQYJKoZIhvcNAQELBQADggGBAGcIthtcK9IVRz4r\n"
    "Rq+ZKE+7k50/OxUsmW8aavOzKb0iCx07YQ9rzi5nU73tME2yGRLzhSViFs/LpFa9\n"
    "lpQL6JL1aQwmDR74TxYGBAIi5f4I5TJoCCEqRHz91kpG6Uvyn2tLmnIdJbPE4vYv\n"
    "WLrtXXfFBSSPD4Afn7+3/XUggAlc7oCTizOfbbtOFlYA4g5KcYgS1J2ZAeMQqbUd\n"
    "ZseZCcaZZZn65tdqee8UXZlDvx0+NdO0LR+5pFy+juM0wWbu59MvzcmTXbjsi7HY\n"
    "6zd53Yq5K244fwFHRQ8eOB0IWB+4PfM7FeAApZvlfqlKOlLcZL2uyVmzRkyR5yW7\n"
    "2uo9mehX44CiPJ2fse9Y6eQtcfEhMPkmHXI01sN+KwPbpA39+xOsStjhP9N1Y1a2\n"
    "tQAVo+yVgLgV2Hws73Fc0o3wC78qPEA+v2aRs/Be3ZFDgDyghc/1fgU+7C+P6kbq\n"
    "d4poyb6IW8KCJbxfMJvkordNOgOUUxndPHEi/tb/U7uLjLOgPA==\n"
    "-----END CERTIFICATE-----\n";

static const char mock_verification_report[] =
    "{\"nonce\":\"35E8FB64ACFB4A8E\","
    "\"id\":\"284773557701539118279755254416631834508\","
    "\"timestamp\":\"2018-07-11T19:30:35.556996\","
    "\"epidPseudonym\":\"2iBfFyk5LE9du4skK9JjlRh1x5RvCIz/Z2nnoViIYY8W8"
    "TmIHg53UlEm2sp8NYVgT+LGSp0oxZgFcIg4p0BWxXqoBEEDnJFaVxgw0fS/RfhtF8"
    "yVNbVQjYjgQjw06wPalXzzNnjFpb873Rycj3JKSzkR3KfvKZfA/CJqEkTZK7U=\","
    "\"isvEnclaveQuoteStatus\":\"GROUP_OUT_OF_DATE\","
    "\"platformInfoBlob\":\"150200650400070000080801010101000000000000"
    "0000000007000006000000020000000000000AE791776C1D5C169132CA96D56CC"
    "2D59E5A46F23E39933DFB3B4962A8608AB53D84F77D254627D906B46F08073D33"
    "FF511E74BC318E8E0C37483C5B08899D1B5E9F\","
    "\"isvEnclaveQuoteBody\":\"AgABAOcKAAAGAAUAAAAAAImTjvVbjrhQGXLFwbd"
    "tyMgAAAAAAAAAAAAAAAAAAAAABwf///8BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAMnL+UpC5HcF6MBCXsbYd"
    "5KUw2gc1tWgNPHNtK4g1NgKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "Cp0uDGT8avpUCoA1LU47KLt5L/RJSpeFFT9807MyvETgAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOeQAQAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAy7+"
    "m9Dx2rPbbbBWJUud3AHHnxoFWhlMQCyNjtVRvD2AAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAA\"}";

static const char mock_signature[] =
    "TuHse3QCPZtyZP436ltUAc6cVlIDzwKyjguOBDMmoou/NlGylzY0EtOEbHvVZ28H"
    "T8U1CiCVVmZso2ut2HY3zFDfpUg5/FV7FUSw/UhDOu3xkDwicrOvd/P1C3BKWJ6v"
    "JWghv3QLpgDItQPapFH/3OfciWs10kC3KV4UY+Irkrrck9+h3+FaltM/52AL1m1Q"
    "WZIutMk1gDs5nz5N87gGvbc9VJKXx/RDDmvX1rLfqnPpH3owkprVLhU8iLcmPPN+"
    "irjfH4f4GGrnbWYCYK5wfB1BBbFl8ppqxm4Gr8ekePCPLMjYYLpKYWEipvTgaYl6"
    "3zg+C9r8g+sIA3I9Jr3Exg==";


int
main(void)
{
    bool is_ok;
    int  count = 0;

#ifdef CRYPTOLIB_OPENSSL
#if OPENSSL_API_COMPAT < 0x10100000L
    OpenSSL_add_all_digests();
#endif
#endif

    printf("Verify RSA signature test . . . ");
    is_ok = verify_signature(test_cert,
        message, strlen(message),
        signature, strlen(signature));
    printf("rc=%d, %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
          ++count;

    printf("Verify RSA signature IAS report test . . . ");
    is_ok = verify_signature(ias_report_signing_cert,
        mock_verification_report, strlen(mock_verification_report),
        mock_signature, strlen(mock_signature));
    printf("rc=%d, %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
          ++count;

    printf("Verify RSA signature negative test (wrong cert) . . . ");
    is_ok = verify_signature(test_cert,
        mock_verification_report, strlen(mock_verification_report),
        mock_signature, strlen(mock_signature));
    printf("rc=%d, %s\n", (int)is_ok, is_ok ? "FAILED" : "PASSED");
    if (is_ok) // expected to fail, but did not
          ++count;

    // Summarize
    if (count == 0) {
        printf("RSA signature verification tests PASSED.\n");
    } else {
        printf("RSA signature verification FAILED %d tests.\n", count);
    }

    return count;
}
