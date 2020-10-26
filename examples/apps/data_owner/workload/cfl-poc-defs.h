//
// CFL_POC: cfl-poc-defs.h
// Common definitions for data owner and requster enclaves 
//

#pragma once

#include "work_order_data.h"
#include "crypto.h"
#include "cfl-utils.h"

// TODO: Remove dummy placeholder for class ExWorkorderInfo when it is implemented
class ExWorkorderInfo {
public:
    void SetVerificationKey(const ByteArray & key)
    {
	VerificationKey.assign(key.begin(), key.end());
    } 

    void GetWorkorderSigningInfo(ByteArray& v_key)
    {
	v_key.assign(VerificationKey.begin(), VerificationKey.end());
    }

    void SetSignature(const ByteArray& sign)
    {
        Signature.assign(sign.begin(), sign.end());
    }

    void SetIndataHash(const std::vector<tcf::WorkOrderData> in_work_order_data)
    {
	ByteArray concat_message;
	for (auto& data: in_work_order_data)
	{
	    ByteArray param = data.decrypted_data; 
	    concat_message.insert(concat_message.end(), param.begin(), param.end());
	}

	Hash = tcf::crypto::ComputeMessageHash(concat_message);
    }

    bool VerifyWorkorderSignature()
    {
	using tcf::crypto::sig::PublicKey;
	std::string vk_block = cfl::VerificationKeyBlockFromByteArray(VerificationKey);
	PublicKey public_key = PublicKey(vk_block);
	return public_key.VerifySignature(Hash, Signature) == 0;
        
    }

private:
    ByteArray VerificationKey;
    ByteArray Signature;
    ByteArray Hash;
};


#define CFL_POC_OP_CFG_NONCE                "create-cfg-nonce"      // used for both requester and DO nodes

// Operations for RequesterList
#define CFL_POC_OP_SETUP_REQUESTER          "setup-requester"
#define CFL_POC_OP_REMOVE_REQUESTER         "remove-requester"
#define CFL_POC_OP_LOOKUP_REQUESTERS        "lookup-requesters"

//Operations for DataOwnerNondeConfig
#define CFL_POC_OP_CFG_SETUP_DO_WORKER      "setup-do-worker"
#define CFL_POC_OP_CFG_REMOVE_DO_WORKER     "remove-do-worker"

#define CFL_POC_OP_CFG_ADD_WORKER_MEAS      "add-worker-measurement"
#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS   "remove-worker-measurement"
#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS   "lookup-worker-measurements"

#define CFL_POC_OP_CFG_SEAL_ENC_KEY         "seal-encryption-key"
#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY       "unseal-encryption-key"

//Operations for DataOwnerLogic
#define CFL_POC_OP_NONCE                    "get-nonce"
#define CFL_POC_OP_PROCESS                  "process"

//Operations for RequesterNodeConfig
#define CFL_POC_OP_ADD_DATASET              "add-dataset"
#define CFL_POC_OP_REMOVE_DATASET           "remove-dataset"
#define CFL_POC_OP_LOOKUP_DATASETS          "lookup-datasets"
#define CFL_POC_OP_ADD_WORKER               "add-worker"
#define CFL_POC_OP_REMOVE_WORKER            "remove-worker"
#define CFL_POC_OP_UPDATE_WORKER            "update-worker"
#define CFL_POC_OP_LOOKUP_WORKERS           "lookup-workers"
#define CFL_POC_OP_ADD_USER                 "add-user"
#define CFL_POC_OP_REMOVE_USER              "remove-user"
#define CFL_POC_OP_LOOKUP_USERS             "lookup-users"
#define CFL_POC_OP_CLEAR_ALL_DATASETS       "remove-all-datasets"

