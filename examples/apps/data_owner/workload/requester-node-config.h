#pragma once

#include <map>
#include "cfl-utils.h"
#include "cfl-poc-defs.h"
#include "requester-node-logic.h"

namespace CflPocRequester {

const size_t VERIFICATION_KEY_SIZE = 88;

// The class below is a placeholder to be extended later

// TODO: hardcode const data owner verification keys to use for RequesterNodeConfig::setting up data_owner_vkeys

class RequesterNodeConfig
{
public:
    friend RequesterProcessor;


    RequesterNodeConfig() { }

    virtual ~RequesterNodeConfig() { }

    virtual void AddWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                           ExWorkorderInfo* wo_info);

    virtual void RemoveWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                              ExWorkorderInfo* wo_info);

    virtual void LookupWorkers(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                               std::vector<tcf::WorkOrderData>& out_work_order_data,
                               ExWorkorderInfo* wo_info);

    virtual void UpdateGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info);

    virtual void AddDataset(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                            std::vector<tcf::WorkOrderData>& out_work_order_data,
                            ExWorkorderInfo* wo_info);
    
    virtual void RemoveDataset(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                               std::vector<tcf::WorkOrderData>& out_work_order_data,
                               ExWorkorderInfo* wo_info); 

    virtual void LookupDatasets(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                std::vector<tcf::WorkOrderData>& out_work_order_data,
                                ExWorkorderInfo* wo_info);

    virtual void AddUser(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                         std::vector<tcf::WorkOrderData>& out_work_order_data,
                         ExWorkorderInfo* wo_info);
    
    virtual void RemoveUser(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                           ExWorkorderInfo* wo_info);

    virtual void LookupUsers(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                             std::vector<tcf::WorkOrderData>& out_work_order_data, 
			     ExWorkorderInfo* wo_info);
    
    virtual bool GetDatasetByVkey(const ByteArray& user_vkey, const ByteArray& dataset_id, ByteArray& dataset_ek);

    virtual bool CheckUserVkey(const ByteArray& user_vkey);

    virtual bool CheckAvalonWorkerOwner(const ByteArray& avalon_vkey, const ByteArray& data_owner_vkey);

    virtual bool CheckGrapheneWorkerParent(const ByteArray& graphene_vkey, const ByteArray& avalon_vkey);

    virtual std::string AvailableDatasets(const ByteArray& user_vkey);

    virtual bool GetDatasetByWorkerAttastation(const ByteArray& attestation, const ByteArray& dataset_id, ByteArray& dataset_ek)
    {
        // TODO: add impleentation
        return false;
    };


protected:
    virtual bool CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey);
        
    virtual bool CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey);

    virtual bool VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo);

    virtual std::string TranslateDatasets(const ByteArray& data_owner_vkey);

    virtual std::string TranslateUserVKeys(const ByteArray& data_owner_vkey);

    std::string TranslateDataset(const cfl::DatasetConfig& d);

    virtual void AddAvalonWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                 std::vector<tcf::WorkOrderData>& out_work_order_data,
                                 ExWorkorderInfo* wo_info);

    virtual void AddGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                   std::vector<tcf::WorkOrderData>& out_work_order_data,
                                   ExWorkorderInfo* wo_info);

    virtual void RemoveAvalonWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                    std::vector<tcf::WorkOrderData>& out_work_order_data,
                                    ExWorkorderInfo* wo_info);

    virtual void RemoveGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info);

    virtual std::string TranslateWorkerInfo();

    virtual std::string TranslateAvalonWorker(const cfl::AvalonWorker& worker);

    virtual std::string TranslateGrapheneWorker(const std::map<ByteArray, cfl::GrapheneWorker>& workers, const cfl::AvalonWorker& parent);

    virtual std::string TranslateGrapheneWorker(const cfl::GrapheneWorker& worker, const cfl::AvalonWorker& parent);
   

    std::map<ByteArray, cfl::DatasetConfig> dataset_map;
    std::map<ByteArray, std::map<ByteArray, int>> user_map;
    std::map<ByteArray, cfl::AvalonWorker> worker_map;
};

} //namespace CflPocRequester
