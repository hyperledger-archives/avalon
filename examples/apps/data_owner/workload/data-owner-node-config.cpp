#include <sgx_tseal.h>

#include "avalon_sgx_error.h"

#include "data-owner-node-config.h"
#include "node-config.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"
#include "verify-workers.h"

namespace cfl {

extern NodeConfig nodeConfig;

}

using namespace cfl;

namespace CflPocDataOwner {

DataOwnerNodeConfig dataOwnerNodeConfig;

void DataOwnerNodeConfig::SetupWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_SETUP_DO_WORKER_PARAM_MIN)
    {
        AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
	return;
    }

    ByteArray nonce = in_work_order_data[CFL_POC_SETUP_DO_WORKER_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    ByteArray data_owner_vkey;

    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!CheckNonce(nonce, data_owner_vkey))
    {
        AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }

    ByteArray signup_data =  in_work_order_data[CFL_POC_SETUP_DO_WORKER_PINDEX_SIGNUP_DATA].decrypted_data;
    signup_data = TransformBase64ByteArray(signup_data);
    std::string signup_data_json = ByteArrayToString(signup_data);

    GrapheneWorker worker;
    if (!VerifyWorker(signup_data_json.c_str(), nonce, worker))
    {
	AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_QUOTE);
        return;
    }


    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_OP, out_work_order_data, CFL_POC_OP_ADD_WORKER);

    ByteArray req_nonce = in_work_order_data[CFL_POC_SETUP_DO_WORKER_PINDEX_REQ_NONCE].decrypted_data;
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_REQ_NONCE, out_work_order_data, req_nonce);

    ByteArray id = in_work_order_data[CFL_POC_SETUP_DO_WORKER_PINDEX_ID].decrypted_data;
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_ID, out_work_order_data, id);

    std::string mrenclave = ByteArrayToHexEncodedString(worker.worker_mrenclave);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_MRENCLAVE, out_work_order_data, mrenclave);
    std::string mrsigner = ByteArrayToHexEncodedString(worker.worker_mrsigner);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_MRSIGNER, out_work_order_data, mrsigner);

    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_PROD_ID, out_work_order_data, worker.isv_prod_id);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_SVN, out_work_order_data, worker.isv_svn);

    std::string vkey_base64 = ByteArrayToBase64EncodedString(worker.worker_vkey);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_VKEY, out_work_order_data, vkey_base64);

    std::string ekey_base64 = ByteArrayToBase64EncodedString(worker.worker_ekey);
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_EKEY, out_work_order_data, ekey_base64);

    ByteArray address = in_work_order_data[CFL_POC_SETUP_DO_WORKER_PINDEX_ADDRESS].decrypted_data;
    worker.worker_addr = address;
    AddOutput(CFL_POC_SETUP_DO_WORKER_RINDEX_ADDRESS, out_work_order_data, address);

    children[worker.worker_vkey] = worker;
    
}

void DataOwnerNodeConfig::RemoveWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                       std::vector<tcf::WorkOrderData>& out_work_order_data,
                                       ExWorkorderInfo* wo_info)
{
    //TODO
    //This function should update the in-memory info of Graphene workers.
    //By now, the info of Graphene workers is managed by requeter Avalon.
    //Thus, as a data owner Avalon, we just return a constant value "0",
    //so that the client could get the signature of the server.
    if (in_work_order_data.size() < CFL_POC_REMOVE_DO_WORKER_PARAM_MIN)
    {
        AddOutput(CFL_POC_REMOVE_DO_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
	return;
    }
    ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_DO_WORKER_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);

    ByteArray data_owner_vkey;

    int err_code = CFL_POC_E_OP_OK;
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        err_code = CFL_POC_E_AUTH;
    }
    else if (!VerifyWorkorderSignature(wo_info))
    {
        err_code = CFL_POC_E_AUTH;
    }
    else if (!CheckNonce(nonce, data_owner_vkey))
    {
        err_code = CFL_POC_E_NONCE;
    }


    AddOutput(CFL_POC_REMOVE_DO_WORKER_RINDEX_STATUS, out_work_order_data, err_code);
    if (err_code == CFL_POC_E_OP_OK)
    {
	ByteArray vkey = in_work_order_data[CFL_POC_REMOVE_DO_WORKER_PINDEX_VKEY].decrypted_data;
        vkey = TransformBase64ByteArray(vkey);
	children.erase(vkey);
        nodeConfig.AddNonce(CFL_POC_REMOVE_DO_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
    }
}