//Operations for RequesterKifuc
#define CFL_POC_OP_CREATE_WORKFLOW          "create-workflow"
#define CFL_POC_OP_REMOVE_WORKFLOW          "remove-workflow"
#define CFL_POC_OP_JOIN_WORKFLOW            "join-workflow"
#define CFL_POC_OP_QUIT_WORKFLOW            "quit-workflow"
#define CFL_POC_OP_UPDATE_WORKFLOW          "update-workflow"
#define CFL_POC_OP_LOOKUP_WORKFLOWS         "lookup-workflows"
#define CFL_POC_OP_AVAILABLE_DATASETS       "available-datasets"
#define CFL_POC_OP_GET_WORKFLOW_RESULT      "get-workflow-result"
#define CFL_POC_OP_CREATE_DO_NONCE_RQST     "create-do-nonce-request"
#define CFL_POC_OP_CREATE_DO_PROCESS_RQST   "create-do-process-request"
#define CFL_POC_OP_PROCESS_DO_PROCESS_RESP  "proces-do-nonce-response"


#define CFL_POC_E_OP_OK             (0)
#define CFL_POC_E_OP_CODE           (-1)
#define CFL_POC_E_PARAM_COUNT       (-2)
#define CFL_POC_E_DATASET_NAME      (-3)
#define CFL_POC_E_DATA_ITEM_INDEX   (-4)
#define CFL_POC_E_DATASET_SETUP     (-5)
#define CFL_POC_E_AUTH              (-6)
#define CFL_POC_E_NONCE             (-7)
#define CFL_POC_E_PARAM             (-8)
#define CFL_POC_E_DATASET_ID        (-9)
#define CFL_POC_E_WORKER_ID         (-10)
#define CFL_POC_E_WORKFLOW_ID       (-11)
#define CFL_POC_E_WORKFLOW_STATUS   (-12)
#define CFL_POC_E_WORKER_BUSY       (-13)
#define CFL_POC_E_OUT_OF_BOUND      (-14)
#define CFL_POC_E_QUOTE             (-15)


#define CFL_POC_WORKFLOW_WAITING    (0)
#define CFL_POC_WORKFLOW_ONGOING    (1)
#define CFL_POC_WORKFLOW_ABORTED    (2)
#define CFL_POC_WORKFLOW_FINISHED   (3)


// command nonce command
#define CFL_POC_CFG_NONCE_PARAM_MIN                (0)
#define CFL_POC_CFG_NONCE_PARAM_MAX                (0)

#define CFL_POC_CFG_NONCE_RINDEX_STATUS            (0)
#define CFL_POC_CFG_NONCE_RINDEX_NONCE             (1)


#define CFL_POC_SETUP_DO_WORKER_PARAM_MIN                   (5)
#define CFL_POC_SETUP_DO_WORKER_PARAM_MAX                   (5)

#define CFL_POC_SETUP_DO_WORKER_PINDEX_NONCE                (0)
#define CFL_POC_SETUP_DO_WORKER_PINDEX_REQ_NONCE            (1)
#define CFL_POC_SETUP_DO_WORKER_PINDEX_ID                   (2)
#define CFL_POC_SETUP_DO_WORKER_PINDEX_SIGNUP_DATA          (3)
#define CFL_POC_SETUP_DO_WORKER_PINDEX_ADDRESS              (4)


#define CFL_POC_SETUP_DO_WORKER_RINDEX_STATUS               (0)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_OP                   (1)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_REQ_NONCE            (2)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_ID                   (3)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_MRENCLAVE            (4)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_MRSIGNER             (5)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_PROD_ID          (6)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_ISV_SVN              (7)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_VKEY                 (8)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_EKEY                 (9)
#define CFL_POC_SETUP_DO_WORKER_RINDEX_ADDRESS              (10)

#define CFL_POC_SETUP_DO_WORKER_RINDEX_SIZE                 (11)


#define CFL_POC_REMOVE_DO_WORKER_PARAM_MIN                  (2)
#define CFL_POC_REMOVE_DO_WORKER_PARAM_MAX                  (2)

#define CFL_POC_REMOVE_DO_WORKER_PINDEX_NONCE               (0)
#define CFL_POC_REMOVE_DO_WORKER_PINDEX_VKEY                (1)

#define CFL_POC_REMOVE_DO_WORKER_RINDEX_STATUS              (0)
#define CFL_POC_REMOVE_DO_WORKER_RINDEX_NONCE               (1)



