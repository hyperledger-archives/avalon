#!/bin/bash

# ./encrypt-result --root-dir="" --result-file="" --key-file=""


for i in "$@"
do
	case $i in
		--root-dir=*)
		ROOT_DIR="${i#*=}"
		shift
		;;
		--result-file=*)
		RESULT_FILE="${i#*=}"
		shift
		;;
		--key-file=*)
		KEY_FILE="${i#*=}"
		shift
		;;
	esac
done

if [[ -z ${ROOT_DIR} ]]; then
    echo "[SHELL] no root directory specified"
    exit
fi

if [[ ! -f "${RESULT_FILE}" ]]; then
    echo "[SHELL] result file not found '${RESULT_FILE}'"
    exit
fi

if [[ ! -f "${KEY_FILE}" ]]; then
    echo "[SHELL] key file not found '${KEY_FILE}'"
	exit
fi

IEXEC_OUT="iexec_out"
AES_KEY_FILE=".iexec-tee-temporary-key"
IV_FILE=".iexec-tee-iv-key"
ENC_RESULT_FILE="result.zip.aes"
ENC_KEY_FILE="encrypted_key"
IV_LENGTH=16

cd ${ROOT_DIR}

case "$(uname -s)" in
    Linux*)     PUB_KEY_SIZE=$(openssl rsa -text -noout -pubin -in ${KEY_FILE} | head -n 1 | grep -o '[[:digit:]]*');;
    Darwin*)    PUB_KEY_SIZE=$(openssl rsa -text -noout -pubin -in ${KEY_FILE} | head -n 1 | egrep -o '[0-9]+');;
esac

echo "[SHELL] PUB_KEY_SIZE: ${PUB_KEY_SIZE}"

case ${PUB_KEY_SIZE} in
	2048)
		AES_KEY_SIZE=16 # 16 bytes = 128bits
		AES_ALG="-aes-128-cbc"
		;;
	4096)
		AES_KEY_SIZE=32 # 16 bytes = 128bits
		AES_ALG="-aes-256-cbc"
		;;
	*)
		echo "[SHELL] unsuported public key size"
		exit 1
		;;
esac

### GENERATE AES KEY
AES_KEY=$(openssl rand ${AES_KEY_SIZE} | tee ${AES_KEY_FILE} | od -An -tx1 | tr -d ' \n')
echo "[SHELL] generated AES_KEY"

### GENERATE IV
IV=$(openssl rand ${IV_LENGTH} | tee ${IV_FILE} | od -An -tx1 | tr -d ' \n')
echo "[SHELL] generated IV_KEY"

### ENCRYPT RESULT AND AES KEY
mv ${IV_FILE} ${IEXEC_OUT}/${ENC_RESULT_FILE} 2>&1
openssl enc ${AES_ALG} -K ${AES_KEY} -iv ${IV} -in ${RESULT_FILE} >> ${IEXEC_OUT}/${ENC_RESULT_FILE} 2>&1
openssl rsautl -encrypt -oaep -inkey ${KEY_FILE} -pubin -in ${AES_KEY_FILE} >> ${IEXEC_OUT}/${ENC_KEY_FILE} 2>&1
echo "[SHELL] encrypted result and key successfully"

### ZIP
zip -r ${IEXEC_OUT} ${IEXEC_OUT}/${ENC_RESULT_FILE} ${IEXEC_OUT}/${ENC_KEY_FILE} 2>&1

### SHRED KEY
shred -u ${AES_KEY_FILE} 2>&1
AES_KEY=""

### REMOVE TEMPORARY FILES
rm -f ${IEXEC_OUT}/${ENC_RESULT_FILE} 2>&1
rm -f ${IEXEC_OUT}/${ENC_KEY_FILE} 2>&1
rm -f ${AES_KEY_FILE} 2>&1

echo "[SHELL] encrypted result zipped to '${IEXEC_OUT}.zip'"