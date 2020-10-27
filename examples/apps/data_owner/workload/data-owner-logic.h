//
// CFL POC: logic.h
// Data owner workload logic definition and inline implementation
//

//
// This a skeleton (pseudo_code) to serve as a reference for actual implementation
//


#pragma once

#include <map>
#include <list>
#include "data-owner-plug-in.h"

namespace CflPocDataOwner {

const size_t VERIFICATION_KEY_SIZE = 88;

struct RequesterInfo
{
    ByteArray id;
    ByteArray mrenclave;
    ByteArray mrsigner;
    ByteArray verification_key;
};

// The class below is a placeholder to be extended later
// The class below is a placeholder to be extended later
// TODO: add nonce generation in a way similar to RequesterNodeConfig class
class RequesterList
{
public:
    RequesterList() { }

    virtual ~RequesterList() { }
   
    virtual void SetupRequesterEnclave(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                       std::vector<tcf::WorkOrderData>& out_work_order_data,
                                       ExWorkorderInfo* exWorkorderInfo);

    virtual void RemoveRequesterEnclave(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* exWorkorderInfo);

    virtual void LookupRequesterEnclaves(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                         std::vector<tcf::WorkOrderData>& out_work_order_data,
                                         ExWorkorderInfo* exWorkorderInfo);
    
    virtual std::vector<RequesterInfo>& GetRequesters()
    {
        return requesters;
    }

protected:
    virtual bool CheckDataOwner(ExWorkorderInfo* exWorkorderInfo, ByteArray& data_owner_vkey);

    virtual bool CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey);

    virtual bool VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo);

    virtual std::string TranslateJSONResultOfRequesters();


    std::vector<RequesterInfo> requesters;
};


class DataOwnerProcessor
{
public:
    DataOwnerProcessor();

    virtual ~DataOwnerProcessor() {}

 
    // TODO: Change nonce name to something else like ekey, beacuse it is actually pablic RSA key
    virtual void CreateNonce(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                             std::vector<tcf::WorkOrderData>& out_work_order_data,
			     ExWorkorderInfo* exWorkorderInfo,
                             const RequesterList& rlist);

    virtual void Process(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                         std::vector<tcf::WorkOrderData>& out_work_order_data,
			 ExWorkorderInfo* exWorkorderInfo);
   
    // TODO: Uncomment the function below when exWorkorderInfo is available in tcf::Workload class
    //virtual void SetExtendedWoroderInfoApi(tcf::ExWorkorderInfo* _exWorkorderInfo)
    //{
    //    exWorkorderInfo = _exWorkorderInfo;
    //};


protected:
    virtual bool CheckNonce(ExWorkorderInfo* exWorkorderInfo, const ByteArray& nonce, const ByteArray& vkey_sig);

    virtual bool RemoveNonce(const ByteArray& nonce);

    virtual bool GenerateNonce(ByteArray& nonce_vkey, ByteArray& skey);
    
    virtual bool VerifyRequestor(ExWorkorderInfo* exWorkorderInfo, ByteArray& attestation_data, const RequesterList& rlist);

    virtual bool PrepareDataset(const ByteArray& dataset_name, const ByteArray& dataset_key, const ByteArray& nonce);

    virtual bool ProcessQuery(const ByteArray& query_data, std::string& value);

    virtual bool VerifyDataSet(const ByteArray& dataset_id);

     
    std::map<std::string, std::vector<std::string>> dataset_map;
    std::string dataset_name_str;

    static std::map<ByteArray, ByteArray> nonce_map;


    // TODO: Uncomment the line below exWorkorderInfo is available in tcf::Workload class
    // tcf::ExWorkorderInfo* exWorkorderInfo;
};


}//namespace CflPocDataOwner

