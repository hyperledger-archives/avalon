#!/bin/bash

# ./decrypt-dataset.sh <dataset-file> <secret-file>


ENC_DATA_FILE="$1"
DEC_DATA_FILE="$1.recovered"
SECRET_FILE="$2"
KEY_FILE="$2.keybin"

if [[ ! -f "${ENC_DATA_FILE}" ]]; then
	echo "[SHELL] encrypted dataset file not found '${RESULT_FILE}'"
	exit
fi

if [[ ! -f "${SECRET_FILE}" ]]; then
	echo "[SHELL] dataset secret file not found '${KEY_FILE}'"
	exit
fi

openssl base64 -d -in ${SECRET_FILE} -out ${KEY_FILE} 2>&1
echo "[SHELL] converted secret file from base64 to bin format"

case "$(uname -s)" in
    Linux*)     openssl enc -d -aes-256-cbc -pbkdf2 -in ${ENC_DATA_FILE} -out ${DEC_DATA_FILE} -kfile ${KEY_FILE} 2>&1;;
    Darwin*)    openssl enc -d -aes-256-cbc -in ${ENC_DATA_FILE} -out ${DEC_DATA_FILE} -kfile ${KEY_FILE} 2>&1;;
esac


echo "[SHELL] decrypted dataset file"

shred -u ${KEY_FILE} 2>&1
rm -f ${KEY_FILE} 2>&1
rm -f ${SECRET_FILE} 2>&1

echo "[SHELL] ended with success"

decryptFile $1 $2