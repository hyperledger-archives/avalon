#include "node-config.h"
#include "cfl-poc-defs.h"
#include "requester-node-logic.h"
#include "cfl-utils.h"

namespace CflPocRequester {

extern RequesterNodeConfig requesterNodeConfig;

}

namespace CflPocDataOwner {

extern DataOwnerNodeConfig dataOwnerNodeConfig;

}

namespace cfl {

NodeConfig nodeConfig;


NodeConfig::NodeConfig()
{
   size_t num_of_keys = sizeof(data_owner_verification_keys) / VERIFICATION_KEY_SIZE;
   for (size_t i = 0; i < num_of_keys; i++)
   {
       ByteArray data_owner_vkey(data_owner_verification_keys[i], data_owner_verification_keys[i] + VERIFICATION_KEY_SIZE);
       data_owner_vkeys[data_owner_vkey] = 1;
   }
}


void NodeConfig::CreateNonce(const std::vector<tcf::WorkOrderData>& in_work_order_data,
                              std::vector<tcf::WorkOrderData>& out_work_order_data,
                              ExWorkorderInfo* wo_info)
{
    if (in_work_order_data.size() < CFL_POC_CFG_NONCE_PARAM_MIN)
    {
        AddOutput(CFL_POC_CFG_NONCE_RINDEX_STATUS, out_work_order_data, CFL_POC_E_PARAM_COUNT);
    }
    else
    {
        int err_code = CFL_POC_E_OP_OK;
        ByteArray data_owner_vkey;
        ByteArray nonce;

        if (!CheckDataOwner(wo_info, data_owner_vkey) &&
            !CflPocRequester::requesterNodeConfig.CheckUserVkey(data_owner_vkey) &&
	    !CflPocDataOwner::dataOwnerNodeConfig.CheckUserVkey(data_owner_vkey))
        {
            err_code = CFL_POC_E_AUTH;
        }
        else if (!CreateNonce(data_owner_vkey, nonce))
        {
            err_code = CFL_POC_E_NONCE;
        }
        AddOutput(CFL_POC_CFG_NONCE_RINDEX_STATUS, out_work_order_data, err_code);
        if (!err_code)
        {
            std::string nonce_hex = ByteArrayToHexEncodedString(nonce);
            AddOutput(CFL_POC_CFG_NONCE_RINDEX_NONCE, out_work_order_data, nonce_hex);
        }
    }
}

bool NodeConfig::CreateNonce(const ByteArray& data_owner_vkey, ByteArray& nonce)
{
    if (! ::cfl::GenerateNonce(nonce))
    {
        return false;
    }
    nonce_map[nonce] = data_owner_vkey;
    return true;
}

void NodeConfig::AddNonce(int index, std::vector<tcf::WorkOrderData>& out_work_order_data,  const ByteArray& data_owner_vkey)
{
    ByteArray nonce;
    if (CreateNonce(data_owner_vkey, nonce))
    {
	std::string nonce_hex = ByteArrayToHexEncodedString(nonce);
        AddOutput(index, out_work_order_data, nonce_hex);
    }
}


bool NodeConfig::CheckNonce(const ByteArray& nonce, const ByteArray& data_owner_vkey)
{
    bool ret_val = false;

    auto search = nonce_map.find(nonce);
    if (search != nonce_map.end())
    {
        if (nonce_map[nonce] == data_owner_vkey)
        {
            ret_val = true;
        }
        nonce_map.erase(nonce);
    }

    return ret_val;
}

bool NodeConfig::CheckDataOwner(ExWorkorderInfo* wo_info, ByteArray& data_owner_vkey)
{
    wo_info->GetWorkorderSigningInfo(data_owner_vkey);
    return data_owner_vkeys.find(data_owner_vkey) != data_owner_vkeys.end();
}


} //namespace cfl