#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PARAM_MIN            (5)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PARAM_MAX            (5)

#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_NONCE         (0)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_MRENCLAVE     (1)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_MRSIGNER      (2)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_ISV_PROD_ID   (3)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_PINDEX_ISV_SVN       (4)

#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_STATUS        (0)
#define CFL_POC_OP_CFG_ADD_WORKER_MEAS_RINDEX_NONCE         (1)


#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PARAM_MIN         (2)
#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PARAM_MAX         (2)

#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PINDEX_NONCE      (0)
#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_PINDEX_ID         (1)

#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_STATUS     (0)
#define CFL_POC_OP_CFG_REMOVE_WORKER_MEAS_RINDEX_NONCE      (1)


#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_PARAM_MIN         (1)
#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_PARAM_MAX         (1)

#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_PINDEX_NONCE      (0)

#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_STATUS     (0)
#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_RESULT     (1)
#define CFL_POC_OP_CFG_LOOKUP_WORKER_MEAS_RINDEX_NONCE      (2)

#define CFL_POC_OP_CFG_SEAL_ENC_KEY_PARAM_MIN               (2)
#define CFL_POC_OP_CFG_SEAL_ENC_KEY_PARAM_MAX               (2)

#define CFL_POC_OP_CFG_SEAL_ENC_KEY_PINDEX_NONCE            (0)
#define CFL_POC_OP_CFG_SEAL_ENC_KEY_PINDEX_KEY              (1)

#define CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_STATUS           (0)
#define CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_SEALED_KEY       (1)
#define CFL_POC_OP_CFG_SEAL_ENC_KEY_RINDEX_NONCE            (2)


#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PARAM_MIN             (2)
#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PARAM_MAX             (2)

#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PINDEX_NONCE          (0)
#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_PINDEX_KEY            (1)

#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_STATUS         (0)
#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_KEY            (1)
#define CFL_POC_OP_CFG_UNSEAL_ENC_KEY_RINDEX_NONCE          (2)




// parameters counts and indexes for DO "setup" operation
#define CFL_POC_SETUP_PARAM_MIN                     (1)
#define CFL_POC_SETUP_PARAM_MAX                     (1)

#define CFL_POC_SETUP_PINDEX_SETUP_DATA             (0)

#define CFL_POC_SETUP_RINDEX_STATUS                 (0)

// parameters counts and indexes for DO "nonce" operation
#define CFL_POC_NONCE_PARAM_MIN                     (3)
#define CFL_POC_NONCE_PARAM_MAX                     (3)

#define CFL_POC_NONCE_PINDEX_WORKFLOW_ID            (0)
#define CFL_POC_NONCE_PINDEX_DATASET_ID             (1)
#define CFL_POC_NONCE_PINDEX_ATT_DATA               (2)

#define CFL_POC_NONCE_RINDEX_STATUS                 (0)
#define CFL_POC_NONCE_RINDEX_WORKFLOW_ID            (1)
#define CFL_POC_NONCE_RINDEX_DATASET_ID             (2)
#define CFL_POC_NONCE_RINDEX_NONCE                  (3)


// parameters counts and indexes for DO "process" operation
#define CFL_POC_PROCESS_PARAM_MIN                   (6)
#define CFL_POC_PROCESS_PARAM_MAX                   (6)

#define CFL_POC_PROCESS_PINDEX_FLOW_ID              (0)
#define CFL_POC_PROCESS_PINDEX_NONCE                (1)
#define CFL_POC_PROCESS_PINDEX_VKEY_SIG             (2)
#define CFL_POC_PROCESS_PINDEX_DATASET_NAME         (3)
#define CFL_POC_PROCESS_PINDEX_DATASET_KEY          (4)
#define CFL_POC_PROCESS_PINDEX_QUERY_DATA           (5)

#define CFL_POC_PROCESS_RINDEX_STATUS               (0)
#define CFL_POC_PROCESS_RINDEX_DATASET_NAME         (1)
#define CFL_POC_PROCESS_RINDEX_DATA_ITEM            (2)

