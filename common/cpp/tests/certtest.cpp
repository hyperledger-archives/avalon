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
 * Test cert chain verification in verify_certificate.cpp.
 *
 * # Script to generate test certs:
 * # Create ca key
 * openssl genrsa -des3 -out rootCA.key 4096
 * # Sign CA
 * openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 15000 \
 *     -out rootCA.pem
 * # Create key
 * openssl genrsa -out avalon.key 4096
 * # Create CSR
 * openssl req -new -key avalon.key -out avalon.csr
 * # Generate cert
 * openssl x509 -req -in avalon.csr -CA rootCA.pem -CAkey rootCA.key
 *     -CAcreateserial -days 14999 -sha256 -out test.pem
 * # Verify self-signed cert
 * openssl verify -CAfile rootCA.pem test.pem
 */

#include <stdio.h>

#include "crypto_shared.h" // Sets default CRYPTOLIB_* value
#ifdef CRYPTOLIB_OPENSSL
#include <openssl/evp.h>
#endif
#include "verify_certificate.h"


// Test X.509 certificates
// To dump, type: openssl x509 -noout -text <mycertfilename.pem
// CA test cert, RSA-4096/SHA-256 2020-2061
static const char ca_cert[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIGPTCCBCWgAwIBAgIUGjmtT+zvFaxWgQve5kc/Sn+RTZUwDQYJKoZIhvcNAQEL\n"
    "BQAwgawxCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJPUjETMBEGA1UEBwwKTGFrZSBH\n"
    "cm92ZTEbMBkGA1UECgwSSHlwZXJsZWRnZXIgQXZhbG9uMRAwDgYDVQQLDAdUZXN0\n"
    "IENBMSIwIAYDVQQDDBljYS5hdmFsb24uaHlwZXJsZWRnZXIub3JnMSgwJgYJKoZI\n"
    "hvcNAQkBFhljYUBhdmFsb24uaHlwZXJsZWRnZXIub3JnMCAXDTIwMDQyODIxMjcy\n"
    "OVoYDzIwNjEwNTIzMjEyNzI5WjCBrDELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk9S\n"
    "MRMwEQYDVQQHDApMYWtlIEdyb3ZlMRswGQYDVQQKDBJIeXBlcmxlZGdlciBBdmFs\n"
    "b24xEDAOBgNVBAsMB1Rlc3QgQ0ExIjAgBgNVBAMMGWNhLmF2YWxvbi5oeXBlcmxl\n"
    "ZGdlci5vcmcxKDAmBgkqhkiG9w0BCQEWGWNhQGF2YWxvbi5oeXBlcmxlZGdlci5v\n"
    "cmcwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCaGNp8JOVeBzT5zaVx\n"
    "wUkvRSNAuDE+a4pf3s/BUPBiW2vA/ARYdNkkb6W8KIw5DePlPsppPoMNfumNkXLL\n"
    "PUDgd/TnR7e7OO7gSN9XvpYzmFtGNqqDu7K5NtUn5AFGb6b4/YGKd1bRrhnmoSHv\n"
    "dRadmupfI0Nt4ABz/Yu60+1CVGES83NYGJPZtQwwA+CrUZadckS7ps4YqWNeuDxY\n"
    "O8CC/9lYyOKg+Fa9GW65mX3WR404Y/SL2VEoKKYaW6l/fO69XKPQO9pmyJa3zFJ5\n"
    "Hwswur0L5Pq6E+avf0hBKqkTM4OeShaVxMXGG+v5yMp5rgteRao9jiLDEGP5Im2H\n"
    "xaIK5hl4S+0AY8pM0lM2rFlrXz49VcjDw7BwOTyUGbtnd65GyIuzk1JIyhMZ68oc\n"
    "MkyxH7bHCJWlFEZNVwKPf4E2SlagpN5oqvwIAgXQammITKPttkhT6CpSwpyTNWYR\n"
    "MYQfsZTtUq9T31bKS4QKoxAqmWkBiN+J1gPDqFyxLoRI1FF9hdhLWwEYXSlZjlry\n"
    "u6XzUzJTsKrJ/rFBRL832S+32esMSlVgpWzpJvZFx3qBqLnuWdYOtjcnFg2mEbiC\n"
    "RT3iHkP9BD10nAyeQjJNHYwpznAG952XaL2jDDmor+qYo9vZfNHLhzglXb+ucCVj\n"
    "nJdaD/qzOt0cgRZTvfF8ZdVfcQIDAQABo1MwUTAdBgNVHQ4EFgQULQbLYP/USzHV\n"
    "mJxG1rGPByYGWyswHwYDVR0jBBgwFoAULQbLYP/USzHVmJxG1rGPByYGWyswDwYD\n"
    "VR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEAfi5fNkgZHGIq5IVsXLWb\n"
    "llJZZPWbgjcbfAiJdmwCGdtq/gW+nPmTjFazCzJWzvjzt4Oc2PcRESIgsg0A5hO+\n"
    "My7wL5JUwZqjp/1kiloXVXIezHsrjwtr1ZbhIuhEXovEsdBJ+tZ1QyDXEDMlkxf8\n"
    "iBsbGl9XP18elfy41htzzZyncQtjPv6P8RpajSsKl5rEBmJ03rjqKnMfLvjizte8\n"
    "wDDDW6nrx+DCYvxrCzP2cbnaTYX6IXmfjYqJ8xsPI8qE9rs/nenx4V4hNkWaA75b\n"
    "spqLlWE9ZB/LJPc2UUqAG7wvHp7MUH2YpIeT/kWAxEilq4kbH1vea1Nd/OS6WcL7\n"
    "TICed4wzMrveIOiCJ4jMz8XwAG6gifGf7wp+1XTW6ydVKQxozvdhn7Cb803EUztR\n"
    "WH7Pyw3O/np0OYtrpzYDOQVj0nenysM9EDQG3MTbkYoYjDIvNVGIkD0QWbpiBSTs\n"
    "DlozLFEJjtn2lMnGiKCSYoO89m7bxCpwB03k6dX1B+3hf255RwgfOgnKIEoxuDPw\n"
    "YWkZtrlSzs0gsIDALv1JjP9GDq1rGHLufffps0sS578QSalIV0g4Sn5mb8e/4ENn\n"
    "c2QVvqDBQJde2uIsObltrvZe/Q1sPvUf5Rn3iLBWPMUog4+oEp9/Vk9E4Ap7vdve\n"
    "qu0rY0kiCKHRB5M7powyzSc=\n"
    "-----END CERTIFICATE-----\n";

// RSA-4096/SHA-256 test cert valid 2020-2061, issued by ca_cert
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

// RSA-3072/SHA-256 Root CA cert valid 2016-2049
static const char ias_root_ca[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIFSzCCA7OgAwIBAgIJANEHdl0yo7CUMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV\n"
    "BAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV\n"
    "BAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0\n"
    "YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwIBcNMTYxMTE0MTUzNzMxWhgPMjA0OTEy\n"
    "MzEyMzU5NTlaMH4xCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwL\n"
    "U2FudGEgQ2xhcmExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQD\n"
    "DCdJbnRlbCBTR1ggQXR0ZXN0YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwggGiMA0G\n"
    "CSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCfPGR+tXc8u1EtJzLA10Feu1Wg+p7e\n"
    "LmSRmeaCHbkQ1TF3Nwl3RmpqXkeGzNLd69QUnWovYyVSndEMyYc3sHecGgfinEeh\n"
    "rgBJSEdsSJ9FpaFdesjsxqzGRa20PYdnnfWcCTvFoulpbFR4VBuXnnVLVzkUvlXT\n"
    "L/TAnd8nIZk0zZkFJ7P5LtePvykkar7LcSQO85wtcQe0R1Raf/sQ6wYKaKmFgCGe\n"
    "NpEJUmg4ktal4qgIAxk+QHUxQE42sxViN5mqglB0QJdUot/o9a/V/mMeH8KvOAiQ\n"
    "byinkNndn+Bgk5sSV5DFgF0DffVqmVMblt5p3jPtImzBIH0QQrXJq39AT8cRwP5H\n"
    "afuVeLHcDsRp6hol4P+ZFIhu8mmbI1u0hH3W/0C2BuYXB5PC+5izFFh/nP0lc2Lf\n"
    "6rELO9LZdnOhpL1ExFOq9H/B8tPQ84T3Sgb4nAifDabNt/zu6MmCGo5U8lwEFtGM\n"
    "RoOaX4AS+909x00lYnmtwsDVWv9vBiJCXRsCAwEAAaOByTCBxjBgBgNVHR8EWTBX\n"
    "MFWgU6BRhk9odHRwOi8vdHJ1c3RlZHNlcnZpY2VzLmludGVsLmNvbS9jb250ZW50\n"
    "L0NSTC9TR1gvQXR0ZXN0YXRpb25SZXBvcnRTaWduaW5nQ0EuY3JsMB0GA1UdDgQW\n"
    "BBR4Q3t2pn680K9+QjfrNXw7hwFRPDAfBgNVHSMEGDAWgBR4Q3t2pn680K9+Qjfr\n"
    "NXw7hwFRPDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBADANBgkq\n"
    "hkiG9w0BAQsFAAOCAYEAeF8tYMXICvQqeXYQITkV2oLJsp6J4JAqJabHWxYJHGir\n"
    "IEqucRiJSSx+HjIJEUVaj8E0QjEud6Y5lNmXlcjqRXaCPOqK0eGRz6hi+ripMtPZ\n"
    "sFNaBwLQVV905SDjAzDzNIDnrcnXyB4gcDFCvwDFKKgLRjOB/WAqgscDUoGq5ZVi\n"
    "zLUzTqiQPmULAQaB9c6Oti6snEFJiCQ67JLyW/E83/frzCmO5Ru6WjU4tmsmy8Ra\n"
    "Ud4APK0wZTGtfPXU7w+IBdG5Ez0kE1qzxGQaL4gINJ1zMyleDnbuS8UicjJijvqA\n"
    "152Sq049ESDz+1rRGc2NVEqh1KaGXmtXvqxXcTB+Ljy5Bw2ke0v8iGngFBPqCTVB\n"
    "3op5KBG3RjbF6RRSzwzuWfL7QErNC8WEy5yDVARzTA5+xmBc388v9Dm21HGfcC8O\n"
    "DD+gT9sSpssq0ascmvH49MOgjt1yoysLtdCtJW/9FZpoOypaHx0R+mJTLwPXVMrv\n"
    "DaVzWh5aiEx+idkSGMnX\n"
    "-----END CERTIFICATE-----\n";

// RSA-2048/SHA-256 CA cert valid 2016-2026, issued by ias_root_ca
static const char ias_child_ca[] =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIFSzCCA7OgAwIBAgIJANEHdl0yo7CUMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV\n"
    "BAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV\n"
    "BAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0\n"
    "YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwIBcNMTYxMTE0MTUzNzMxWhgPMjA0OTEy\n"
    "MzEyMzU5NTlaMH4xCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwL\n"
    "U2FudGEgQ2xhcmExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQD\n"
    "DCdJbnRlbCBTR1ggQXR0ZXN0YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwggGiMA0G\n"
    "CSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCfPGR+tXc8u1EtJzLA10Feu1Wg+p7e\n"
    "LmSRmeaCHbkQ1TF3Nwl3RmpqXkeGzNLd69QUnWovYyVSndEMyYc3sHecGgfinEeh\n"
    "rgBJSEdsSJ9FpaFdesjsxqzGRa20PYdnnfWcCTvFoulpbFR4VBuXnnVLVzkUvlXT\n"
    "L/TAnd8nIZk0zZkFJ7P5LtePvykkar7LcSQO85wtcQe0R1Raf/sQ6wYKaKmFgCGe\n"
    "NpEJUmg4ktal4qgIAxk+QHUxQE42sxViN5mqglB0QJdUot/o9a/V/mMeH8KvOAiQ\n"
    "byinkNndn+Bgk5sSV5DFgF0DffVqmVMblt5p3jPtImzBIH0QQrXJq39AT8cRwP5H\n"
    "afuVeLHcDsRp6hol4P+ZFIhu8mmbI1u0hH3W/0C2BuYXB5PC+5izFFh/nP0lc2Lf\n"
    "6rELO9LZdnOhpL1ExFOq9H/B8tPQ84T3Sgb4nAifDabNt/zu6MmCGo5U8lwEFtGM\n"
    "RoOaX4AS+909x00lYnmtwsDVWv9vBiJCXRsCAwEAAaOByTCBxjBgBgNVHR8EWTBX\n"
    "MFWgU6BRhk9odHRwOi8vdHJ1c3RlZHNlcnZpY2VzLmludGVsLmNvbS9jb250ZW50\n"
    "L0NSTC9TR1gvQXR0ZXN0YXRpb25SZXBvcnRTaWduaW5nQ0EuY3JsMB0GA1UdDgQW\n"
    "BBR4Q3t2pn680K9+QjfrNXw7hwFRPDAfBgNVHSMEGDAWgBR4Q3t2pn680K9+Qjfr\n"
    "NXw7hwFRPDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBADANBgkq\n"
    "hkiG9w0BAQsFAAOCAYEAeF8tYMXICvQqeXYQITkV2oLJsp6J4JAqJabHWxYJHGir\n"
    "IEqucRiJSSx+HjIJEUVaj8E0QjEud6Y5lNmXlcjqRXaCPOqK0eGRz6hi+ripMtPZ\n"
    "sFNaBwLQVV905SDjAzDzNIDnrcnXyB4gcDFCvwDFKKgLRjOB/WAqgscDUoGq5ZVi\n"
    "zLUzTqiQPmULAQaB9c6Oti6snEFJiCQ67JLyW/E83/frzCmO5Ru6WjU4tmsmy8Ra\n"
    "Ud4APK0wZTGtfPXU7w+IBdG5Ez0kE1qzxGQaL4gINJ1zMyleDnbuS8UicjJijvqA\n"
    "152Sq049ESDz+1rRGc2NVEqh1KaGXmtXvqxXcTB+Ljy5Bw2ke0v8iGngFBPqCTVB\n"
    "3op5KBG3RjbF6RRSzwzuWfL7QErNC8WEy5yDVARzTA5+xmBc388v9Dm21HGfcC8O\n"
    "DD+gT9sSpssq0ascmvH49MOgjt1yoysLtdCtJW/9FZpoOypaHx0R+mJTLwPXVMrv\n"
    "DaVzWh5aiEx+idkSGMnX\n"
    "-----END CERTIFICATE-----\n";

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

    printf("Verify CA test . . . ");
    is_ok = verify_certificate_chain(ca_cert, ca_cert);
    printf("%d %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
        ++count;

    printf("Verify real CA test . . . ");
    is_ok = verify_certificate_chain(ias_child_ca, ias_root_ca);
    printf("%d %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
        ++count;

    printf("Verify IAS CA test . . . ");
    is_ok = verify_certificate_chain(ias_report_signing_cert, ias_root_ca);
    printf("%d %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
        ++count;

    printf("Verify cert test . . . ");
    is_ok = verify_certificate_chain(test_cert, ca_cert);
    printf("%d %s\n", (int)is_ok, is_ok ? "PASSED" : "FAILED");
    if (!is_ok)
        ++count;

    printf("Verify cert negative test . . . ");
    is_ok = verify_certificate_chain(test_cert, test_cert2);
    printf("%d %s\n", (int)!is_ok, is_ok ? "FAILED" : "PASSED");
    if (is_ok) // should not succeed; success is failure for this test
        ++count;

    // Summarize
    if (count == 0) {
        printf("Verify certificate chain tests PASSED.\n");
    } else {
        printf("Verify certificate chain FAILED %d tests.\n", count);
    }
    return count;
}
