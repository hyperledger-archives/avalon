#include "requester-node-config.h"
#include "requester-node-logic.h"
#include "node-config.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"


namespace cfl {

extern NodeConfig nodeConfig;

}

using namespace cfl;

namespace CflPocRequester {

void RequesterNodeConfig::AddWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                    std::vector<tcf::WorkOrderData>& out_work_order_data,
                                    ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_ADD_WORKER_PINDEX_TYPE + 1)
    {
        AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
	ByteArray worker_type_byte = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_TYPE].decrypted_data;
	std::string worker_type = ByteArrayToString(worker_type_byte);
	if (worker_type == "avalon")
	{
	    AddAvalonWorker(in_work_order_data, out_work_order_data, wo_info);
	}
	else if(worker_type == "graphene")
	{
	    AddGrapheneWorker(in_work_order_data, out_work_order_data, wo_info);
	}
	else
	{
	    AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM);
	}
    }    
}

void RequesterNodeConfig::RemoveWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                       std::vector<tcf::WorkOrderData>& out_work_order_data,
                                       ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_WORKER_PINDEX_TYPE + 1)
    {
        AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray worker_type_byte = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_TYPE].decrypted_data;
        std::string worker_type = ByteArrayToString(worker_type_byte);
        if (worker_type == "avalon")
        {
            RemoveAvalonWorker(in_work_order_data, out_work_order_data, wo_info);
        }
        else if(worker_type == "graphene")
        {
            RemoveGrapheneWorker(in_work_order_data, out_work_order_data, wo_info);
        }
        else
        {
            AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM);
        }
    }
}


void RequesterNodeConfig::RemoveAvalonWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                             std::vector<tcf::WorkOrderData>& out_work_order_data,
                                             ExWorkorderInfo* wo_info)
{
     if (in_work_order_data.size() < CFL_POC_REMOVE_AVALON_WORKER_PARAM_MIN)
     {
         AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
     }
    
     RequesterProcessor p;
     ByteArray worker_vkey = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_WORKER_VKEY].decrypted_data;
     worker_vkey = TransformBase64ByteArray(worker_vkey);
     ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_NONCE].decrypted_data;
     nonce = TransformHexByteArray(nonce);

     ByteArray data_owner_vkey;

     int err_code = CFL_POC_E_OP_OK;
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
     else if (worker_map.find(worker_vkey) == worker_map.end())
     {
	 err_code = CFL_POC_E_WORKER_ID;
     }
     else if (worker_map[worker_vkey].data_owner_vkey != data_owner_vkey)
     {
	 err_code = CFL_POC_E_AUTH;
     }
     else if(p.IsWorkerActive(worker_vkey))
     {
	 err_code = CFL_POC_E_WORKER_BUSY;
     }
     else
     {
         worker_map.erase(worker_vkey);
     }
     AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, err_code);
     if (err_code == CFL_POC_E_OP_OK)
     {
	 nodeConfig.AddNonce(CFL_POC_REMOVE_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
     }

}


void RequesterNodeConfig::RemoveGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                               std::vector<tcf::WorkOrderData>& out_work_order_data,
                                               ExWorkorderInfo* wo_info)
{
     if (in_work_order_data.size() < CFL_POC_REMOVE_GRAPHENE_WORKER_PARAM_MIN)
     {
         AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
     }

     RequesterProcessor p;
     ByteArray worker_vkey = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_WORKER_VKEY].decrypted_data;
     worker_vkey = TransformBase64ByteArray(worker_vkey);
     ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_NONCE].decrypted_data;
     nonce = TransformHexByteArray(nonce);
     ByteArray parent_vkey = in_work_order_data[CFL_POC_REMOVE_WORKER_PINDEX_PARENT_VKEY].decrypted_data;
     parent_vkey = TransformBase64ByteArray(parent_vkey);

     ByteArray data_owner_vkey;

     int err_code = CFL_POC_E_OP_OK;
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
     else if (worker_map.find(parent_vkey) == worker_map.end())
     {
         err_code = CFL_POC_E_WORKER_ID;
     }
     else if (worker_map[parent_vkey].data_owner_vkey != data_owner_vkey)
     {
         err_code = CFL_POC_E_AUTH;
     }
     else if(p.IsWorkerActive(worker_vkey))
     {
         err_code = CFL_POC_E_WORKER_BUSY;
     }
     else
     {
         worker_map[parent_vkey].children.erase(worker_vkey);
     }
     AddOutput(CFL_POC_REMOVE_WORKER_RINDEX_STATUS, out_work_order_data, err_code);
     if (err_code == CFL_POC_E_OP_OK)
     {
         nodeConfig.AddNonce(CFL_POC_REMOVE_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
     }
}


