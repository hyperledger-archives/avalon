# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import time

from ssl import SSLError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import utility.ias_client as ias_client
import tcf_enclave_manager.tcf_enclave as enclave

import logging
logger = logging.getLogger(__name__)

TCFHOME = os.environ.get("TCF_HOME", "../../../")

send_to_sgx_worker = enclave.HandleWorkOrderRequest
get_enclave_public_info = enclave.UnsealEnclaveData


# -----------------------------------------------------------------
_tcf_enclave_info = None
_ias = None

_sig_rl_update_time = None
_sig_rl_update_period = 8 * 60 * 60  # in seconds every 8 hours

_epid_group = None


# ----------------------------------------------------------------
def __find_enclave_library(config):
    """
    Find enclave library file from the parsed config
    """
    enclave_file_name = config.get('enclave_library')
    enclave_file_path = TCFHOME + "/" + config.get('enclave_library_path')
    logger.info("Enclave Lib: %s", enclave_file_name)

    if enclave_file_path:
        enclave_file = os.path.join(enclave_file_path, enclave_file_name)
        if os.path.exists(enclave_file):
            logger.info("Enclave Lib Exists")
            return enclave_file
    else:
        script_directory = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        logger.info("Script directory - %s", script_directory)
        search_path = [
            script_directory,
            os.path.abspath(os.path.join(script_directory, '..', 'lib')),
        ]

        for path in search_path:
            enclave_file = os.path.join(path, enclave_file_name)
            if os.path.exists(enclave_file):
                logger.info("Enclave Lib Exits")
                return enclave_file

    raise IOError("Could not find enclave shared object")


# -----------------------------------------------------------------
def __update_sig_rl():
    """
    Update the signature revocation lists for EPID group on IAS server
    """
    global _epid_group
    global _sig_rl_update_time
    global _sig_rl_update_period

    if _epid_group is None:
        _epid_group = _tcf_enclave_info.get_epid_group()
    logger.info("EPID: " + _epid_group)

    if not _sig_rl_update_time \
            or (time.time() - _sig_rl_update_time) > _sig_rl_update_period:
        sig_rl = ""
        if (not enclave.is_sgx_simulator()):
            sig_rl = _ias.get_signature_revocation_lists(_epid_group)
            logger.debug("Received SigRl of {} bytes ".format(len(sig_rl)))

        _tcf_enclave_info.set_signature_revocation_list(sig_rl)
        _sig_rl_update_time = time.time()


# -----------------------------------------------------------------
def initialize_with_configuration(config):
    """
    Create and Initialize a SGX enclave with passed config
    """
    global _tcf_enclave_info
    global _ias
    global logger

    enclave._SetLogger(logger)

    # Ensure that the required keys are in the configuration
    valid_keys = set(['spid', 'ias_url', 'ias_api_key'])
    found_keys = set(config.keys())

    missing_keys = valid_keys.difference(found_keys)
    if missing_keys:
        raise \
            ValueError(
                'TCF enclave config file missing the following keys: '
                '{}'.format(
                    ', '.join(sorted(list(missing_keys)))))
    # IAS is not initialized in SGX SIM mode
    if not _ias and not enclave.is_sgx_simulator():
        _ias = \
            ias_client.IasClient(
                IasServer=config['ias_url'],
                ApiKey=config['ias_api_key'],
                Spid=config['spid'],
                HttpsProxy=config.get('https_proxy', ""))

    if not _tcf_enclave_info:
        signed_enclave = __find_enclave_library(config)
        logger.debug("Attempting to load enclave at: %s", signed_enclave)
        _tcf_enclave_info = enclave.tcf_enclave_info(signed_enclave, config['spid'], int(config['num_of_enclaves']))
        logger.info("Basename: %s", get_enclave_basename())
        logger.info("MRENCLAVE: %s", get_enclave_measurement())

    sig_rl_updated = False
    while not sig_rl_updated:
        try:
            __update_sig_rl()
            sig_rl_updated = True
        except (SSLError, Timeout, HTTPError) as e:
            logger.warning("Failed to retrieve initial sig rl from IAS: %s", str(e))
            logger.warning("Retrying in 60 sec")
            time.sleep(60)

    return get_enclave_basename(), get_enclave_measurement()


