#include <sgx_trts.h>
#include "cfl-utils.h"

namespace cfl
{

ByteArray TransformBase64ByteArray(const ByteArray& data)
{
    std::string base64_str = ByteArrayToString(data);
    if (base64_str.size() == 0 || base64_str == "null")
    {
	return ByteArray();  //empty
    }
    return Base64EncodedStringToByteArray(base64_str);

}

ByteArray TransformHexByteArray(const ByteArray& data)
{
    std::string hex_str = ByteArrayToString(data);
    if (hex_str.size() == 0 || hex_str == "null")
    {
        return ByteArray();  //empty
    }
    return HexEncodedStringToByteArray(hex_str);

}

int TransformByteArrayToInteger(const ByteArray& data)
{
    std::string str =  ByteArrayToString(data);
    return std::stoi(str);
}


std::string VerificationKeyBlockFromByteArray(const ByteArray& vkey)
{
    std::string vkey_base64 = ByteArrayToBase64EncodedString(vkey);
    return AddBeginEndBlockToVerificationKey(vkey_base64);
}


std::string AddBeginEndBlockToVerificationKey(const std::string& vkey_base64)
{
    std::string block = "-----BEGIN PUBLIC KEY-----\n";
    size_t vkey_len = vkey_base64.size();
    for(size_t i = 0; i < vkey_len; i += 64)
    {
        block += vkey_base64.substr(i, 64);
        block += "\n";
    }
    block += "-----END PUBLIC KEY-----\n";
    return block;

}


bool GenerateNonce(ByteArray& nonce) {
    uint8_t id[NONCE_LENGTH];
    sgx_status_t status = sgx_read_rand(reinterpret_cast<unsigned char*>(id), sizeof(id));
    if (status != SGX_SUCCESS) {
        return false;
    }
    else {
        nonce.assign(id, id + NONCE_LENGTH);
	return true;
    }
}


void Split(std::string str, std::vector<std::string>& result) {
    char *saved_ptr;

    char *token = strtok_r((char *)str.c_str(), " ", &saved_ptr);
    while (token) {
         result.push_back(token);
         token = strtok_r(NULL, " ", &saved_ptr);
    }
}


} //namespace cfl;
