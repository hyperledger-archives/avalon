#pragma once

#include "work_order_data.h"
#include <map>

namespace cfl
{

struct WorkerMeasurement {
    ByteArray id;
    ByteArray mrenclave;
    ByteArray mrsigner;
    /*
     * isv_prod_id and isv_svn are 16-bits numbers. we use -1 to indicate that they are not specified.
     */
    int isv_prod_id;
    int isv_svn;
};


struct DatasetConfig
{
    ByteArray id;
    ByteArray data_owner_vkey;
    ByteArray data_ek;                              // encryption key
    ByteArray worker_mrenclave;
    ByteArray worker_mrsigner;              // reserved
    ByteArray worker_vkey;
};

struct GrapheneWorker
{
    ByteArray id;
    ByteArray worker_mrenclave;
    ByteArray worker_mrsigner;     
    int isv_prod_id;
    int isv_svn;
    ByteArray worker_vkey;
    ByteArray worker_ekey;
    ByteArray worker_addr;                  // TODO: remove this when block chain is enabled
    ByteArray extra_specs;
};

struct AvalonWorker
{
    ByteArray id;
    ByteArray worker_mrenclave;
    ByteArray worker_mrsigner;             
    int isv_prod_id;
    int isv_svn;
    ByteArray worker_vkey;
    ByteArray data_owner_vkey;
    std::map<ByteArray, GrapheneWorker> children;
};


const int NONCE_LENGTH = 32;

ByteArray TransformBase64ByteArray(const ByteArray& data);

ByteArray TransformHexByteArray(const ByteArray& data);

int TransformByteArrayToInteger(const ByteArray& data);

std::string VerificationKeyBlockFromByteArray(const ByteArray& vkey);

std::string AddBeginEndBlockToVerificationKey(const std::string& vkey_base64);

bool GenerateNonce(ByteArray& nonce);

void Split(std::string str, std::vector<std::string>& result);

} //namespace cfl;
