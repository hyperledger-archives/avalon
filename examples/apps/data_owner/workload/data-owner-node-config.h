#pragma once

#include <map>
#include "cfl-poc-defs.h"

namespace CflPocDataOwner {

// The class below is a placeholder to be extended later

// TODO: hardcode const data owner verification keys to use for RequesterNodeConfig::setting up data_owner_vkeys
//


class DataOwnerNodeConfig
{
public:
    
    DataOwnerNodeConfig() {}

    virtual ~DataOwnerNodeConfig(){};

    virtual void SetupWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                           ExWorkorderInfo* wo_info);

    virtual void RemoveWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                              ExWorkorderInfo* wo_info);

    virtual void AddWorkerMeasurement(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info);

    virtual void RemoveWorkerMeasurement(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                         std::vector<tcf::WorkOrderData>& out_work_order_data,
                                         ExWorkorderInfo* wo_info);

    virtual void LookupWorkerMeasurements(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                          std::vector<tcf::WorkOrderData>& out_work_order_data,
                                          ExWorkorderInfo* wo_info);

    virtual void SealEncryptionKey(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                   std::vector<tcf::WorkOrderData>& out_work_order_data,
                                   ExWorkorderInfo* wo_info);

    virtual void UnsealEncryptionKey(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                     std::vector<tcf::WorkOrderData>& out_work_order_data,
                                     ExWorkorderInfo* wo_info);

    const std::vector<cfl::WorkerMeasurement>& GetWorkerMeasurements() { return worker_measurements; }

    virtual bool CheckUserVkey(const ByteArray& user_vkey);


protected:
    virtual bool CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey);
        
    virtual bool CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey);

    virtual bool VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo);

    virtual std::string TranslateWorkerMeasurements();
    virtual std::string TranslateWorkerMeasurement(const cfl::WorkerMeasurement& worker_meas);

    std::vector<cfl::WorkerMeasurement> worker_measurements;
    std::map<ByteArray, cfl::GrapheneWorker> children;
};

} //namespace CflPocDataOwner