void RequesterNodeConfig::UpdateGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                               std::vector<tcf::WorkOrderData>& out_work_order_data,
                                               ExWorkorderInfo* wo_info)
{
     if (in_work_order_data.size() < CFL_POC_UPDATE_WORKER_PARAM_MIN)
     {
         AddOutput(CFL_POC_UPDATE_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
     }

     RequesterProcessor p;
     ByteArray worker_vkey = in_work_order_data[CFL_POC_UPDATE_WORKER_PINDEX_WORKER_VKEY].decrypted_data;
     worker_vkey = TransformBase64ByteArray(worker_vkey);
     ByteArray nonce = in_work_order_data[CFL_POC_UPDATE_WORKER_PINDEX_NONCE].decrypted_data;
     nonce = TransformHexByteArray(nonce);
     ByteArray parent_vkey = in_work_order_data[CFL_POC_UPDATE_WORKER_PINDEX_PARENT_VKEY].decrypted_data;
     parent_vkey = TransformBase64ByteArray(parent_vkey);

     ByteArray data_owner_vkey;

     int err_code = CFL_POC_E_OP_OK;
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
     else if (worker_map.find(parent_vkey) == worker_map.end())
     {
         err_code = CFL_POC_E_WORKER_ID;
     }
     else if (worker_map[parent_vkey].data_owner_vkey != data_owner_vkey)
     {
         err_code = CFL_POC_E_AUTH;
     }
     else if(p.IsWorkerActive(worker_vkey))
     {
         err_code = CFL_POC_E_WORKER_BUSY;
     }
     else
     {
         auto& worker = worker_map[parent_vkey].children[worker_vkey];
	 ByteArray extra_specs = in_work_order_data[CFL_POC_UPDATE_WORKER_PINDEX_EXTRA_SPECS].decrypted_data;
	 worker.extra_specs = extra_specs;
     }
     AddOutput(CFL_POC_UPDATE_WORKER_RINDEX_STATUS, out_work_order_data, err_code);
      if (err_code == CFL_POC_E_OP_OK)
     {
         nodeConfig.AddNonce(CFL_POC_UPDATE_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
     }
}



void RequesterNodeConfig::LookupWorkers(const std::vector<tcf::WorkOrderData>& in_work_order_data,
		                      std::vector<tcf::WorkOrderData>& out_work_order_data,
				      ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_LOOKUP_WORKER_PARAM_MIN)
    {
        AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
        return;
    }
    ByteArray nonce = in_work_order_data[CFL_POC_LOOKUP_WORKER_PINDEX_NONCE].decrypted_data;
    nonce = TransformHexByteArray(nonce);
    ByteArray data_owner_vkey;
    
    if (!CheckDataOwner(wo_info, data_owner_vkey))
    {
        AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
    }
    else if (!CheckNonce(nonce, data_owner_vkey))
    {
        AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
    }
    else if (!VerifyWorkorderSignature(wo_info))
    {
        AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
    }
    else
    {
	std::string worker_info = TranslateWorkerInfo();
	AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
	AddOutput(CFL_POC_LOOKUP_WORKER_RINDEX_RESULT, out_work_order_data, worker_info);
        nodeConfig.AddNonce(CFL_POC_LOOKUP_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);

    }

}


void RequesterNodeConfig::AddAvalonWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                          std::vector<tcf::WorkOrderData>& out_work_order_data,
                                          ExWorkorderInfo* wo_info)
{
     if (in_work_order_data.size() < CFL_POC_ADD_AVALON_WORKER_PARAM_MIN)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
	 return;
     }
     ByteArray id = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_ID].decrypted_data;
     id = TransformHexByteArray(id);
     ByteArray worker_mrenclave = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_MRENCLAVE].decrypted_data;
     worker_mrenclave = TransformHexByteArray(worker_mrenclave);
     ByteArray worker_mrsigner = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_MRSIGNER].decrypted_data;
     ByteArray worker_vkey =  in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_WORKER_VKEY].decrypted_data;
     worker_vkey = TransformBase64ByteArray(worker_vkey);
     ByteArray nonce = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_NONCE].decrypted_data;
     nonce = TransformHexByteArray(nonce);

     ByteArray data_owner_vkey;

     int err_code = CFL_POC_E_OP_OK;
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
     else
     {
	  auto search = worker_map.find(worker_vkey);

          if (search != worker_map.end())
          {
              if (worker_map[worker_vkey].data_owner_vkey != data_owner_vkey)
              {
                  err_code = CFL_POC_E_WORKER_ID;
              }
              else
              {
                  worker_map[worker_vkey].worker_mrenclave = worker_mrenclave;
                  worker_map[worker_vkey].worker_mrsigner = worker_mrsigner;
                  worker_map[worker_vkey].worker_vkey = worker_vkey;
              }
          }
          else
          {
              AvalonWorker worker;

              worker.id = id;
              worker.data_owner_vkey = data_owner_vkey;
              worker.worker_mrenclave = worker_mrenclave;
              worker.worker_mrsigner = worker_mrsigner;
	      //TODO Avalon worker verification is not enabled by now.
	      //Set isv prod id and isv svn to fake values.
	      worker.isv_prod_id = -1;
	      worker.isv_svn = -1;
              worker.worker_vkey = worker_vkey;
              worker_map[worker_vkey] = worker;
	  }
     }
     AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, err_code);
     if (err_code == CFL_POC_E_OP_OK)
     {
         nodeConfig.AddNonce(CFL_POC_ADD_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);
     }
}