// parameters counts and indexes for DO "setup requester" operation
#define CFL_POC_SETUP_REQUESTER_PARAM_MIN           (5)
#define CFL_POC_SETUP_REQUESTER_PARAM_MAX           (5)

#define CFL_POC_SETUP_REQUESTER_PINDEX_NONCE        (0)
#define CFL_POC_SETUP_REQUESTER_PINDEX_ID           (1)
#define CFL_POC_SETUP_REQUESTER_PINDEX_MRENCLAVE    (2)
#define CFL_POC_SETUP_REQUESTER_PINDEX_MRSIGNER     (3)
#define CFL_POC_SETUP_REQUESTER_PINDEX_VKEY         (4)

#define CFL_POC_SETUP_REQUESTER_RINDEX_STATUS       (0)
#define CFL_POC_SETUP_REQUESTER_RINDEX_NONCE        (1)


// parameters counts and indexes for DO "remove requester" operation
#define CFL_POC_REMOVE_REQUESTER_PARAM_MIN          (2)
#define CFL_POC_REMOVE_REQUESTER_PARAM_MAX          (2)

#define CFL_POC_REMOVE_REQUESTER_PINDEX_NONCE       (0)
#define CFL_POC_REMOVE_REQUESTER_PINDEX_VKEY        (1)

#define CFL_POC_REMOVE_REQUESTER_RINDEX_STATUS      (0)
#define CFL_POC_REMOVE_REQUESTER_RINDEX_NONCE       (1)

// parameters counts and indexes for DO "lookup requesters" operation
#define CFL_POC_LOOKUP_REQUESTER_PARAM_MIN          (1)
#define CFL_POC_LOOKUP_REQUESTER_PARAM_MAX          (1)

#define CFL_POC_LOOKUP_REQUESTER_PINDEX_NONCE       (0)

#define CFL_POC_LOOKUP_REQUESTER_RINDEX_STATUS      (0)
#define CFL_POC_LOOKUP_REQUESTER_RINDEX_RESULT      (1)
#define CFL_POC_LOOKUP_REQUESTER_RINDEX_NONCE       (2)


// Requester node ops
#define CFL_POC_ADD_DATASET_PARAM_MIN               (6)
#define CFL_POC_ADD_DATASET_PARAM_MAX               (6)

#define CFL_POC_ADD_DATASET_PINDEX_ID               (0)
#define CFL_POC_ADD_DATASET_PINDEX_EK               (1)
#define CFL_POC_ADD_DATASET_PINDEX_MRENCLAVE        (2)
#define CFL_POC_ADD_DATASET_PINDEX_MRSIGNER         (3)
#define CFL_POC_ADD_DATASET_PINDEX_WORKER_VKEY      (4)
#define CFL_POC_ADD_DATASET_PINDEX_NONCE            (5)

#define CFL_POC_ADD_DATASET_RINDEX_STATUS           (0)


#define CFL_POC_REMOVE_DATASET_PARAM_MIN            (2)
#define CFL_POC_REMOVE_DATASET_PARAM_MAX            (2)

#define CFL_POC_REMOVE_DATASET_PINDEX_ID            (0)
#define CFL_POC_REMOVE_DATASET_PINDEX_NONCE         (1)

#define CFL_POC_REMOVE_DATASET_RINDEX_STATUS        (0)



#define CFL_POC_LOOKUP_DATASET_PARAM_MIN            (1)
#define CFL_POC_LOOKUP_DATASET_PARAM_MAX            (1)

#define CFL_POC_LOOKUP_DATASET_PINDEX_NONCE         (0)

#define CFL_POC_LOOKUP_DATASET_RINDEX_STATUS        (0)
#define CFL_POC_LOOKUP_DATASET_RINDEX_RESULT        (1)



#define CFL_POC_ADD_AVALON_WORKER_PARAM_MIN         (6)
#define CFL_POC_ADD_AVALON_WORKER_PARAM_MAX         (6)
#define CFL_POC_ADD_GRAPHENE_WORKER_PARAM_MIN       (8)
#define CFL_POC_ADD_GRAPHENE_WORKER_PARAM_MAX       (8)

