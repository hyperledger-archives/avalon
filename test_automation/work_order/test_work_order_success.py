import pytest
import logging
import json
import work_order_utility

logger = logging.getLogger(__name__)

def test_work_order_success(setup_config):
    """ Testing work order request with all valid parameter values. """

    # retrieve values from conftest session fixture
    worker_obj = setup_config[0]
    sig_obj = setup_config[1]
    uri_client = setup_config[2]
    private_key = setup_config[3]
    err_cd = setup_config[4]

    # input and output names
    input_json_file = './work_order/input/work_order_success.json'
    input_type = 'file'
    output_json_file_name = 'work_order_success'
    tamper = {"params": {}}

    # expected response
    check_submit = {"error": {"code": 5}}
    check_result = '''{"result": {"workOrderId": "", "workloadId": "",
                       "workerId": "", "requesterId": "", "workerNonce": "",
                       "workerSignature": "", "outData": ""}}'''
    check_get_result = json.loads(check_result)

    # process worker actions
    (err_cd, input_json_str1, response, processing_time,
    worker_obj, sig_obj, session_key, session_iv,
    enc_session_key) = work_order_utility.process_work_order(input_json_file,
    input_type, tamper, output_json_file_name, worker_obj, sig_obj,
    uri_client, private_key, err_cd, check_submit, check_get_result)

    if err_cd == 0:
        err_cd = work_order_utility.verify_work_order_signature(response,
                 sig_obj, worker_obj)

    if err_cd == 0:
        (err_cd, decrypted_data) = (work_order_utility.
        decrypt_work_order_response(response, enc_session_key))

    if err_cd == 0:
        logger.info('''Test Case Success : Work Order Processed successfully
                   with Signature Verification and Decrypted Response \n''')
    else:
        logger.info('''Test Case Failed : Work Order Not Processed successfully
                   with Signature Verification and Decrypted Response''')

    assert err_cd == 0
