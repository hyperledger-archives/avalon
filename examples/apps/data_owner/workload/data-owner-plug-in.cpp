//
// CFL POC: Plug-in.cpp
// Workload registration and entry point
//

#include <memory>

#include "data-owner-logic.h"
#include "data-owner-plug-in.h"
#include "data-owner-node-config.h"
#include "cfl-poc-defs.h"
#include "cfl-utils.h"

using namespace cfl;


typedef CflPocDataOwner::DataOwner DataOwnerSetupRequester;
typedef CflPocDataOwner::DataOwner DataOwnerRemoveRequester;
typedef CflPocDataOwner::DataOwner DataOwnerLookupRequesters;

typedef CflPocDataOwner::DataOwner DataOwnerSetupDOWorker;
typedef CflPocDataOwner::DataOwner DataOwnerRemoveDOWorker;

typedef CflPocDataOwner::DataOwner DataOwnerAddWorkerMeasuremnet;
typedef CflPocDataOwner::DataOwner DataOwnerRemoveWorkerMeasuremnet;
typedef CflPocDataOwner::DataOwner DataOwnerLookupWorkerMeasuremnets;
typedef CflPocDataOwner::DataOwner DataOwnerSealEncryptionKey;
typedef CflPocDataOwner::DataOwner DataOwnerUnsealEncryptionKey;

typedef CflPocDataOwner::DataOwner DataOwnerNonce;
typedef CflPocDataOwner::DataOwner DataOwnerProcess;

//TODO: change CFL_POC_OP_RLIST_NONCE to CFL_POC_OP_CFG_NONCE for release version
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_SETUP_REQUESTER, DataOwnerSetupRequester)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_REMOVE_REQUESTER, DataOwnerRemoveRequester)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_LOOKUP_REQUESTERS, DataOwnerLookupRequesters)

REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_ADD_WORKER_MEAS, DataOwnerAddWorkerMeasuremnet)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_REMOVE_WORKER_MEAS, DataOwnerRemoveWorkerMeasuremnet)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS, DataOwnerLookupWorkerMeasuremnets)

REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_SETUP_DO_WORKER, DataOwnerSetupDOWorker)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_REMOVE_DO_WORKER, DataOwnerRemoveDOWorker)

REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_NONCE, DataOwnerNonce)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_PROCESS, DataOwnerProcess)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_SEAL_ENC_KEY, DataOwnerSealEncryptionKey)
REGISTER_WORKLOAD_PROCESSOR(CFL_POC_OP_CFG_UNSEAL_ENC_KEY, DataOwnerUnsealEncryptionKey)

namespace CflPocDataOwner {
	
extern RequesterList requester_list;
extern DataOwnerNodeConfig dataOwnerNodeConfig;
static ExWorkorderInfo data_owner_ex;

void DataOwner::ProcessWorkOrder(
    std::string workload_id,
    const ByteArray& requester_id,
    const ByteArray& worker_id,
    const ByteArray& work_order_id,
    const std::vector<tcf::WorkOrderData>& in_work_order_data,
    std::vector<tcf::WorkOrderData>& out_work_order_data)
{
    DataOwnerProcessor processor;

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
    //std::string block = VerificationKeyBlockFromByteArray(verificationKey);
    //AddOutput(0, out_work_order_data, block);
    //return;


    // TODO: Uncomment the line below exWorkorderInfo is available in tcf::Workload class
    // processor.SetExtendedWoroderInfoApi(exWorkorderInfo);

    // TODO: remove line below exWorkorderInfo is available in tcf::Workload class and remove the dummy line
     //ExWorkorderInfo* exWorkorderInfo = &data_owner_ex;  // TODO: remove this dummy placeholder
    std::unique_ptr<ExWorkorderInfo> exWorkorderInfo_ptr(new ExWorkorderInfo);
    ExWorkorderInfo* exWorkorderInfo = exWorkorderInfo_ptr.get();
    exWorkorderInfo->SetVerificationKey(verificationKey);
    exWorkorderInfo->SetSignature(signature);

    //TODO:
    //Remove this when output data with multiple elementes is supported.
    std::vector<tcf::WorkOrderData> _out_work_order_data;


    if (workload_id == CFL_POC_OP_SETUP_REQUESTER)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
	//Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requester_list.SetupRequesterEnclave(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_REMOVE_REQUESTER)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requester_list.RemoveRequesterEnclave(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_LOOKUP_REQUESTERS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        requester_list.LookupRequesterEnclaves(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_SETUP_DO_WORKER)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.SetupWorker(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_REMOVE_DO_WORKER)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.RemoveWorker(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_ADD_WORKER_MEAS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.AddWorkerMeasurement(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_REMOVE_WORKER_MEAS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.RemoveWorkerMeasurement(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.LookupWorkerMeasurements(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_SEAL_ENC_KEY)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.SealEncryptionKey(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_CFG_UNSEAL_ENC_KEY)
    {
        //TODO:
        //Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        dataOwnerNodeConfig.UnsealEncryptionKey(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
    }
    else if (workload_id == CFL_POC_OP_NONCE)
    {
	//TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        processor.CreateNonce(_in_work_order_data, _out_work_order_data, exWorkorderInfo, requester_list);
    }
    else if (workload_id == CFL_POC_OP_PROCESS)
    {
        //TODO:
	//Change the variable _in_work_order_data back to in_work_order_data when output data with multiple elementes is supported.
        //Change the variable _out_work_order_data back to out_work_order_data when output data with multiple elementes is supported.
        processor.Process(_in_work_order_data, _out_work_order_data, exWorkorderInfo);
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

} //namespace CflPocDataOwner