#define CFL_POC_ADD_WORKER_PINDEX_NONCE             (0)
#define CFL_POC_ADD_WORKER_PINDEX_TYPE              (1)

//For Avalon worker
#define CFL_POC_ADD_WORKER_PINDEX_ID                (2)
#define CFL_POC_ADD_WORKER_PINDEX_MRENCLAVE         (3)
#define CFL_POC_ADD_WORKER_PINDEX_MRSIGNER          (4)
#define CFL_POC_ADD_WORKER_PINDEX_WORKER_VKEY       (5)

//For Graphene worker
#define CFL_POC_ADD_WORKER_PINDEX_INDATA            (2)
#define CFL_POC_ADD_WORKER_PINDEX_PARENT_VKEY       (3)
#define CFL_POC_ADD_WORKER_PINDEX_HASH1             (4)
#define CFL_POC_ADD_WORKER_PINDEX_SESSION_KEY       (5)
#define CFL_POC_ADD_WORKER_PINDEX_SESSION_IV        (6)
#define CFL_POC_ADD_WORKER_PINDEX_PARENT_SIGNATURE  (7)

#define CFL_POC_ADD_WORKER_RINDEX_STATUS            (0)
#define CFL_POC_ADD_WORKER_RINDEX_NONCE             (1)


#define CFL_POC_REMOVE_AVALON_WORKER_PARAM_MIN      (3)
#define CFL_POC_REMOVE_AVALON_WORKER_PARAM_MAX      (3)
#define CFL_POC_REMOVE_GRAPHENE_WORKER_PARAM_MIN    (4)
#define CFL_POC_REMOVE_GRAPHENE_WORKER_PARAM_MAX    (4)

#define CFL_POC_REMOVE_WORKER_PINDEX_NONCE          (0)
#define CFL_POC_REMOVE_WORKER_PINDEX_TYPE           (1)
#define CFL_POC_REMOVE_WORKER_PINDEX_WORKER_VKEY    (2)
// For Graphene worker only
#define CFL_POC_REMOVE_WORKER_PINDEX_PARENT_VKEY    (3)

#define CFL_POC_REMOVE_WORKER_RINDEX_STATUS         (0)
#define CFL_POC_REMOVE_WORKER_RINDEX_NONCE          (1)


#define CFL_POC_UPDATE_WORKER_PARAM_MIN             (5)
#define CFL_POC_UPDATE_WORKER_PARAM_MAX             (5)

#define CFL_POC_UPDATE_WORKER_PINDEX_NONCE          (0)
#define CFL_POC_UPDATE_WORKER_PINDEX_TYPE           (1)
#define CFL_POC_UPDATE_WORKER_PINDEX_WORKER_VKEY    (2)
#define CFL_POC_UPDATE_WORKER_PINDEX_EXTRA_SPECS    (3)
// For graphene worker only
#define CFL_POC_UPDATE_WORKER_PINDEX_PARENT_VKEY    (4)

#define CFL_POC_UPDATE_WORKER_RINDEX_STATUS         (0)
#define CFL_POC_UPDATE_WORKER_RINDEX_NONCE          (1)



//List workers
#define CFL_POC_LOOKUP_WORKER_PARAM_MIN             (1)
#define CFL_POC_LOOKUP_WORKER_PARAM_MAX             (1)

#define CFL_POC_LOOKUP_WORKER_PINDEX_NONCE          (0)

#define CFL_POC_LOOKUP_WORKER_RINDEX_STATUS         (0)
#define CFL_POC_LOOKUP_WORKER_RINDEX_RESULT         (1)
#define CFL_POC_LOOKUP_WORKER_RINDEX_NONCE          (2)


#define CFL_POC_ADD_USER_PARAM_MIN                  (2)
#define CFL_POC_ADD_USER_PARAM_MAX                  (2)

#define CFL_POC_ADD_USER_PINDEX_VKEY                (0)
#define CFL_POC_ADD_USER_PINDEX_NONCE               (1)