void RequesterNodeConfig::AddGrapheneWorker(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                          std::vector<tcf::WorkOrderData>& out_work_order_data,
                                          ExWorkorderInfo* wo_info)
{
     if (in_work_order_data.size() < CFL_POC_ADD_GRAPHENE_WORKER_PARAM_MIN)
     {
         AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
         return;
     }

     ByteArray nonce = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_NONCE].decrypted_data;
     nonce = TransformHexByteArray(nonce);
     ByteArray indata = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_INDATA].decrypted_data;
     ByteArray parent_vkey = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_PARENT_VKEY].decrypted_data;
     parent_vkey = TransformBase64ByteArray(parent_vkey);

     ByteArray data_owner_vkey;
     if (!CheckDataOwner(wo_info, data_owner_vkey))
     {
         AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
         return;
     }
     else if (!CheckNonce(nonce, data_owner_vkey))
     {
         AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
         return;
     }
     else if (!VerifyWorkorderSignature(wo_info))
     {
         AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
         return;
     }

     auto search = worker_map.find(parent_vkey);
     if (search == worker_map.end())
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_WORKER_ID);
         return;
     }

     AvalonWorker& parent = worker_map[parent_vkey];
     if (parent.data_owner_vkey != data_owner_vkey)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
         return;
     }
     
     ByteArray session_key = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_SESSION_KEY].decrypted_data;
     session_key = TransformHexByteArray(session_key);
     ByteArray session_iv = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_SESSION_IV].decrypted_data;
     session_iv = TransformHexByteArray(session_iv);

     indata = TransformBase64ByteArray(indata);
     indata = tcf::crypto::skenc::DecryptMessage(session_key, session_iv, indata);
     /*code */
     ByteArray hash2;
     hash2 = tcf::crypto::ComputeMessageHash(indata);
	 
     ByteArray hash1 = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_HASH1].decrypted_data;
     ByteArray concat_hash;
     concat_hash.insert(concat_hash.end(),hash1.begin(),hash1.end());
     concat_hash.insert(concat_hash.end(),hash2.begin(),hash2.end());
     ByteArray final_hash;
     final_hash = tcf::crypto::ComputeMessageHash(concat_hash);

     using tcf::crypto::sig::PublicKey;
     std::string vk_block = cfl::VerificationKeyBlockFromByteArray(parent_vkey);
     PublicKey public_key = PublicKey(vk_block);
     ByteArray parent_sig = in_work_order_data[CFL_POC_ADD_WORKER_PINDEX_PARENT_SIGNATURE].decrypted_data;
     parent_sig = TransformBase64ByteArray(parent_sig);
     if(public_key.VerifySignature(final_hash, parent_sig) != 0)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
	 return;
     }

     /*code*/
     std::string indata_string = ByteArrayToString(indata);
     std::vector<std::string> indata_array;
     Split(indata_string, indata_array);

     if (indata_array.size() != CFL_POC_SETUP_DO_WORKER_RINDEX_SIZE)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
         return;
     }
     if (indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS] != "0")
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
	 return;
     }
     if (indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_OP] != CFL_POC_OP_ADD_WORKER)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_CODE);
         return;
     }
     std::string indata_nonce_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_REQ_NONCE];
     ByteArray indata_nonce = HexEncodedStringToByteArray(indata_nonce_string);
     if (indata_nonce != nonce)
     {
	 AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_NONCE);
         return;
     }

     std::string indata_id_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_ID];
     std::string indata_mrenclave_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_MRENCLAVE];
     std::string indata_mrsigner_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_MRSIGNER];
     std::string indata_prodid_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_PROD_ID];
     std::string indata_svn_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_SVN];
     std::string indata_vkey_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_VKEY];
     std::string indata_ekey_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_EKEY];
     std::string indata_address_string = indata_array[CFL_POC_SETUP_DO_WORKER_RINDEX_ADDRESS];
     
     ByteArray indata_id = HexEncodedStringToByteArray(indata_id_string);
     ByteArray indata_mrenclave = HexEncodedStringToByteArray(indata_mrenclave_string);
     ByteArray indata_mrsigner = HexEncodedStringToByteArray(indata_mrsigner_string);
     int indata_prod_id = std::stoi(indata_prodid_string);
     int indata_svn = std::stoi(indata_svn_string);
     ByteArray indata_vkey = Base64EncodedStringToByteArray(indata_vkey_string);
     ByteArray indata_ekey = Base64EncodedStringToByteArray(indata_ekey_string);
     ByteArray indata_address(indata_address_string.begin(), indata_address_string.end());

     auto& graphenes = parent.children;
     if (graphenes.find(indata_vkey) != graphenes.end())
     {
	 GrapheneWorker& g = graphenes[indata_id];
	 g.worker_mrenclave = indata_mrenclave;
	 g.worker_mrsigner = indata_mrsigner;
	 g.isv_prod_id = indata_prod_id;
	 g.isv_svn = indata_svn;
	 g.worker_ekey = indata_ekey;
	 g.worker_addr = indata_address;
     }
     else
     {
	 GrapheneWorker g;
	 g.id = indata_id;
	 g.worker_mrenclave = indata_mrenclave;
         g.worker_mrsigner = indata_mrsigner;
	 g.isv_prod_id = indata_prod_id;
         g.isv_svn = indata_svn;
         g.worker_vkey = indata_vkey;
         g.worker_ekey = indata_ekey;
         g.worker_addr = indata_address;
	 graphenes[indata_vkey] = g;
     }

     AddOutput(CFL_POC_ADD_WORKER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
     nodeConfig.AddNonce(CFL_POC_ADD_WORKER_RINDEX_NONCE, out_work_order_data, data_owner_vkey);

}


