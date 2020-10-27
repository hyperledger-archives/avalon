#pragma once

#include <map>
#include "cfl-poc-defs.h"

namespace CflPocRequester {

class RequesterProcessor
{
public:
    struct DatasetInfo
    {
        ByteArray dataset_id;
        ByteArray processing_result;
        ByteArray workorder_id;
        ByteArray workorder_nonce;
        ByteArray workorder_ek;
        DatasetInfo() {};
        virtual ~DatasetInfo() {};
    };

    struct WorkflowInfo
    {
        ByteArray workflow_id;
        ByteArray data_owner_vkey;
	std::map<ByteArray, ByteArray> joined_workers;
	int status;
	ByteArray workflow_result;
        WorkflowInfo() {};
        virtual ~WorkflowInfo() {};
    };

    virtual void CreateWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                std::vector<tcf::WorkOrderData>& out_work_order_data,
                                ExWorkorderInfo* wo_info);
    
    virtual void JoinWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                              ExWorkorderInfo* wo_info);
    
    virtual void QuitWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                              ExWorkorderInfo* wo_info);

    virtual void UpdateWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                std::vector<tcf::WorkOrderData>& out_work_order_data,
                                ExWorkorderInfo* wo_info);

    virtual void LookupWorkflows(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                 std::vector<tcf::WorkOrderData>& out_work_order_data,
                                 ExWorkorderInfo* wo_info);
    
    virtual void GetWorkflowResult(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                   std::vector<tcf::WorkOrderData>& out_work_order_data,
                                   ExWorkorderInfo* wo_info);
    
    virtual void RemoveWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                std::vector<tcf::WorkOrderData>& out_work_order_data,
                                ExWorkorderInfo* wo_info);

    virtual void AvailableDatasets(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                   std::vector<tcf::WorkOrderData>& out_work_order_data,
                                   ExWorkorderInfo* wo_info);

    virtual void CreateNonceRequest(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                    std::vector<tcf::WorkOrderData>& out_work_order_data,
                                    ExWorkorderInfo* wo_info);
    
    virtual void CreateProcessDatasetRequest(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                             std::vector<tcf::WorkOrderData>& out_work_order_data,
                                             ExWorkorderInfo* wo_info);
    
    virtual void ProcessDatasetResult(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info);

    virtual bool IsWorkerActive(const ByteArray& worker_vkey);
   
protected:
    virtual bool CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey);

    virtual bool CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey);

    virtual bool VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo);

    virtual int ParseDoNonceResult(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, const ByteArray& json_result, ByteArray nonce);
    
    virtual int CreateProcessDatasetRequest(ExWorkorderInfo* wo_info, 
                                            const ByteArray& work_flow_id,
                                            const ByteArray& nonce,
                                            const ByteArray& dataset_id,
                                            const ByteArray& dataset_ek,
                                            const ByteArray& query_data,
                                            ByteArray& json_request);
   
    virtual int ParseProcessDatasetResult(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, const ByteArray& json_result);

    virtual bool CheckWorkflowOwner(const ByteArray& data_owner_vkey, const ByteArray& workflow_id);

    virtual bool CheckUser(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, ByteArray& user_vkey);
    
    virtual bool GetUserVkey(ExWorkorderInfo* wo_info, ByteArray& user_vkey);
    
    virtual void AggregateData(const ByteArray& workflow_id, ByteArray& result);
   
    virtual bool AddWorkflow(const ByteArray& user_vkey, ByteArray& workflow_id);
    
    virtual int CreateGetNonceWoRequest(ExWorkorderInfo* wo_info,
                                        const ByteArray& attestation_data, const ByteArray& workflow_id,
                                        const ByteArray& dataset_id,
                                        ByteArray& json_request);
   

    virtual bool CheckDatasetAccess(const ByteArray& workflow_id, const ByteArray& user_vkey, const ByteArray& dataset_id, ByteArray& dataset_ek);

    virtual std::string TranslateWorkflowInfo();

    virtual std::string TranslateWorkflowInfo(const ByteArray& user_vkey);

    virtual std::string TranslateWorkflowInfo(const WorkflowInfo& workflow);

    virtual std::string TranslateBriefWorkflowWorkers(const WorkflowInfo& workflow);

    virtual std::string TranslateDetailedWorkflowWorkers(const WorkflowInfo& workflow);

    virtual bool JoinedWorkflow(const ByteArray& user_vkey, const WorkflowInfo& workflow);
    

    static std::map<ByteArray, WorkflowInfo> workflow_map;
};


} //namespace CflPocRequester
