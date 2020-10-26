//
// CFL POC: requester-node-plug-in.cpp
// Workload registration and entry point
//

#include "node-config-plug-in.h"
#include "node-config.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"

using namespace cfl;

REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_NONCE, NodeConfigPlugin)


namespace cfl {

extern NodeConfig nodeConfig;

// TODO: this dummy placeholder when the interface is implemented
//static ExWorkorderInfo requester_ex;

void NodeConfigPlugin::ProcessWorkOrder(
    std::string workload_id,
    const ByteArray& requester_id,
    const ByteArray& worker_id,
    const ByteArray& work_order_id,
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data)
{
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


    if (workload_id == CFL_POC_OP_CFG_NONCE)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        nodeConfig.CreateNonce(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
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

} //namespace cfl