void RequesterNodeConfig::AddDataset(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                     std::vector<tcf::WorkOrderData>& out_work_order_data,
                                     ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_ADD_DATASET_PARAM_MIN)
    {
        AddOutput(CFL_POC_ADD_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray dataset_id = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_ID].decrypted_data;
        ByteArray dataset_ek = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_EK].decrypted_data;
	dataset_ek = TransformBase64ByteArray(dataset_ek);
        ByteArray worker_mrenclave = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_MRENCLAVE].decrypted_data;
	worker_mrenclave = TransformHexByteArray(worker_mrenclave);
        ByteArray worker_mrsigner = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_MRSIGNER].decrypted_data; //TODO: place holder
        ByteArray worker_vkey = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_WORKER_VKEY].decrypted_data;
        worker_vkey = TransformBase64ByteArray(worker_vkey);
        ByteArray nonce = in_work_order_data[CFL_POC_ADD_DATASET_PINDEX_NONCE].decrypted_data;
	nonce = TransformHexByteArray(nonce);

        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
	else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
	    auto search = dataset_map.find(dataset_id);

            if (search != dataset_map.end())
            {
		if (dataset_map[dataset_id].data_owner_vkey != data_owner_vkey)
		{
		    err_code = CFL_POC_E_DATASET_ID;
		}
		else
		{
                    dataset_map[dataset_id].data_ek = dataset_ek;
                    dataset_map[dataset_id].worker_mrenclave = worker_mrenclave;
                    dataset_map[dataset_id].worker_mrsigner = worker_mrsigner;
                    dataset_map[dataset_id].worker_vkey = worker_vkey;
		}
            }
            else
            {
                DatasetConfig dataset;

                dataset.id = dataset_id;
                dataset.data_owner_vkey = data_owner_vkey;
                dataset.data_ek = dataset_ek;
                dataset.worker_mrenclave = worker_mrenclave;
                dataset.worker_mrsigner = worker_mrsigner;
                dataset.worker_vkey = worker_vkey;

                dataset_map[dataset_id] = dataset;
           }
        }
        AddOutput(CFL_POC_ADD_DATASET_RINDEX_STATUS, out_work_order_data, err_code);
    }
}


