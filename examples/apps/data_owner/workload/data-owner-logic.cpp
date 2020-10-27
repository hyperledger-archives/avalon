// CFL POC: Plug-in.cpp
// Workload registration and entry point
//
//


#include "data-owner-logic.h"
#include "node-config.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"

namespace cfl {

extern NodeConfig nodeConfig;

}

using namespace cfl;

namespace CflPocDataOwner {

RequesterList requester_list;
std::map<ByteArray, ByteArray> DataOwnerProcessor::nonce_map;


void RequesterList::SetupRequesterEnclave(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                          std::vector<tcf::WorkOrderData>& out_work_order_data,
                                          ExWorkorderInfo* exWorkorderInfo)
{
    if (in_work_order_data.size() < CFL_POC_SETUP_REQUESTER_PARAM_MIN)
    {
        AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
	ByteArray data_owner_vkey;
        ByteArray nonce = in_work_order_data[CFL_POC_SETUP_REQUESTER_PINDEX_NONCE].decrypted_data;
	nonce = TransformHexByteArray(nonce);

	if (!CheckDataOwner(exWorkorderInfo, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
	else if (!VerifyWorkorderSignature(exWorkorderInfo))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        }
        else
        {
            RequesterInfo rinfo;
            rinfo.id = in_work_order_data[CFL_POC_SETUP_REQUESTER_PINDEX_ID].decrypted_data;
	    rinfo.id = TransformHexByteArray(rinfo.id);
            rinfo.mrenclave = in_work_order_data[CFL_POC_SETUP_REQUESTER_PINDEX_MRENCLAVE].decrypted_data;
	    rinfo.mrenclave = TransformHexByteArray(rinfo.mrenclave);
            rinfo.mrsigner = in_work_order_data[CFL_POC_SETUP_REQUESTER_PINDEX_MRSIGNER].decrypted_data;
            rinfo.verification_key = in_work_order_data[CFL_POC_SETUP_REQUESTER_PINDEX_VKEY].decrypted_data;
	    rinfo.verification_key = TransformBase64ByteArray(rinfo.verification_key);

	    if (rinfo.id.size() == 0 || rinfo.mrenclave.size() == 0 || rinfo.verification_key.size() == 0)
	    {
                AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM);
		return;
	    }

            bool found = false;

            for (auto& r : requesters)
            { 
  	        if (r.id == rinfo.id)
                {
                    r = rinfo;
                    found = true;
                }
            }

            if (!found)
            {
                requesters.push_back(rinfo);
            }

            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
	    nodeConfig.AddNonce(CFL_POC_SETUP_REQUESTER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}


void RequesterList::RemoveRequesterEnclave(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                                           ExWorkorderInfo* exWorkorderInfo)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_REQUESTER_PARAM_MIN)
    {
        AddOutput(CFL_POC_REMOVE_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_REQUESTER_PINDEX_NONCE].decrypted_data;
	nonce = TransformHexByteArray(nonce);

	ByteArray data_owner_vkey;
        if (!CheckDataOwner(exWorkorderInfo, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
	else if (!VerifyWorkorderSignature(exWorkorderInfo))
        {
            AddOutput(CFL_POC_REMOVE_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        }
        else
        {
            ByteArray vkey = in_work_order_data[CFL_POC_REMOVE_REQUESTER_PINDEX_VKEY].decrypted_data;
	    vkey = TransformBase64ByteArray(vkey);

            for (size_t i = 0; i < requesters.size(); i++)
            {
                RequesterInfo r = requesters[i];
                if (r.verification_key == vkey)
                {
                    requesters.erase(requesters.begin() + i);
                    break;
                }
            }

            AddOutput(CFL_POC_REMOVE_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
	    nodeConfig.AddNonce(CFL_POC_REMOVE_REQUESTER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}

void RequesterList::LookupRequesterEnclaves(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                            std::vector<tcf::WorkOrderData>& out_work_order_data,
                                            ExWorkorderInfo* exWorkorderInfo)
{
    if (in_work_order_data.size() < CFL_POC_LOOKUP_REQUESTER_PARAM_MIN)
    {
        AddOutput(CFL_POC_LOOKUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray nonce = in_work_order_data[CFL_POC_LOOKUP_REQUESTER_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);

	ByteArray data_owner_vkey;
        if (!CheckDataOwner(exWorkorderInfo, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
	else if (!VerifyWorkorderSignature(exWorkorderInfo))
        {
            AddOutput(CFL_POC_LOOKUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            AddOutput(CFL_POC_SETUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        }
        else
        {
            std::string json = TranslateJSONResultOfRequesters();
            AddOutput(CFL_POC_LOOKUP_REQUESTER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
            AddOutput(CFL_POC_LOOKUP_REQUESTER_RINDEX_RESULT, out_work_order_data, json);
	    nodeConfig.AddNonce(CFL_POC_LOOKUP_REQUESTER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
        }
    }
}




bool RequesterList::CheckDataOwner(ExWorkorderInfo* exWorkorderInfo, ByteArray& data_owner_vkey)
{
    return nodeConfig.CheckDataOwner(exWorkorderInfo, data_owner_vkey);
}



bool RequesterList::CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey)
{
   return nodeConfig.CheckNonce(nonce, data_owner_vkey); 
}


bool RequesterList::VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo)
{
    
    return exWorkorderInfo->VerifyWorkorderSignature();
}

std::string RequesterList::TranslateJSONResultOfRequesters()
{
    std::string json = "";

    size_t req_sz = requesters.size();
    for (size_t i = 0; i < req_sz; i++)
    {
	auto& r = requesters[i];
	std::string rjson = i > 0 ? ",{" : "{";
	rjson += "\"id\":\"" + ByteArrayToHexEncodedString(r.id) + "\",";
	rjson += "\"mrenclave\":\"" + ByteArrayToHexEncodedString(r.mrenclave) + "\",";
	//TODO: just a placeholder here
	rjson += "\"mrsigner\":\"\",";
	rjson += "\"verification_key\":\"" + ByteArrayToBase64EncodedString(r.verification_key) + "\"}";
	json += rjson;
    }

    json = "[" + json + "]";
    
    return json;
}


DataOwnerProcessor::DataOwnerProcessor()
{
    // stub the datasets
    std::vector<std::string> dataset1 = { "node-A-dataset1-1", "node-A-dataset1-2", "node-A-dataset1-3" };
    std::vector<std::string> dataset2 = { "node-A-dataset2-1", "node-A-dataset2-2", "node-A-dataset2-3" };
    std::vector<std::string> dataset3 = { "node-A-dataset3-1", "node-A-dataset3-2", "node-A-dataset3-3" };

    dataset_map["dataset1"] = dataset1;
    dataset_map["dataset2"] = dataset2;
    dataset_map["dataset3"] = dataset3;
}


// TODO: Change nonce name to something else like ekey, beacuse it is actually pablic RSA key
void DataOwnerProcessor::CreateNonce(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                     std::vector<tcf::WorkOrderData>& out_work_order_data,
                                     ExWorkorderInfo* exWorkorderInfo,
                                     const RequesterList& rlist)
{
    if (in_work_order_data.size() < CFL_POC_NONCE_PARAM_MIN)
    {
        AddOutput(CFL_POC_PROCESS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray nonce_vkey;
        ByteArray skey;
        ByteArray attestation_data = in_work_order_data[CFL_POC_NONCE_PINDEX_ATT_DATA].decrypted_data;
        ByteArray workflow_id = in_work_order_data[CFL_POC_NONCE_PINDEX_WORKFLOW_ID].decrypted_data;
        ByteArray dataset_id = in_work_order_data[CFL_POC_NONCE_PINDEX_DATASET_ID].decrypted_data;

        if (!VerifyDataSet(dataset_id))
        {
            AddOutput(CFL_POC_NONCE_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
            AddOutput(CFL_POC_NONCE_RINDEX_WORKFLOW_ID, out_work_order_data, workflow_id);
            AddOutput(CFL_POC_NONCE_RINDEX_DATASET_ID, out_work_order_data, dataset_id);
        }
        else if (!VerifyRequestor(exWorkorderInfo, attestation_data, rlist))
        {
            AddOutput(CFL_POC_NONCE_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
            AddOutput(CFL_POC_NONCE_RINDEX_WORKFLOW_ID, out_work_order_data, workflow_id);
            AddOutput(CFL_POC_NONCE_RINDEX_DATASET_ID, out_work_order_data, dataset_id);
        }
        else if (!GenerateNonce(nonce_vkey, skey))
        {
            AddOutput(CFL_POC_NONCE_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
            AddOutput(CFL_POC_NONCE_RINDEX_WORKFLOW_ID, out_work_order_data, workflow_id);
            AddOutput(CFL_POC_NONCE_RINDEX_DATASET_ID, out_work_order_data, dataset_id);
        }
        else
        {
            // TODO: store a map<nonce, dataset> to make sure that nonce generated for one dataset cannot be used for another

            nonce_map[nonce_vkey] = skey;

            AddOutput(CFL_POC_NONCE_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
            AddOutput(CFL_POC_NONCE_RINDEX_WORKFLOW_ID, out_work_order_data, workflow_id);
            AddOutput(CFL_POC_NONCE_RINDEX_DATASET_ID, out_work_order_data, dataset_id);
            AddOutput(CFL_POC_NONCE_RINDEX_NONCE, out_work_order_data, nonce_vkey);
        }
    }
}


void DataOwnerProcessor::Process(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                 std::vector<tcf::WorkOrderData>& out_work_order_data,
                                 ExWorkorderInfo* exWorkorderInfo)
{
    if (in_work_order_data.size() < CFL_POC_PROCESS_PARAM_MIN)
    {
        AddOutput(CFL_POC_PROCESS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = 0;
        ByteArray flow_id = in_work_order_data[CFL_POC_PROCESS_PINDEX_FLOW_ID].decrypted_data;
        ByteArray nonce = in_work_order_data[CFL_POC_PROCESS_PINDEX_NONCE].decrypted_data;
        ByteArray vkey_sig = in_work_order_data[CFL_POC_PROCESS_PINDEX_VKEY_SIG].decrypted_data;
        ByteArray dataset_name = in_work_order_data[CFL_POC_PROCESS_PINDEX_DATASET_NAME].decrypted_data;
        ByteArray dataset_key = in_work_order_data[CFL_POC_PROCESS_PINDEX_DATASET_KEY].decrypted_data;
        ByteArray query_data = in_work_order_data[CFL_POC_PROCESS_PINDEX_QUERY_DATA].decrypted_data;
        std::string query_result;

        if (!CheckNonce(exWorkorderInfo, nonce, vkey_sig))
        {
            err_code = CFL_POC_E_NONCE;
        }
        else
        {
            if (!PrepareDataset(dataset_name, dataset_key, vkey_sig))
            {
                err_code = CFL_POC_E_DATASET_NAME;
            }
            else if (!ProcessQuery(query_data, query_result))
            {
                err_code = CFL_POC_E_DATA_ITEM_INDEX;
            }
            RemoveNonce(nonce);
        }

        AddOutput(CFL_POC_PROCESS_RINDEX_STATUS, out_work_order_data, err_code);
        AddOutput(CFL_POC_PROCESS_RINDEX_DATASET_NAME, out_work_order_data, dataset_name);

        if (!err_code)
        {
            AddOutput(CFL_POC_PROCESS_RINDEX_DATA_ITEM, out_work_order_data, query_result);
        }
    }
}



bool DataOwnerProcessor::CheckNonce(ExWorkorderInfo* exWorkorderInfo, const ByteArray& nonce, const ByteArray& vkey_sig)
{
    bool ret_val = false;

    // proper implemetation should
    // - check the nonce exists in the nonce_map
    // - get the requester signig key from the map
    // - vetify the the workorder is sighed by this key using exWorkorderInfo::GetWorkorderSigningInfo()
    //      - directly in case of singleton 
    //      - or indirectly in case of WPE (using nonce and vkey_sig)

    // it is a simple stub now - just chaeck that the nonce exist 
    auto search = nonce_map.find(nonce);

    if (search != nonce_map.end())
    {
        ret_val = true;
    }

    return ret_val;
}


bool DataOwnerProcessor::RemoveNonce(const ByteArray& nonce)
{
    bool ret_val = false;
    auto search = nonce_map.find(nonce);

    if (search != nonce_map.end())
    {
        nonce_map.erase(nonce);
        ret_val = true;
    }

    return ret_val;
}



bool DataOwnerProcessor::GenerateNonce(ByteArray& nonce_vkey, ByteArray& skey)
{
    // Final implementation with call exWororderInfo API to generate RSA Key pair
    // public key is used as nonce and key in the map below, and the value includes
    // - secret (decryption) RSA key
    // - the requester verification key (from the prior call to VerifyRequestor


    // In the phase 1 we will use a stub below

    static uint32_t counter = 0;
    bool ret_val = true;

    std::string result_str = std::to_string(++counter);
    ByteArray ba(result_str.begin(), result_str.end());
    nonce_vkey = ba;

    return ret_val;
}



bool DataOwnerProcessor::VerifyRequestor(ExWorkorderInfo* exWorkorderInfo, ByteArray& attestation_data, const RequesterList& rlist)
{
    // call ExWorkorderInfo::VerifyAttestaion();
    // calls requester_list.GetRequesters to get list of allowed requester MRENCLAVE values
    // verify that MRENCLAVE value returened by call ExWorkorderInfo::VerifyAttestaion() is on the list 

    return true; // stub it for now
}



bool DataOwnerProcessor::PrepareDataset(const ByteArray& dataset_name, const ByteArray& dataset_key, const ByteArray& nonce)
{
    bool ret_val = false;

    // in the proper implementation dataset key comes encrypted with the RSA public key used known as nonce
    // so the flow will be
    // - check if the dataset name is valid
    // - get secret RSA key by looking up nonce_map with "nonce" as the key
    // - decrypt the dataset_key
    // - load or setup an access to the dataset using dataset_name and dataset_key

    // stub it for now
    // - check that the dataset name is valid
    // - store the dataset name for later use in the ProcessQuery call

    dataset_name_str = ByteArrayToString(dataset_name);
    auto search = dataset_map.find(dataset_name_str);

    if (search != dataset_map.end())
    {
        ret_val = true;
    }

    return ret_val;
}



bool DataOwnerProcessor::ProcessQuery(const ByteArray& query_data, std::string& value)
{
    bool ret_val = false;

    // Previous calls PrepareDataset verified that dataset_name_str is valid

    std::vector<std::string> dataset = dataset_map[dataset_name_str];
    std::string index_str = ByteArrayToString(query_data);
    size_t index = atoi(index_str.data());

    if (index >= 0 && index < dataset.size())
    {
       value = dataset[index].data();
       ret_val = true; 
    }

    return ret_val;
}


bool DataOwnerProcessor::VerifyDataSet(const ByteArray& dataset_id)
{
    auto search = dataset_map.find(ByteArrayToString(dataset_id));
    return (search != dataset_map.end());
}

}//namespace CflPocDataOwner