#define CFL_POC_ADD_USER_RINDEX_STATUS              (0)


#define CFL_POC_REMOVE_USER_PARAM_MIN               (2)
#define CFL_POC_REMOVE_USER_PARAM_MAX               (2)

#define CFL_POC_REMOVE_USER_PINDEX_VKEY             (0)
#define CFL_POC_REMOVE_USER_PINDEX_NONCE            (1)

#define CFL_POC_REMOVE_USER_RINDEX_STATUS           (0)


#define CFL_POC_LOOKUP_USER_PARAM_MIN               (1)
#define CFL_POC_LOOKUP_USER_PARAM_MAX               (1)

#define CFL_POC_LOOKUP_USER_PINDEX_NONCE            (0)

#define CFL_POC_LOOKUP_USER_RINDEX_STATUS           (0)
#define CFL_POC_LOOKUP_USER_RINDEX_RESULT           (1)


#define CFL_POC_CREATE_WORKFLOW_PARAM_MIN           (1)
#define CFL_POC_CREATE_WORKFLOW_PARAM_MAX           (1)

#define CFL_POC_CREATE_WORKFLOW_PINDEX_NONCE        (0)

#define CFL_POC_CREATE_WORKFLOW_RINDEX_STATUS       (0)
#define CFL_POC_CREATE_WORKFLOW_RINDEX_ID           (1)
#define CFL_POC_CREATE_WORKFLOW_RINDEX_NONCE        (2)

#define CFL_POC_JOIN_WORKFLOW_PARAM_MIN             (4)
#define CFL_POC_JOIN_WORKFLOW_PARAM_MAX             (4)

#define CFL_POC_JOIN_WORKFLOW_PINDEX_NONCE          (0)
#define CFL_POC_JOIN_WORKFLOW_PINDEX_WORKFLOW_ID    (1)
#define CFL_POC_JOIN_WORKFLOW_PINDEX_WORKER_VKEY    (2)
#define CFL_POC_JOIN_WORKFLOW_PINDEX_PARENT_VKEY    (3)

#define CFL_POC_JOIN_WORKFLOW_RINDEX_STATUS         (0)
#define CFL_POC_JOIN_WORKFLOW_RINDEX_NONCE          (1)


#define CFL_POC_QUIT_WORKFLOW_PARAM_MIN             (4)
#define CFL_POC_QUIT_WORKFLOW_PARAM_MAX             (4)

#define CFL_POC_QUIT_WORKFLOW_PINDEX_NONCE          (0)
#define CFL_POC_QUIT_WORKFLOW_PINDEX_WORKFLOW_ID    (1)
#define CFL_POC_QUIT_WORKFLOW_PINDEX_WORKER_VKEY    (2)
#define CFL_POC_QUIT_WORKFLOW_PINDEX_PARENT_VKEY    (3)

#define CFL_POC_QUIT_WORKFLOW_RINDEX_STATUS         (0)
#define CFL_POC_QUIT_WORKFLOW_RINDEX_NONCE          (1)



#define CFL_POC_LOOKUP_WORKFLOWS_PARAM_MIN          (1)
#define CFL_POC_LOOKUP_WORKFLOWS_PARAM_MAX          (1)

#define CFL_POC_LOOKUP_WORKFLOWS_PINDEX_NONCE       (0)

#define CFL_POC_LOOKUP_WORKFLOWS_RINDEX_STATUS      (0)
#define CFL_POC_LOOKUP_WORKFLOWS_RINDEX_RESULT      (1)
#define CFL_POC_LOOKUP_WORKFLOWS_RINDEX_NONCE       (2)

#define CFL_POC_WORKFLOW_RESULT_PARAM_MIN           (1)
#define CFL_POC_WORKFLOW_RESULT_PARAM_MAX           (1)


#define CFL_POC_WORKFLOW_RESULT_PINDEX_ID           (0)

#define CFL_POC_WORKFLOW_RESULT_RINDEX_STATUS       (0)
#define CFL_POC_WORKFLOW_RESULT_RINDEX_RESULT       (1)