std::string RequesterNodeConfig::AvailableDatasets(const ByteArray& user_vkey)
{
    std::string json = "";
    int found = 0;

    for (auto iter = dataset_map.begin(); iter != dataset_map.end(); iter++)
    {
        const DatasetConfig& dataset = iter->second;
        const ByteArray& data_owner_vkey = dataset.data_owner_vkey;

	if (user_map.find(data_owner_vkey) == user_map.end())
	{
	    continue;
	}

        auto& users = user_map[data_owner_vkey];
        if(users.find(user_vkey) == users.end())
	{
	    continue;
	}

	if (found == 0)
	{
	    json += TranslateDataset(dataset);
	}
	else {
	    json += "," + TranslateDataset(dataset);
	}

	found++;

    }

    return "[" + json + "]";
}



void RequesterNodeConfig::RemoveDataset(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                        std::vector<tcf::WorkOrderData>& out_work_order_data,
                                        ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_DATASET_PARAM_MIN)
    {
        AddOutput(CFL_POC_REMOVE_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray dataset_id = in_work_order_data[CFL_POC_REMOVE_DATASET_PINDEX_ID].decrypted_data;
        ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_DATASET_PINDEX_NONCE].decrypted_data;
	nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
	else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            auto search = dataset_map.find(dataset_id);

            if (search != dataset_map.end())
            {
                if (dataset_map[dataset_id].data_owner_vkey == data_owner_vkey)
                {
                    dataset_map.erase(dataset_id);
                }
                else
                {
                    err_code = CFL_POC_E_AUTH;
                }
            }
        }
        AddOutput(CFL_POC_REMOVE_DATASET_RINDEX_STATUS, out_work_order_data, err_code);
    }
}