bool DataOwnerNodeConfig::CheckUserVkey(const ByteArray& user_vkey)
{
    return children.find(user_vkey) != children.end();
}


void DataOwnerNodeConfig::AddWorkerMeasurement(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                               std::vector<tcf::WorkOrderData>& out_work_order_data,
                                               ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_OP_CFG_ADD_WORKER_MEAS_PARAM_MIN)
    {
        AddOutput(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
	return;
    }

    ByteArray data_owner_vkey;
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
	AddOutput(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
	AddOutput(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    
    ByteArray nonce = in_work_order_data[CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    if (!CheckNonce(nonce, data_owner_vkey))
    {
	AddOutput(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }

    ByteArray mrenclave = in_work_order_data[CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_MRENCLAVE].decrypted_data;
    mrenclave = TransformHexByteArray(mrenclave);
    ByteArray mrsigner = in_work_order_data[CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_MRSIGNER].decrypted_data;
    mrsigner = TransformHexByteArray(mrsigner);
    ByteArray isv_prod_id_byte = in_work_order_data[CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_ISV_PROD_ID].decrypted_data;
    int isv_prod_id = TransformByteArrayToInteger(isv_prod_id_byte);
    ByteArray isv_svn_byte = in_work_order_data[CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_ISV_SVN].decrypted_data;
    int isv_svn = TransformByteArrayToInteger(isv_svn_byte);
    ByteArray id;
    ::cfl::GenerateNonce(id);

    WorkerMeasurement worker_meas;
    worker_meas.id = id;
    worker_meas.mrenclave = mrenclave;
    worker_meas.mrsigner = mrsigner;
    worker_meas.isv_prod_id = isv_prod_id;
    worker_meas.isv_svn = isv_svn;
    worker_measurements.emplace_back(worker_meas);

    AddOutput(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    nodeConfig.AddNonce(CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
}


void DataOwnerNodeConfig::RemoveWorkerMeasurement(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                                  std::vector<tcf::WorkOrderData>& out_work_order_data,
                                                  ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PARAM_MIN)
    {
        AddOutput(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
        return;
    }

    ByteArray data_owner_vkey;
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }

    ByteArray nonce = in_work_order_data[CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    if (!CheckNonce(nonce, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }


    ByteArray id = in_work_order_data[CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PINDEX_ID].decrypted_data;
    id = TransformHexByteArray(id);
    for (auto it = worker_measurements.begin(); it != worker_measurements.end(); it++)
    {
	if (it->id == id)
	{
	    worker_measurements.erase(it);
	    break;
	}
    }

    AddOutput(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    nodeConfig.AddNonce(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
}


void DataOwnerNodeConfig::LookupWorkerMeasurements(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                                   std::vector<tcf::WorkOrderData>& out_work_order_data,
                                                   ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_PARAM_MIN)
    {
        AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
        return;
    }

    ByteArray data_owner_vkey;
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }

    ByteArray nonce = in_work_order_data[CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    if (!CheckNonce(nonce, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }

    std::string result = TranslateWorkerMeasurements();
    AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    AddOutput(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_RESULT, out_work_order_data, result);
    nodeConfig.AddNonce(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
}


void DataOwnerNodeConfig::SealEncryptionKey(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                            std::vector<tcf::WorkOrderData>& out_work_order_data,
                                            ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_OP_CFG_SEAL_ENC_KEY_PARAM_MIN)
    {
        AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
        return;
    }

    ByteArray data_owner_vkey;
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }

    ByteArray nonce = in_work_order_data[CFL_POC_OP_CFG_SEAL_ENC_KEY_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    if (!CheckNonce(nonce, data_owner_vkey))
    {
        AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }

    ByteArray key = in_work_order_data[CFL_POC_OP_CFG_SEAL_ENC_KEY_PINDEX_KEY].decrypted_data;
    key = TransformBase64ByteArray(key);
    const uint8_t * key_ptr = key.data();
    size_t key_size = key.size();

    const uint32_t sealed_key_size = sgx_calc_sealed_data_size(0, key_size);
    ByteArray sealed_key_buffer(sealed_key_size);
    sgx_attributes_t attribute_mask = {0xfffffffffffffff3, 0};
    sgx_status_t ret = sgx_seal_data_ex(
	                   SGX_KEYPOLICY_MRENCLAVE, 
	                   attribute_mask,
                           0,        // misc_mask
                           0,        // additional mac text length
                           nullptr,  // additional mac text
                           key_size,
                           key_ptr,
                           sealed_key_size,
                           reinterpret_cast<sgx_sealed_data_t*>(sealed_key_buffer.data()));

    tcf::error::ThrowSgxError(ret, "Failed to seal encryption key");


    AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    AddOutput(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_SEALED_KEY, out_work_order_data, 
	      ByteArrayToBase64EncodedString(sealed_key_buffer));
    nodeConfig.AddNonce(CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
}


void DataOwnerNodeConfig::UnsealEncryptionKey(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                           std::vector<tcf::WorkOrderData>& out_work_order_data,
                                           ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PARAM_MIN)
    {
        AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
        return;
    }

    ByteArray vkey;
    bool is_data_owner = CheckDataOwner(wo_info, vkey);

    if (!is_data_owner && !CheckUserVkey(vkey))
    {
        AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }
    if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        return;
    }

    ByteArray nonce = in_work_order_data[CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    if (!CheckNonce(nonce, vkey))
    {	
        AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
        return;
    }

    ByteArray sealed_key = in_work_order_data[CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PINDEX_KEY].decrypted_data;
    sealed_key = TransformBase64ByteArray(sealed_key);

   
    uint32_t key_size = sgx_get_encrypt_txt_len(reinterpret_cast<const sgx_sealed_data_t*>(sealed_key.data()));
    ByteArray key_buffer(key_size);

    sgx_status_t ret = sgx_unseal_data(reinterpret_cast<const sgx_sealed_data_t*>(sealed_key.data()),
                                       nullptr, 0, key_buffer.data(), &key_size);
    tcf::error::ThrowSgxError(ret, "Failed to unseal encryption key");


    AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
    AddOutput(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_KEY, out_work_order_data,
              ByteArrayToBase64EncodedString(key_buffer));
    nodeConfig.AddNonce(CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_NONCE, out_work_order_data, vkey);
}




bool DataOwnerNodeConfig::CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey)
{
	return nodeConfig.CheckDataOwner(wo_info, data_owner_vkey);
}

bool DataOwnerNodeConfig::CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey)
{
	return nodeConfig.CheckNonce(nonce, data_owner_vkey);
}

bool DataOwnerNodeConfig::VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo)
{
	return exWorkorderInfo->VerifyWorkorderSignature();
}

std::string DataOwnerNodeConfig::TranslateWorkerMeasurements()
{
    std::string json = "";

    bool first = true;
    for (auto& worker_meas: worker_measurements)
    {
	if(first) json += TranslateWorkerMeasurement(worker_meas);
	else json += "," + TranslateWorkerMeasurement(worker_meas);
    }
    return "[" + json + "]";
}


std::string DataOwnerNodeConfig::TranslateWorkerMeasurement(const WorkerMeasurement & worker_meas)
{
    std::string json = "";

    json += "{\"id\":\"" + ByteArrayToHexEncodedString(worker_meas.id) + "\",";
    json += "\"mrenclave\":\"" + ByteArrayToHexEncodedString(worker_meas.mrenclave) + "\",";
    json += "\"mrsigner\":\"" + ByteArrayToHexEncodedString(worker_meas.mrsigner) + "\",";
    json += "\"isv_prod_id\":" + std::to_string(worker_meas.isv_prod_id) + ",";
    json += "\"isv_svn\":" + std::to_string(worker_meas.isv_svn) + "}";

    return json;

}

} //namespace CflPocDataOwner