#define CFL_POC_REMOVE_WORKFLOW_PARAM_MIN           (2)
#define CFL_POC_REMOVE_WORKFLOW_PARAM_MAX           (2)

#define CFL_POC_REMOVE_WORKFLOW_PINDEX_NONCE        (0)
#define CFL_POC_REMOVE_WORKFLOW_PINDEX_ID           (1)

#define CFL_POC_REMOVE_WORKFLOW_RINDEX_STATUS       (0)
#define CFL_POC_REMOVE_WORKFLOW_RINDEX_NONCE        (1)


#define CFL_POC_UPDATE_WORKFLOW_PARAM_MIN           (3)
#define CFL_POC_UPDATE_WORKFLOW_PARAM_MAX           (3)

#define CFL_POC_UPDATE_WORKFLOW_PINDEX_NONCE        (0)
#define CFL_POC_UPDATE_WORKFLOW_PINDEX_ID           (1)
#define CFL_POC_UPDATE_WORKFLOW_PINDEX_STATUS       (2)

#define CFL_POC_UPDATE_WORKFLOW_RINDEX_STATUS       (0)
#define CFL_POC_UPDATE_WORKFLOW_RINDEX_NONCE        (1)


#define CFL_POC_AVAILABLE_DATASETS_PARAM_MIN        (0)
#define CFL_POC_AVAILABLE_DATASETS_PARAM_MAX        (0)

#define CFL_POC_AVAILABLE_DATASETS_RINDEX_STATUS    (0)
#define CFL_POC_AVAILABLE_DATASETS_RINDEX_RESULT    (1)


#define CFL_POC_DO_NONCE_RQST_PARAM_MIN             (3)
#define CFL_POC_DO_NONCE_RQST_PARAM_MAX             (3)

#define CFL_POC_DO_NONCE_RQST_PINDEX_ATT_DATA       (0)
#define CFL_POC_DO_NONCE_RQST_PINDEX_WORKFLOW_ID    (1)
#define CFL_POC_DO_NONCE_RQST_PINDEX_DATASET_ID     (2)

#define CFL_POC_DO_NONCE_RQST_RINDEX_STATUS         (0)
#define CFL_POC_DO_NONCE_RQST_RINDEX_REQUEST        (1)


#define CFL_POC_DO_PROCESS_RQST_PARAM_MIN           (4)
#define CFL_POC_DO_PROCESS_RQST_PARAM_MAX           (4)

#define CFL_POC_DO_PROCESS_RQST_PINDEX_WORKFLOW_ID  (0)
#define CFL_POC_DO_PROCESS_RQST_PINDEX_DATASET_ID   (1)
#define CFL_POC_DO_PROCESS_RQST_PINDEX_QUERY_DATA   (2)
#define CFL_POC_DO_PROCESS_RQST_PINDEX_JSON_RESULT  (3)

#define CFL_POC_DO_PROCESS_RQST_RINDEX_STATUS       (0)
#define CFL_POC_DO_PROCESS_RQST_RINDEX_REQUEST      (1)


#define CFL_POC_DO_PROCESS_RESP_PARAM_MIN           (2)
#define CFL_POC_DO_PROCESS_RESP_PARAM_MAX           (2)

#define CFL_POC_DO_PROCESS_RESP_PINDEX_WORKFLOW_ID  (0)
#define CFL_POC_DO_PROCESS_RESP_PINDEX_JSON_RESULT  (1)

#define CFL_POC_DO_PROCESS_RESP_RINDEX_STATUS       (0)

// this common functions reuasable by both Node and Requester enclaves

namespace cfl {
    void AddOutput(int index,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        const ByteArray& data);


    void AddOutput(int index,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        const std::string& str);

    void AddOutput(int index,
        std::vector<tcf::WorkOrderData>& out_work_order_data,
        int num);

    void AddOutput(int index,
       std::vector<tcf::WorkOrderData>& out_work_order_data,
       const char* ptr);

    void MergeOutput(ByteArray& output,
		     const std::vector<tcf::WorkOrderData>& out_work_order_data);

} //namespace cfl