void RequesterNodeConfig::LookupDatasets(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                         std::vector<tcf::WorkOrderData>& out_work_order_data,
                                         ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_LOOKUP_DATASET_PARAM_MIN)
    {
        AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        ByteArray nonce = in_work_order_data[CFL_POC_LOOKUP_DATASET_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_AUTH);
        }
        else
        {
            std::string json = TranslateDatasets(data_owner_vkey);
            AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_STATUS, out_work_order_data, CFL_POC_E_OP_OK);
	    AddOutput(CFL_POC_LOOKUP_DATASET_RINDEX_RESULT, out_work_order_data, json);
        }
    }
}


void RequesterNodeConfig::AddUser(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                  std::vector<tcf::WorkOrderData>& out_work_order_data,
                                  ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_ADD_USER_PARAM_MIN)
    {
        AddOutput(CFL_POC_ADD_USER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray user_vkey = in_work_order_data[CFL_POC_ADD_USER_PINDEX_VKEY].decrypted_data;
	user_vkey = TransformBase64ByteArray(user_vkey);
        ByteArray nonce = in_work_order_data[CFL_POC_ADD_USER_PINDEX_NONCE].decrypted_data;
	nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
	else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            auto search = user_map.find(data_owner_vkey);

            if (search != user_map.end())
            {
                user_map[data_owner_vkey][user_vkey] = 1;
            }
            else
            {
                std::map<ByteArray, int> users;
                users[user_vkey] = 1;
                user_map[data_owner_vkey] = users;
            }
        }
        AddOutput(CFL_POC_ADD_DATASET_RINDEX_STATUS, out_work_order_data, err_code);
    }
}


void RequesterNodeConfig::RemoveUser(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                     std::vector<tcf::WorkOrderData>& out_work_order_data,
                                     ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_REMOVE_USER_PARAM_MIN)
    {
        AddOutput(CFL_POC_REMOVE_USER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray user_vkey = in_work_order_data[CFL_POC_REMOVE_USER_PINDEX_VKEY].decrypted_data;
	user_vkey = TransformBase64ByteArray(user_vkey);
        ByteArray nonce = in_work_order_data[CFL_POC_REMOVE_USER_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
             err_code = CFL_POC_E_AUTH;
        }
	else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
            auto search = user_map.find(data_owner_vkey);

            if (search != user_map.end())
            {
                user_map.erase(user_vkey);
            }
        }
        AddOutput(CFL_POC_REMOVE_USER_RINDEX_STATUS, out_work_order_data, err_code);
    }
}


void RequesterNodeConfig::LookupUsers(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                                      std::vector<tcf::WorkOrderData>& out_work_order_data,
                                      ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_LOOKUP_USER_PARAM_MIN)
    {
        AddOutput(CFL_POC_LOOKUP_USER_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray nonce = in_work_order_data[CFL_POC_LOOKUP_USER_PINDEX_NONCE].decrypted_data;
        nonce = TransformHexByteArray(nonce);
        ByteArray data_owner_vkey;

        if (!CheckDataOwner(wo_info, data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CheckNonce(nonce, data_owner_vkey))
        {
             err_code = CFL_POC_E_AUTH;
        }
        else if (!VerifyWorkorderSignature(wo_info))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else
        {
	    std::string json = TranslateUserVKeys(data_owner_vkey);
            AddOutput(CFL_POC_LOOKUP_USER_RINDEX_STATUS, out_work_order_data, err_code);
	    AddOutput(CFL_POC_LOOKUP_USER_RINDEX_RESULT, out_work_order_data, json);

        }
    }
}


bool RequesterNodeConfig::GetDatasetByVkey(const ByteArray& user_vkey, const ByteArray& dataset_id, ByteArray& dataset_ek)
{
    bool ret_val = false;

    auto search = dataset_map.find(dataset_id);

    if (search != dataset_map.end())
    {
        ByteArray dataset_owner_vkey = dataset_map[dataset_id].data_owner_vkey;

        auto search = user_map.find(dataset_owner_vkey);

        if (search != user_map.end())
        {
            auto search = user_map[dataset_owner_vkey].find(user_vkey);

            if (search != user_map[dataset_owner_vkey].end())
            {
                ret_val = true;
                dataset_ek = dataset_map[dataset_id].data_ek;
            }
        }
    }

    return ret_val;
}


bool RequesterNodeConfig::CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey)
{
    return nodeConfig.CheckDataOwner(wo_info, data_owner_vkey);
}



