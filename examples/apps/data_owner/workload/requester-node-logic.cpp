#include "requester-node-logic.h"
#include "requester-node-config.h"
#include "node-config.h"
#include "cfl-utils.h"

namespace cfl {

extern NodeConfig nodeConfig;

}

using namespace cfl;

namespace CflPocRequester {

std::map<ByteArray, RequesterProcessor::WorkflowInfo> RequesterProcessor::workflow_map;
RequesterNodeConfig requesterNodeConfig;

void RequesterProcessor::CreateWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_CREATE_WORKFLOW_PARAM_MIN)
    {
        AddOutput(CFL_POC_CREATE_WORKFLOW_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id;

        ByteArray nonce = in_work_order_data[CFL_POC_CREATE_WORKFLOW_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!AddWorkflow(data_owner_vkey, workflow_id))
        {
            err_code = CFL_POC_E_NONCE;
        }

        AddOutput(CFL_POC_CREATE_WORKFLOW_RINDEX_STATUS, out_work_order_data, err_code);
        if (!err_code)
        {
            std::string wid_str = ByteArrayToHexEncodedString(workflow_id);
            AddOutput(CFL_POC_CREATE_WORKFLOW_RINDEX_ID, out_work_order_data, wid_str);
            nodeConfig.AddNonce(CFL_POC_CREATE_WORKFLOW_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}

void RequesterProcessor::JoinWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_JOIN_WORKFLOW_PARAM_MIN)
    {
        AddOutput(CFL_POC_JOIN_WORKFLOW_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id = in_work_order_data[CFL_POC_JOIN_WORKFLOW_PINDEX_WORKFLOW_ID].decrypted_data;
	workflow_id = TransformHexByteArray(workflow_id);

        ByteArray nonce = in_work_order_data[CFL_POC_JOIN_WORKFLOW_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
	else if (workflow_map.find(workflow_id) == workflow_map.end())
	{
	    err_code = CFL_POC_E_WORKFLOW_ID;
	}
	else if (workflow_map[workflow_id].status != CFL_POC_WORKFLOW_WAITING)
	{
	    err_code = CFL_POC_E_WORKFLOW_STATUS;
	}
        else 
        {
            ByteArray graphene_vkey = in_work_order_data[CFL_POC_JOIN_WORKFLOW_PINDEX_WORKER_VKEY].decrypted_data;
	    graphene_vkey = TransformBase64ByteArray(graphene_vkey);
	    ByteArray avalon_vkey = in_work_order_data[CFL_POC_JOIN_WORKFLOW_PINDEX_PARENT_VKEY].decrypted_data;
            avalon_vkey = TransformBase64ByteArray(avalon_vkey);
	    if (!requesterNodeConfig.CheckAvalonWorkerOwner(avalon_vkey, data_owner_vkey))
	    {
		err_code = CFL_POC_E_AUTH;
	    }
	    else if (!requesterNodeConfig.CheckGrapheneWorkerParent(graphene_vkey, avalon_vkey))
	    {
		err_code = CFL_POC_E_WORKER_ID;
	    }
	    else
	    {
		workflow_map[workflow_id].joined_workers[graphene_vkey] = avalon_vkey;
	    }

        }

        AddOutput(CFL_POC_JOIN_WORKFLOW_RINDEX_STATUS, out_work_order_data, err_code);
	if (err_code == CFL_POC_E_OP_OK)
	{
	    nodeConfig.AddNonce(CFL_POC_JOIN_WORKFLOW_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
	}
    }
}


void RequesterProcessor::QuitWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_QUIT_WORKFLOW_PARAM_MIN)
    {
        AddOutput(CFL_POC_QUIT_WORKFLOW_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id = in_work_order_data[CFL_POC_QUIT_WORKFLOW_PINDEX_WORKFLOW_ID].decrypted_data;
        workflow_id = TransformHexByteArray(workflow_id);

        ByteArray nonce = in_work_order_data[CFL_POC_QUIT_WORKFLOW_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (workflow_map.find(workflow_id) == workflow_map.end())
        {
            err_code = CFL_POC_E_WORKFLOW_ID;
        }
        else if (workflow_map[workflow_id].status != CFL_POC_WORKFLOW_WAITING)
        {
            err_code = CFL_POC_E_WORKFLOW_STATUS;
        }
        else
        {
            ByteArray graphene_vkey = in_work_order_data[CFL_POC_QUIT_WORKFLOW_PINDEX_WORKER_VKEY].decrypted_data;
            graphene_vkey = TransformBase64ByteArray(graphene_vkey);
            ByteArray avalon_vkey = in_work_order_data[CFL_POC_QUIT_WORKFLOW_PINDEX_PARENT_VKEY].decrypted_data;
            avalon_vkey = TransformBase64ByteArray(avalon_vkey);
            if (!requesterNodeConfig.CheckAvalonWorkerOwner(avalon_vkey, data_owner_vkey) &&
	        workflow_map[workflow_id].data_owner_vkey != data_owner_vkey)
            {
                err_code = CFL_POC_E_AUTH;
            }
            else if (!requesterNodeConfig.CheckGrapheneWorkerParent(graphene_vkey, avalon_vkey))
            {
                err_code = CFL_POC_E_WORKER_ID;
            }
            else
            {
                workflow_map[workflow_id].joined_workers.erase(graphene_vkey);
            }
        }

        AddOutput(CFL_POC_QUIT_WORKFLOW_RINDEX_STATUS, out_work_order_data, err_code);
	if (err_code == CFL_POC_E_OP_OK)
        {
            nodeConfig.AddNonce(CFL_POC_QUIT_WORKFLOW_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}


void RequesterProcessor::LookupWorkflows(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    ByteArray vkey;
    bool is_data_owner = CheckDataOwner(wo_info, vkey);

    if (!is_data_owner && !requesterNodeConfig.CheckUserVkey(vkey))
    {
        AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
    }
    else if (in_work_order_data.size() < CFL_POC_LOOKUP_WORKFLOWS_PARAM_MIN)
    {
        AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray nonce = in_work_order_data[CFL_POC_LOOKUP_WORKFLOWS_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);

        if (!CheckNonce(nonce, vkey))
        {
	    AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);	
        }
        else 
        {
            AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
	    std::string workflow_info;
	    if (is_data_owner)
	    {
	        workflow_info = TranslateWorkflowInfo();
	    }
	    else
	    {
	        workflow_info = TranslateWorkflowInfo(vkey);
	    }
	    AddOutput(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_RESULT, out_work_order_data, workflow_info);
            nodeConfig.AddNonce(CFL_POC_LOOKUP_WORKFLOWS_RINDEX_NONCE, out_work_order_data, vkey);
        }
    }
}

void RequesterProcessor::GetWorkflowResult(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                                           ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_WORKFLOW_RESULT_PARAM_MIN)
    {
        AddOutput(CFL_POC_WORKFLOW_RESULT_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id = in_work_order_data[CFL_POC_WORKFLOW_RESULT_PINDEX_ID].decrypted_data;
        ByteArray user_vkey;
        ByteArray result;

        if (!CheckUser(wo_info, workflow_id, user_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            AggregateData(workflow_id, result);
        }

        AddOutput(CFL_POC_WORKFLOW_RESULT_RINDEX_STATUS, out_work_order_data, err_code);
        if (!err_code)
        {
            AddOutput(CFL_POC_WORKFLOW_RESULT_RINDEX_RESULT, out_work_order_data, result);
        }
    }
}


void RequesterProcessor::RemoveWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_WORKFLOW_PARAM_MIN)
    {
        AddOutput(CFL_POC_REMOVE_WORKFLOW_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;

        ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_WORKFLOW_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
	ByteArray workflow_id = in_work_order_data[CFL_POC_REMOVE_WORKFLOW_PINDEX_ID].decrypted_data;
        workflow_id = TransformHexByteArray(workflow_id);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (workflow_map.find(workflow_id) == workflow_map.end())
        {
            err_code = CFL_POC_E_WORKFLOW_ID;
        }
	else if (workflow_map[workflow_id].data_owner_vkey != data_owner_vkey)
	{
	    err_code = CFL_POC_E_AUTH;
	}
        if (!err_code)
        {
            workflow_map.erase(workflow_id);
        }
	AddOutput(CFL_POC_REMOVE_WORKFLOW_RINDEX_STATUS, out_work_order_data, err_code);
	if (err_code == CFL_POC_E_OP_OK)
        {
            nodeConfig.AddNonce(CFL_POC_REMOVE_WORKFLOW_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}


void RequesterProcessor::UpdateWorkflow(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_WORKFLOW_PARAM_MIN)
    {
        AddOutput(CFL_POC_UPDATE_WORKFLOW_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;

        ByteArray nonce = in_work_order_data[CFL_POC_UPDATE_WORKFLOW_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray workflow_id = in_work_order_data[CFL_POC_UPDATE_WORKFLOW_PINDEX_ID].decrypted_data;
        workflow_id = TransformHexByteArray(workflow_id);

	ByteArray status_bytes = in_work_order_data[CFL_POC_UPDATE_WORKFLOW_PINDEX_STATUS].decrypted_data;
	std::string status_str = ByteArrayToString(status_bytes);
	int status = std::stoi(status_str);
	
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (workflow_map.find(workflow_id) == workflow_map.end())
        {
            err_code = CFL_POC_E_WORKFLOW_ID;
        }
        else if (workflow_map[workflow_id].data_owner_vkey != data_owner_vkey)
        {
            err_code = CFL_POC_E_AUTH;
        }
        if (!err_code)
        {
            workflow_map[workflow_id].status = status;
        }
        AddOutput(CFL_POC_UPDATE_WORKFLOW_RINDEX_STATUS, out_work_order_data, err_code);
	if (err_code == CFL_POC_E_OP_OK)
        {
            nodeConfig.AddNonce(CFL_POC_UPDATE_WORKFLOW_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }

    }
}



void RequesterProcessor::AvailableDatasets(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                                           ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_AVAILABLE_DATASETS_PARAM_MIN)
    {
        AddOutput(CFL_POC_AVAILABLE_DATASETS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray user_vkey;

        if (!GetUserVkey(wo_info, user_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }

        AddOutput(CFL_POC_AVAILABLE_DATASETS_RINDEX_STATUS, out_work_order_data, err_code);

	if (!err_code)
	{
	    std::string datasets = requesterNodeConfig.AvailableDatasets(user_vkey);
	    AddOutput(CFL_POC_AVAILABLE_DATASETS_RINDEX_RESULT, out_work_order_data, datasets);
	}
    }
}



void RequesterProcessor::CreateNonceRequest(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                            std::vector<tcf::WorkOrderData>& out_work_order_data,
                                            ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_DO_NONCE_RQST_PARAM_MIN)
    {
        AddOutput(CFL_POC_DO_NONCE_RQST_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray attestation_data = in_work_order_data[CFL_POC_DO_NONCE_RQST_PINDEX_ATT_DATA].decrypted_data;
        ByteArray workflow_id = in_work_order_data[CFL_POC_DO_NONCE_RQST_PINDEX_WORKFLOW_ID].decrypted_data;
        ByteArray dataset_id = in_work_order_data[CFL_POC_DO_NONCE_RQST_PINDEX_DATASET_ID].decrypted_data;
        ByteArray user_vkey;
        ByteArray json_request;
        ByteArray dataset_ek;

        if (!CheckUser(wo_info, workflow_id, user_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckDatasetAccess(workflow_id, user_vkey, dataset_id, dataset_ek))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            err_code = CreateGetNonceWoRequest(wo_info, attestation_data, workflow_id, dataset_id, json_request);
        }

        AddOutput(CFL_POC_DO_NONCE_RQST_RINDEX_STATUS, out_work_order_data, err_code);

        if (!err_code)
        {
            AddOutput(CFL_POC_DO_NONCE_RQST_RINDEX_REQUEST, out_work_order_data, json_request);
        }
        else
        {
            workflow_map.erase(workflow_id);
        }
    }
}


void RequesterProcessor::CreateProcessDatasetRequest(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                                     std::vector<tcf::WorkOrderData>& out_work_order_data,
                                                     ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_DO_PROCESS_RQST_PARAM_MIN)
    {
        AddOutput(CFL_POC_DO_PROCESS_RQST_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id = in_work_order_data[CFL_POC_DO_PROCESS_RQST_PINDEX_WORKFLOW_ID].decrypted_data;
        ByteArray dataset_id = in_work_order_data[CFL_POC_DO_PROCESS_RQST_PINDEX_DATASET_ID].decrypted_data;
        ByteArray query_data = in_work_order_data[CFL_POC_DO_PROCESS_RQST_PINDEX_QUERY_DATA].decrypted_data;
        ByteArray json_result = in_work_order_data[CFL_POC_DO_PROCESS_RQST_PINDEX_JSON_RESULT].decrypted_data;
        ByteArray user_vkey;
        ByteArray json_request;
        ByteArray dataset_ek;

        if (!CheckUser(wo_info, workflow_id, user_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckDatasetAccess(workflow_id, user_vkey, dataset_id, dataset_ek))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            ByteArray nonce;

            if (!(err_code = ParseDoNonceResult(wo_info, workflow_id, json_result, nonce)))
            {
                err_code = CreateProcessDatasetRequest(wo_info, workflow_id, nonce, dataset_id, dataset_ek, query_data, json_request);
            }
        }

        AddOutput(CFL_POC_DO_PROCESS_RQST_RINDEX_STATUS, out_work_order_data, err_code);

        if (!err_code)
        {
            AddOutput(CFL_POC_DO_PROCESS_RQST_RINDEX_REQUEST, out_work_order_data, json_request);
        }
        else
        {
            workflow_map.erase(workflow_id);
        }
    }
}



void RequesterProcessor::ProcessDatasetResult(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                                              ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_DO_PROCESS_RESP_PARAM_MIN)
    {
        AddOutput(CFL_POC_DO_PROCESS_RESP_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray workflow_id = in_work_order_data[CFL_POC_DO_PROCESS_RESP_PINDEX_WORKFLOW_ID].decrypted_data;
        ByteArray json_result = in_work_order_data[CFL_POC_DO_PROCESS_RESP_PINDEX_JSON_RESULT].decrypted_data;
        ByteArray user_vkey;

        if (!CheckUser(wo_info, workflow_id, user_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            err_code = ParseProcessDatasetResult(wo_info, workflow_id, json_result);
        }

        AddOutput(CFL_POC_DO_PROCESS_RESP_RINDEX_STATUS, out_work_order_data, err_code);

        if (err_code)
        {
            workflow_map.erase(workflow_id);
        }
    }
}



int RequesterProcessor::ParseDoNonceResult(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, const ByteArray& json_result, ByteArray nonce)
{
    // TODO:
    // parse json workorder result returned by DO for "get-nonce"
    // use generic_client as a base for porting frok python code
    // use dataset from the json_result to locate right workorder id, nonce, and ek
    // stub for now

    std::string str = "do-nonce";
    nonce.assign(str.begin(), str.end());

    return CFL_POC_E_OP_OK;
}


int RequesterProcessor::CreateProcessDatasetRequest(ExWorkorderInfo* wo_info,
                                                    const ByteArray& work_flow_id,
                                                    const ByteArray& nonce,
                                                    const ByteArray& dataset_id,
                                                    const ByteArray& dataset_ek,
                                                    const ByteArray& query_data,
                                                    ByteArray& json_request)
{
    // TODO: make a "process" workorder request to be sent to the DO node
    // use generic_client as a base for porting frok python code
    // it also needs to set up wororder_id, workorder_nonce, and workorder_ek in the workflow_map for this dataset_id
    // stub for now

    std::string str = "{\"op\":\"process\"}";
    json_request.assign(str.begin(), str.end());

    return CFL_POC_E_OP_OK;
}



int RequesterProcessor::ParseProcessDatasetResult(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, const ByteArray& json_result)
{
    // TODO:
    // parse json workorder result returned by DO for "process"
    // use generic_client as a base for porting frok python code
    // use dataset from the json_result to locate right workorder id, nonce, and ek
    // make sure that dataset_id and workload_id match corresponding items in the workflow_map[workflow_id]
    // add dataitem from json_result to a corresponding dataset in workflow_map[workflow_id].datasets

    // stub for now by
    // adding content of the json_result to the last item in the workflow_map[workflow_id].datasets

    /*size_t size = workflow_map[workflow_id].datasets.size();
    if (size)
    {
        workflow_map[workflow_id].datasets[size - 1].processing_result = json_result;
    } */
    return CFL_POC_E_OP_OK;
}



bool RequesterProcessor::CheckUser(ExWorkorderInfo* wo_info, const ByteArray& workflow_id, ByteArray& user_vkey)
{
    bool ret_val = false;
    // TODO:
    // call ExWorkorderInfo::GetWorkorderSigningInfo()
    // it must returned true (meaning that the workorder request was signed)
    // In future there should be an additional check user_vk known in RequesterNodeConfig
    // currently stub it

   /* wo_info->GetWorkorderSigningInfo(user_vkey);

    auto search = workflow_map.find(workflow_id);
    if (search != workflow_map.end())
    {
        if (workflow_map[workflow_id].user_vkey == user_vkey)
        {
            ret_val = true;
        }
    }*/

    return ret_val;
}


bool RequesterProcessor::GetUserVkey(ExWorkorderInfo* wo_info, ByteArray& user_vkey)
{
    // TODO:
    // call ExWorkorderInfo::GetWorkorderSigningInfo()
    // it must returned true (meaning that the workorder request was signed
    // return verification_key parameter from the prevoius call in user_vkey
    // In future there should be an additional check user_vk known in RequesterNodeConfig

    // currently stub it
    wo_info->GetWorkorderSigningInfo(user_vkey);
    return requesterNodeConfig.CheckUserVkey(user_vkey);
}


void RequesterProcessor::AggregateData(const ByteArray& workflow_id, ByteArray& result)
{
    /*size_t size = 1;
    WorkflowInfo& wi = workflow_map[workflow_id];

    for (size_t i = 0; i < wi.datasets.size(); i++)
    {
        size += wi.datasets[i].processing_result.size() + 1;
    }

    result.resize(size);
    int index = 0;
    for (size_t i = 0; i < wi.datasets.size(); i++)
    {
        result.data()[index++] = '_';
        memmove(&result.data()[index], wi.datasets[i].processing_result.data(), wi.datasets[i].processing_result.size());
        index += wi.datasets[i].processing_result.size();
    }
    result.data()[index] = '_';*/
}


bool RequesterProcessor::AddWorkflow(const ByteArray& data_owner_vkey, ByteArray& workflow_id)
{
    // TODO:generate a random workflow id, foe now stun=b as below
    if (! ::cfl::GenerateNonce(workflow_id)) {
	return false;
    }

    WorkflowInfo wi;
    wi.data_owner_vkey = data_owner_vkey;
    wi.workflow_id = workflow_id;
    wi.status = CFL_POC_WORKFLOW_WAITING;

    workflow_map[workflow_id] = wi;
    return true;
}


bool RequesterProcessor::CheckWorkflowOwner(const ByteArray& data_owner_vkey, const ByteArray& workflow_id)
{
    // TODO:generate a random workflow id, foe now stun=b as below
    if (workflow_map.find(workflow_id) == workflow_map.end()) {
        return false;
    }

    if ( workflow_map[workflow_id].data_owner_vkey != data_owner_vkey)
    {
	return false;
    }

    return true;
}




int RequesterProcessor::CreateGetNonceWoRequest(ExWorkorderInfo* wo_info,
                                                const ByteArray& attestation_data, const ByteArray& workflow_id,
                                                const ByteArray& dataset_id,
                                                ByteArray& json_request)
{
    // TODO: make a "get-nonce" workorder request to be sent to the DO node
    // use generic_client as a base for porting frok python code
    // it also needs to set up wororder_id, workorder_nonce, and workorder_ek in the workflow_map for this dataset_id
    // stub for now

    std::string str = "{\"op\":\"get-nonce\"}";
    json_request.assign(str.begin(), str.end());

    return CFL_POC_E_OP_OK;
}


bool RequesterProcessor::CheckDatasetAccess(const ByteArray& workflow_id, const ByteArray& user_vkey, const ByteArray& dataset_id, ByteArray& dataset_ek)
{
    bool ret_val = false;

    /*if (requesterNodeConfig.GetDatasetByVkey(user_vkey, dataset_id, dataset_ek))
    {
        WorkflowInfo& wi = workflow_map[workflow_id];

        for (size_t i = 0; i < wi.datasets.size(); i++)
        {
            if (wi.datasets[i].dataset_id == dataset_id)
            {
                // item exists - reset it
                wi.datasets[i].workorder_id.resize(0);
                wi.datasets[i].workorder_nonce.resize(0);
                wi.datasets[i].processing_result.resize(0);
                ret_val = true;
            }
        }
        if (!ret_val)
        {
            DatasetInfo di;
            di.dataset_id = dataset_id;
            wi.datasets.push_back(di);
            ret_val = true;
        }
    }*/

    return ret_val;
}

bool RequesterProcessor::CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey)
{
    return nodeConfig.CheckDataOwner(wo_info, data_owner_vkey);
}



bool RequesterProcessor::CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey)
{
   return nodeConfig.CheckNonce(nonce, data_owner_vkey);
}


bool RequesterProcessor::VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo)
{

    return exWorkorderInfo->VerifyWorkorderSignature();
}

std::string RequesterProcessor::TranslateWorkflowInfo()
{
    bool first = true;
    std::string json = "";
    for (auto it = workflow_map.begin(); it != workflow_map.end(); it++)
    {
	if (first)
	{
	    json += TranslateWorkflowInfo(it->second);
	}
	else
	{
	    json += "," + TranslateWorkflowInfo(it->second);
	}
	first = false;
    }
    return "[" + json + "]";
}

std::string RequesterProcessor::TranslateWorkflowInfo(const ByteArray& user_vkey)
{
    bool first = true;
    std::string json = "";
    for (auto it = workflow_map.begin(); it != workflow_map.end(); it++)
    {
	if (!JoinedWorkflow(user_vkey, it->second))
	{
	    continue;
	}
        if (first)
        {
            json += TranslateWorkflowInfo(it->second);
        }
        else
        {
            json += "," + TranslateWorkflowInfo(it->second);
        }
        first = false;
    }
    return "[" + json + "]";

}

std::string RequesterProcessor::TranslateWorkflowInfo(const WorkflowInfo& workflow)
{
    std::string json = "{";
    json += "\"id\":\"" + ByteArrayToHexEncodedString(workflow.workflow_id) + "\",";
    json += "\"data_owner_vkey\":\"" + ByteArrayToBase64EncodedString(workflow.data_owner_vkey) + "\",";
    json += "\"status\":" +   std::to_string(workflow.status) + ",";
    json += "\"result\":\"" + ByteArrayToString(workflow.workflow_result) + "\",";
    if (workflow.status == CFL_POC_WORKFLOW_ABORTED || workflow.status == CFL_POC_WORKFLOW_FINISHED)
    {
	json += "\"joined_workers\":" + TranslateBriefWorkflowWorkers(workflow) + "}";
    }
    else
    {
       json += "\"joined_workers\":" + TranslateDetailedWorkflowWorkers(workflow) + "}";
    }
    return json;
}

std::string RequesterProcessor::TranslateBriefWorkflowWorkers(const WorkflowInfo& workflow)
{
    bool first = true;
    std::string json = "";
    for (auto it = workflow.joined_workers.begin(); it != workflow.joined_workers.end(); it++)
    {
        if (first)
        {
            json += "{\"worker_vkey\":\"" + ByteArrayToBase64EncodedString(it->first) +
		    "\",\"parent_vkey\":\"" + ByteArrayToBase64EncodedString(it->second) + "\"}";
        }
        else
        {
            json += ",{\"worker_vkey\":\"" + ByteArrayToBase64EncodedString(it->first) + 
		    "\",\"parent_vkey\":\"" + ByteArrayToBase64EncodedString(it->second) + "\"}";
        }
        first = false;
    }
    return "[" + json + "]";
}

std::string RequesterProcessor::TranslateDetailedWorkflowWorkers(const WorkflowInfo& workflow)
{
    bool first = true;
    std::string json = "";
    for (auto it = workflow.joined_workers.begin(); it != workflow.joined_workers.end(); it++)
    {
	const auto& p = requesterNodeConfig.worker_map[it->second];
	const auto& g = requesterNodeConfig.worker_map[it->second].children[it->first];
	if (first)
        {
            json += requesterNodeConfig.TranslateGrapheneWorker(g, p);
        }
        else
        {
            json += "," + requesterNodeConfig.TranslateGrapheneWorker(g, p);
        }
        first = false;
    }
    return "[" + json + "]";
}


bool RequesterProcessor::JoinedWorkflow(const ByteArray& user_vkey, const WorkflowInfo& workflow)
{
    return workflow.joined_workers.find(user_vkey) != workflow.joined_workers.end();
}

bool RequesterProcessor::IsWorkerActive(const ByteArray& worker_vkey)
{
    for (auto wf_it = workflow_map.begin(); wf_it != workflow_map.end(); wf_it++)
    {
	WorkflowInfo& workflow = wf_it->second;
	if (workflow.status == CFL_POC_WORKFLOW_ABORTED || workflow.status == CFL_POC_WORKFLOW_FINISHED)
	{
	    continue;
	}
	for (auto it = workflow.joined_workers.begin(); it != workflow.joined_workers.end(); it++)
	{
	    if (it->first == worker_vkey || it->second == worker_vkey)
	    {
		return true;
	    }
	}
    }

    return false;
}


} //namespace CflPocRequester