# -----------------------------------------------------------------
def shutdown():
    global _tcf_enclave_info
    global _ias
    global _sig_rl_update_time
    global _epid_group

    _tcf_enclave_info = None
    _ias = None
    _sig_rl_update_time = None
    _epid_group = None


# -----------------------------------------------------------------
def get_enclave_measurement():
    global _tcf_enclave_info
    return _tcf_enclave_info.mr_enclave if _tcf_enclave_info is not None else None


# -----------------------------------------------------------------
def get_enclave_basename():
    global _tcf_enclave_info
    return _tcf_enclave_info.basename if _tcf_enclave_info is not None else None


# -----------------------------------------------------------------
def verify_enclave_info(enclave_info, mr_enclave, originator_public_key_hash):
    """
    Verifies enclave signup info
    - enclave_info is a JSON serialised enclave signup info
      along with IAS attestation report
    - mr_enclave is enclave measurement value
    """
    return enclave.VerifyEnclaveInfo(enclave_info, mr_enclave, originator_public_key_hash)


# -----------------------------------------------------------------
def create_signup_info(originator_public_key_hash, nonce):
    """
    Create enclave signup data
    """
    # Part of what is returned with the signup data is an enclave quote, we
    # want to update the revocation list first.
    __update_sig_rl()
    # Now, let the enclave create the signup data
    signup_data = enclave.CreateEnclaveData(originator_public_key_hash)
    if signup_data is None:
        return None

    # We don't really have any reason to call back down into the enclave
    # as we have everything we now need.  For other objects such as wait
    # timer and certificate they are serialized into JSON down in C++ code.
    #
    # Start building up the signup info dictionary we will serialize
    signup_info = {
        'verifying_key': signup_data['verifying_key'],
        'encryption_key': signup_data['encryption_key'],
        'proof_data': 'Not present',
        'enclave_persistent_id': 'Not present'
    }

    # If we are not running in the simulator, we are going to go and get
    # an attestation verification report for our signup data.
    if not enclave.is_sgx_simulator():
        logger.debug("posting verification to IAS")
        response = _ias.post_verify_attestation(quote=signup_data['enclave_quote'], nonce=nonce)
        logger.debug("posted verification to IAS")

        # check verification report
        if not _ias.verify_report_fields(signup_data['enclave_quote'], response['verification_report']):
            logger.debug("last error: " + _ias.last_verification_error())
            if _ias.last_verification_error() == "GROUP_OUT_OF_DATE":
                logger.warning("failure GROUP_OUT_OF_DATE (update your BIOS/microcode!!!) keep going")
            else:
                logger.error("invalid report fields")
                return None
        # ALL checks have passed
        logger.info("report fields verified")

        # Now put the proof data into the dictionary
        signup_info['proof_data'] = \
            json.dumps({
                'verification_report': response['verification_report'],
                'ias_report_signature': response['ias_signature'],
                'ias_report_signing_certificate': response['ias_certificate']
            })
        # Grab the EPID pseudonym and put it in the enclave-persistent ID for the
        # signup info
        verification_report_dict = json.loads(response['verification_report'])
        signup_info['enclave_persistent_id'] = verification_report_dict.get('epidPseudonym')

        mr_enclave = get_enclave_measurement()
        status = verify_enclave_info(json.dumps(signup_info), mr_enclave, originator_public_key_hash)
        if status != 0:
            logger.error("Verification of enclave signup info failed")
        else:
            logger.info("Verification of enclave signup info passed")
    # Now we can finally serialize the signup info and create a corresponding
    # signup info object. Because we don't want the sealed signup data in the
    # serialized version, we set it separately.
    signup_info_obj = enclave.deserialize_signup_info(json.dumps(signup_info))
    signup_info_obj.sealed_signup_data = signup_data['sealed_enclave_data']

    # Now we can return the real object
    return signup_info_obj