bool RequesterNodeConfig::CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey)
{
   return nodeConfig.CheckNonce(nonce, data_owner_vkey); 
}


bool RequesterNodeConfig::VerifyWorkorderSignature(ExWorkorderInfo* exWorkorderInfo)
{

    return exWorkorderInfo->VerifyWorkorderSignature();
}


std::string RequesterNodeConfig::TranslateDatasets(const ByteArray& data_owner_vkey)
{
    std::string json = "";
    int found = 0;
    for (auto iter = dataset_map.begin(); iter != dataset_map.end(); iter++)
    {
	const DatasetConfig& d = iter->second;
	if (d.data_owner_vkey != data_owner_vkey)
        {
            continue;
	}

        if (found == 0)
	{
	    json += TranslateDataset(d);
	}
	else {
	    json += "," + TranslateDataset(d);
	}
        found++;
    }

    return "[" + json + "]";
}


std::string RequesterNodeConfig::TranslateDataset(const DatasetConfig& d)
{
    std::string json = "{";
    
    json += "\"dataset_id\":\"" + ByteArrayToString(d.id) + "\",";
    json += "\"dataset_ek\":\"" + ByteArrayToBase64EncodedString(d.data_ek) + "\",";
    json += "\"mrenclave\":\"" + ByteArrayToHexEncodedString(d.worker_mrenclave) + "\",";
    //TODO: just a placeholder here
    json += "\"mrsigner\":\"\",";
    json += "\"worker_vkey\":\"" + ByteArrayToBase64EncodedString(d.worker_vkey) + "\"}";

    return json;
}


std::string RequesterNodeConfig::TranslateUserVKeys(const ByteArray& data_owner_vkey)
{
    std::string json = "";
    if (user_map.find(data_owner_vkey) != user_map.end())
    {
	std::map<ByteArray, int>& users = user_map[data_owner_vkey];
	int found = 0;
	for (auto iter = users.begin(); iter != users.end(); iter++)
        {
             const ByteArray& vkey_byte = iter->first;
	     std::string vkey_string = ByteArrayToBase64EncodedString(vkey_byte);
	     if (found == 0)
	     {
		 json += "\"" + vkey_string + "\"";
	     }	     
	     else
	     {
		 json += ",\"" + vkey_string + "\"";
	     }
             found++;
        }
    }
    return "[" + json + "]";
}


std::string RequesterNodeConfig::TranslateWorkerInfo()
{
    std::string json = "";
    bool first = true;
    for (auto it = worker_map.begin(); it != worker_map.end(); it++)
    {
	if (first)
	{
	    json += TranslateAvalonWorker(it->second);
	}
	else
	{
	    json += "," + TranslateAvalonWorker(it->second);
	}
	first = false;
    }
    return "[" + json + "]";
}


