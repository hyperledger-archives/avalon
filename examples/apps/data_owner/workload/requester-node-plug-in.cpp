//
// CFL POC: requester-node-plug-in.cpp
// Workload registration and entry point
//

#include "requester-node-config.h"
#include "requester-node-logic.h"
#include "requester-node-plug-in.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"

using namespace cfl;

typedef CflPocRequester::Requester RequesterAddDataset;
typedef CflPocRequester::Requester RequesterRemoveDataset;
typedef CflPocRequester::Requester RequesterLookupDatasets;
typedef CflPocRequester::Requester RequesterAddWorker;
typedef CflPocRequester::Requester RequesterRemoveWorker;
typedef CflPocRequester::Requester RequesterUpdateWorker;
typedef CflPocRequester::Requester RequesterLookupWorkers;
typedef CflPocRequester::Requester RequesterAddUser;
typedef CflPocRequester::Requester RequesterRemoveUser;
typedef CflPocRequester::Requester RequesterLookupUsers;
typedef CflPocRequester::Requester RequesterCreateWorkflow;
typedef CflPocRequester::Requester RequesterJoinWorkflow;
typedef CflPocRequester::Requester RequesterQuitWorkflow;
typedef CflPocRequester::Requester RequesterUpdateWorkflow;
typedef CflPocRequester::Requester RequesterLookupWorkflows;
typedef CflPocRequester::Requester RequesterRemoveWorkflow;
typedef CflPocRequester::Requester RequesterAvailableDatasets;
typedef CflPocRequester::Requester RequesterWorkflowResult;
typedef CflPocRequester::Requester RequesterDoNonce;
typedef CflPocRequester::Requester RequesterDoProcess;
typedef CflPocRequester::Requester RequesterResponseProcess;

REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_ADD_DATASET, RequesterAddDataset)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_REMOVE_DATASET, RequesterRemoveDataset)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_LOOKUP_DATASETS, RequesterLookupDatasets)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_ADD_WORKER, RequesterAddWorker)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_REMOVE_WORKER, RequesterRemoveWorker)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_UPDATE_WORKER, RequesterUpdateWorker)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_LOOKUP_WORKERS, RequesterLookupWorkers)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_ADD_USER, RequesterAddUser)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_REMOVE_USER, RequesterRemoveUser)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_LOOKUP_USERS, RequesterLookupUsers)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CREATE_WORKFLOW, RequesterCreateWorkflow)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_JOIN_WORKFLOW, RequesterJoinWorkflow)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_QUIT_WORKFLOW, RequesterQuitWorkflow)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_UPDATE_WORKFLOW, RequesterUpdateWorkflow)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_LOOKUP_WORKFLOWS, RequesterLookupWorkflows)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_REMOVE_WORKFLOW, RequesterRemoveWorkflow)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_AVAILABLE_DATASETS, RequesterAvailableDatasets)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_GET_WORKFLOW_RESULT, RequesterWorkflowResult)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CREATE_DO_NONCE_RQST, RequesterDoNonce)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CREATE_DO_PROCESS_RQST, RequesterDoProcess)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_PROCESS_DO_PROCESS_RESP, RequesterResponseProcess)


namespace CflPocRequester {


// TODO: this dummy placeholder when the interface is implemented
static ExWorkorderInfo requester_ex;


extern RequesterNodeConfig requesterNodeConfig;

void Requester::ProcessWorkOrder(
    std::string workload_id,
    const ByteArray& requester_id,
    const ByteArray& worker_id,
    const ByteArray& work_order_id,
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data)
{
    RequesterProcessor p;
  
    //TODO:
    //Remove the block below, when class ExWorkorderInfo is available.
    //By now, we have a fake ExWorkorderInfo, and the verifying key is passed through parameter.
    size_t input_size = in_work_order_data.size();
    if(input_size < 2)
    {
        AddOutput(0, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }

    std::vector<tcf::WorkOrderData> _in_work_order_data;
    for(size_t i = 0; i < input_size - 2; i++)
    {
        _in_work_order_data.emplace_back(in_work_order_data[i]);
    }

    ByteArray signature = in_work_order_data[input_size - 2].decrypted_data;
    signature = TransformBase64ByteArray(signature);
    ByteArray verificationKey = in_work_order_data[input_size - 1].decrypted_data;
    verificationKey = TransformBase64ByteArray(verificationKey);


    // TODO: remove line below exWorkorderInfo is available in tcf::Workload class and remove the dummy line
    //ExWorkorderInfo* exWorkorderInfo = &requester_ex;  // TODO: remove this dummy placeholder

    std::unique_ptr<ExWorkorderInfo> exWorkorderInfo_ptr(new ExWorkorderInfo);
    ExWorkorderInfo* exWorkorderInfo = exWorkorderInfo_ptr.get();
    exWorkorderInfo->SetVerificationKey(verificationKey);
    exWorkorderInfo->SetSignature(signature);


    //TODO:
    //Remove this when output data with multiple elementes is supported.
    std::vector<tcf::WorkOrderData> _out_work_order_data;


    if (workload_id == CFL_POC_OP_ADD_DATASET)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.AddDataset(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_REMOVE_DATASET)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.RemoveDataset(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_LOOKUP_DATASETS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.LookupDatasets(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_ADD_WORKER)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.AddWorker(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_REMOVE_WORKER)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.RemoveWorker(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_UPDATE_WORKER)
    {
        //TODO:
	//By now, we only support updating extra specs of Graphene worker.
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.UpdateGrapheneWorker(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_LOOKUP_WORKERS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.LookupWorkers(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_ADD_USER)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.AddUser(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_REMOVE_USER)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.RemoveUser(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_LOOKUP_USERS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requesterNodeConfig.LookupUsers(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_CREATE_WORKFLOW)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.CreateWorkflow(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_JOIN_WORKFLOW)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.JoinWorkflow(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_QUIT_WORKFLOW)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.QuitWorkflow(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_UPDATE_WORKFLOW)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.UpdateWorkflow(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_LOOKUP_WORKFLOWS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.LookupWorkflows(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_REMOVE_WORKFLOW)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.RemoveWorkflow(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_AVAILABLE_DATASETS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.AvailableDatasets(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_GET_WORKFLOW_RESULT)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.GetWorkflowResult(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_CREATE_DO_NONCE_RQST)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.CreateNonceRequest(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_CREATE_DO_PROCESS_RQST)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.CreateProcessDatasetRequest(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    if (workload_id == CFL_POC_OP_PROCESS_DO_PROCESS_RESP)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        p.ProcessDatasetResult(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else
    {
	//TODO:
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        AddOutput(0, _out_work_order_data, CFL_POC_E_OP_CODE);
    }

    //TODO:
    //Remove this when output data with multiple elementes is supported.
    ByteArray output;
    MergeOutput(output, _out_work_order_data);
    AddOutput(0, out_work_order_data, output);
}

} //namespace CflPocRequester