std::string RequesterNodeConfig::TranslateAvalonWorker(const AvalonWorker& worker)
{
    std::string json = "{";
    json += "\"id\":\"" + ByteArrayToHexEncodedString(worker.id) + "\",";
    json += "\"mrenclave\":\"" + ByteArrayToHexEncodedString(worker.worker_mrenclave) + "\",";
    json += "\"mrsigner\":\"" + ByteArrayToString(worker.worker_mrsigner) + "\",";
    json += "\"isv_prod_id\":" + std::to_string(worker.isv_prod_id) + ",";
    json += "\"isv_svn\":" + std::to_string(worker.isv_svn) + ",";
    json += "\"verification_key\":\"" + ByteArrayToBase64EncodedString(worker.worker_vkey) + "\",";
    json += "\"data_owner_vkey\":\"" + ByteArrayToBase64EncodedString(worker.data_owner_vkey) + "\",";
    json += "\"children\":" + TranslateGrapheneWorker(worker.children, worker) + "}";
    return json;
}


std::string RequesterNodeConfig::TranslateGrapheneWorker(const std::map<ByteArray, GrapheneWorker>& workers, const AvalonWorker& parent)
{
    std::string json = "";
    bool first = true;
    for (auto it = workers.begin(); it != workers.end(); it++)
    {
        if (first)
        {
            json += TranslateGrapheneWorker(it->second, parent);
        }
        else
        {
            json += "," + TranslateGrapheneWorker(it->second, parent);
        }
	first = false;
    }
    return "[" + json + "]";
}


std::string RequesterNodeConfig::TranslateGrapheneWorker(const GrapheneWorker& worker, const AvalonWorker& parent)
{
    std::string json = "{";
    json += "\"id\":\"" + ByteArrayToHexEncodedString(worker.id) + "\",";
    json += "\"mrenclave\":\"" + ByteArrayToHexEncodedString(worker.worker_mrenclave) + "\",";
    json += "\"mrsigner\":\"" + ByteArrayToHexEncodedString(worker.worker_mrsigner) + "\",";
    json += "\"isv_prod_id\":" + std::to_string(worker.isv_prod_id) + ",";
    json += "\"isv_svn\":" + std::to_string(worker.isv_svn) + ",";
    json += "\"verification_key\":\"" + ByteArrayToBase64EncodedString(worker.worker_vkey) + "\",";
    json += "\"encryption_key\":\"" + ByteArrayToBase64EncodedString(worker.worker_ekey) + "\",";
    json += "\"parent_id\":\"" + ByteArrayToHexEncodedString(parent.id) + "\",";
    json += "\"data_owner_vkey\":\"" + ByteArrayToBase64EncodedString(parent.data_owner_vkey) + "\",";
    json += "\"address\":\"" + ByteArrayToString(worker.worker_addr) + "\",";
    json += "\"extra_specs\":\"" + ByteArrayToString(worker.extra_specs) + "\"}";
    return json;
}


bool RequesterNodeConfig::CheckUserVkey(const ByteArray& user_vkey)
{
    for (auto iter = worker_map.begin(); iter != worker_map.end(); iter++)
    {
	auto& graphenes = iter->second.children;
	if (graphenes.find(user_vkey) != graphenes.end())
	{
	    return true;
	}
    }
    return false;
}

bool RequesterNodeConfig::CheckAvalonWorkerOwner(const ByteArray& avalon_vkey, const ByteArray& data_owner_vkey)
{
    if (worker_map.find(avalon_vkey) == worker_map.end())
    {
	return false;
    }
    return worker_map[avalon_vkey].data_owner_vkey == data_owner_vkey;
}

bool RequesterNodeConfig::CheckGrapheneWorkerParent(const ByteArray& graphene_vkey, const ByteArray& avalon_vkey)
{
    if (worker_map.find(avalon_vkey) == worker_map.end())
    {
        return false;
    }
    auto& graphenes = worker_map[avalon_vkey].children;
    return graphenes.find(graphene_vkey) != graphenes.end();

}

} // namespace CflPocRequester


