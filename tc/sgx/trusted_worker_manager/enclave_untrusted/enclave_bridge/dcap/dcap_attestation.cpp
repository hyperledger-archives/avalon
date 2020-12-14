/* Copyright 2020 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <algorithm>
#include <string>
#include <sgx_uae_launch.h>

#include "sgx_dcap_quoteverify.h"
#include "dcap_attestation.h"
#include "sgx_utility.h"
#include "avalon_sgx_error.h"
#include "zero.h"
#include "hex_string.h"
#include "enclave_common_u.h"
#include "sgx_dcap_ql_wrapper.h"
#include "sgx_quote_3.h"
#include "sgx_utils.h"
#include "sgx_report.h"
#include "sgx_error.h"
#include "sgx_qve_header.h"
#include "sgx_ql_quote.h"
#include "sgx_urts.h"
#include "sgx_pce.h"

#include "jsonvalue.h"
#include "parson.h"
#include "types.h"
#include "utils.h"
#include "log.h"
#include "sgx_utility.h"


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DcapAttestation::DcapAttestation() {
    // Initialize the targetinfo
    quote3_error_t qe3_ret = tcf::sgx_util::CallSgx([this] () {
                return sgx_qe_get_target_info(&this->reportTargetInfo);
    });
    tcf::error::ThrowSgxError(qe3_ret,
        "Failed to initialize dcap quote in enclave constructor");
    // Initialize the quote size
    uint32_t size;
    qe3_ret = sgx_qe_get_quote_size(&size);
    tcf::error::ThrowSgxError(qe3_ret,
         "Failed to get Intel SGX quote size.");
    this->quoteSize = size;

}  // DcapAttestation::DcapAttestation

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DcapAttestation::~DcapAttestation() {

}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t DcapAttestation::GetEnclaveCharacteristics(
    const sgx_enclave_id_t& enclave_id,
    sgx_measurement_t* outEnclaveMeasurement,
    sgx_basename_t* outEnclaveBasename) {
    tcf::error::ThrowIfNull(outEnclaveMeasurement,
        "Enclave measurement pointer is NULL");
    tcf::error::ThrowIfNull(outEnclaveBasename,
        "Enclave basename pointer is NULL");

    Zero(outEnclaveMeasurement, sizeof(*outEnclaveMeasurement));
    Zero(outEnclaveBasename, sizeof(*outEnclaveBasename));

    // We can get the enclave's measurement (i.e., mr_enclave) and
    // basename only by getting a quote. To do that, we need to first
    // generate a report.

    // Initialize a quote
    sgx_target_info_t targetInfo = { 0 };

    quote3_error_t ret = tcf::sgx_util::CallSgx([&targetInfo] () {
        return sgx_qe_get_target_info(&targetInfo);
    });
    tcf::error::ThrowSgxError(ret, "Failed to initialize enclave quote");

    // Now retrieve a fake enclave report so that we can later
    // create a quote from it. We need to the quote so that we can
    // get some of the information (basename and mr_enclave,
    // specifically) being requested.
    sgx_report_t enclaveReport = { 0 };
    tcf_err_t tcfRet = TCF_SUCCESS;
    sgx_status_t s_ret = tcf::sgx_util::CallSgx(
        [&enclave_id,
         &tcfRet,
         &targetInfo,
         &enclaveReport] () {
            sgx_status_t ret =
            ecall_CreateErsatzEnclaveReport(
                enclave_id,
                &tcfRet,
                &targetInfo,
                &enclaveReport);
            return tcf::error::ConvertErrorStatus(ret, tcfRet);
        });
    tcf::error::ThrowSgxError(s_ret,
        "Failed to retrieve ersatz enclave report");

    if (tcfRet != TCF_SUCCESS) {
      return tcfRet;
    }

    // Properly size a buffer to receive an enclave quote and then
    // retrieve it. The enclave quote contains the basename.
    ByteArray enclaveQuoteBuffer(this->quoteSize);
    sgx_quote_t* enclaveQuote = reinterpret_cast<sgx_quote_t *>(&enclaveQuoteBuffer[0]);

    uint32_t quote_size = 0;
    quote3_error_t qe3_ret = sgx_qe_get_quote_size(&quote_size);
    tcf::error::ThrowSgxError(qe3_ret,
        "Failed to calculate the quote size");

    this->quoteSize = quote_size;
    uint8_t* p_quote_buffer = NULL;
    p_quote_buffer = (uint8_t*)malloc(this->quoteSize);
    memset(p_quote_buffer, 0, this->quoteSize);
    quote3_error_t sresult = tcf::sgx_util::CallSgx(
        [this,
         &enclaveReport,
         p_quote_buffer] () {
             return sgx_qe_get_quote(
                 &enclaveReport,
                 this->quoteSize,
                 p_quote_buffer);
        });
    tcf::error::ThrowSgxError(
        sresult,
        "Failed to get DCAP quote from the enclave");
    std::copy(p_quote_buffer, p_quote_buffer+this->quoteSize,
        enclaveQuoteBuffer.begin());

    // Copy the mr_enclave and basename to the caller's buffers
    memcpy_s(outEnclaveMeasurement,
        sizeof(*outEnclaveMeasurement),
        &enclaveQuote->report_body.mr_enclave,
        sizeof(*outEnclaveMeasurement));
    memcpy_s(outEnclaveBasename,
        sizeof(*outEnclaveBasename),
        &enclaveQuote->basename,
        sizeof(*outEnclaveBasename));
    return TCF_SUCCESS;
}  // DcapAttestation::GetEnclaveCharacteristics

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
size_t DcapAttestation::GetQuoteSize(void) {
    return this->quoteSize;
} // GetQuoteSize

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void DcapAttestation::CreateQuoteFromReport(
    const sgx_report_t* inEnclaveReport,
    ByteArray& outEnclaveQuote) {
    // Properly size the enclave quote buffer for the caller and zero
    // it out so we have predictable contents.
    outEnclaveQuote.resize(this->quoteSize);
    uint8_t* p_quote_buffer = NULL;
    p_quote_buffer = (uint8_t*)malloc(this->quoteSize);
    memset(p_quote_buffer, 0, this->quoteSize);
    quote3_error_t sresult =
        tcf::sgx_util::CallSgx(
            [&inEnclaveReport,
             this,
             p_quote_buffer] () {
                 return sgx_qe_get_quote(
                     inEnclaveReport,
                     this->quoteSize,
                     p_quote_buffer);
            });
    tcf::error::ThrowSgxError(sresult,
        "Failed to get the DCAP quote from enclave");
    std::copy(p_quote_buffer,
        p_quote_buffer+this->quoteSize,
        outEnclaveQuote.begin());

}  // DcapAttestation::CreateQuoteFromReport

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void DcapAttestation::InitQuote(sgx_target_info_t& target_info) {
    quote3_error_t qe3_ret = tcf::sgx_util::CallSgx(
        [&target_info] () {
            return sgx_qe_get_target_info(&target_info);
        });
    tcf::error::ThrowSgxError(qe3_ret,
        "Intel SGX enclave call failed (sgx_qe_get_target_info);"
        " failed to initialize target info");
} // DcapAttestation::InitQuote

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#ifdef BUILD_SINGLETON
tcf_err_t DcapAttestation::VerifyEnclaveInfoSingleton(
    const std::string& enclaveInfo, const std::string& mr_enclave,
    const sgx_enclave_id_t& enclave_id) {

    tcf_err_t presult = TCF_SUCCESS;
    tcf_err_t result = this->VerifyEnclaveInfo(enclaveInfo, enclave_id);
    tcf::error::ThrowSgxError(result,
        "Failed to verify DCAP enclave info");

    sgx_status_t sresult = tcf::sgx_util::CallSgx(
        [ enclave_id,
          &presult,
          enclaveInfo,
          mr_enclave ] () {
              sgx_status_t sresult = ecall_VerifyEnclaveInfoDcap(
                     enclave_id,
                     &presult,
                     enclaveInfo.c_str(),
                     mr_enclave.c_str());
        return tcf::error::ConvertErrorStatus(sresult, presult);
    });

    tcf::error::ThrowSgxError(sresult,
        "Intel SGX enclave call failed (ecall_VerifyEnclaveInfoDcap)");
    return presult;
}  // DcapAttestation::VerifyEnclaveInfoSingleton

#elif BUILD_KME
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tcf_err_t DcapAttestation::VerifyEnclaveInfoKME(
    const std::string& enclaveInfo, const std::string& mr_enclave,
    const std::string& ext_data, const sgx_enclave_id_t& enclave_id) {
    tcf_err_t presult = TCF_SUCCESS;

    tcf_err_t result = this->VerifyEnclaveInfo(enclaveInfo, enclave_id);
    tcf::error::ThrowIf<tcf::error::ValueError>(result != TCF_SUCCESS,
        "Failed to verify DCAP enclave info");
    ByteArray ext_data_bytes = HexEncodedStringToByteArray(ext_data);
    sgx_status_t sresult = tcf::sgx_util::CallSgx(
        [ enclave_id,
          &presult,
          enclaveInfo,
          mr_enclave,
          ext_data_bytes ] () {
              sgx_status_t sresult = ecall_VerifyEnclaveInfoKMEDcap(
                     enclave_id,
                     &presult,
                     enclaveInfo.c_str(),
                     mr_enclave.c_str(),
                     ext_data_bytes.data(),
                     ext_data_bytes.size());
         return tcf::error::ConvertErrorStatus(sresult, presult);
    });

    tcf::error::ThrowSgxError(sresult,
        "Intel SGX enclave call failed (ecall_VerifyEnclaveInfoKMEDcap)");
    return presult;
}  // DcapAttestation::VerifyEnclaveInfoKME

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#elif BUILD_WPE
tcf_err_t DcapAttestation::VerifyEnclaveInfoWPE(
    const std::string& enclaveInfo, const std::string& mr_enclave,
    const std::string& ext_data, const sgx_enclave_id_t& enclave_id) {
    tcf_err_t presult = TCF_SUCCESS;

    tcf_err_t result = this->VerifyEnclaveInfo(enclaveInfo, enclave_id);
    tcf::error::ThrowIf<tcf::error::ValueError>(result != TCF_SUCCESS,
        "Failed to verify DCAP enclave info");
    sgx_status_t sresult = tcf::sgx_util::CallSgx(
        [ enclave_id,
          &presult,
          enclaveInfo,
          mr_enclave,
          ext_data ] () {
              sgx_status_t sresult = ecall_VerifyEnclaveInfoWPEDcap(
                  enclave_id,
                  &presult,
                  enclaveInfo.c_str(),
                  mr_enclave.c_str(),
                  ext_data.c_str());
              return tcf::error::ConvertErrorStatus(sresult,
                      presult);
        });

    tcf::error::ThrowSgxError(sresult,
        "Intel SGX enclave call failed (ecall_VerifyEnclaveInfoWPEDcap)");
    return presult;
}  // DcapAttestation::VerifyEnclaveInfoWPE
#endif

tcf_err_t DcapAttestation::VerifyEnclaveInfo(const std::string& enclave_info,
   const sgx_enclave_id_t& enclave_id) {
   tcf_err_t result = TCF_SUCCESS;
   sgx_status_t sgx_ret = SGX_SUCCESS;
   quote3_error_t dcap_ret = SGX_QL_ERROR_UNEXPECTED;
   sgx_ql_qv_result_t quote_verification_result = SGX_QL_QV_RESULT_UNSPECIFIED;
   sgx_ql_qe_report_info_t qve_report_info;
   uint32_t supplemental_data_size = 0;
   uint8_t *p_supplemental_data = NULL;
   unsigned char rand_nonce[16] = "59jslk201fgjmm;";
   time_t current_time = 0;
   uint32_t collateral_expiration_status = 1;
   quote3_error_t verify_qveid_ret = SGX_QL_ERROR_UNEXPECTED;

   // Parse the enclave_info
   JsonValue enclave_info_parsed(json_parse_string(enclave_info.c_str()));
   tcf::error::ThrowIfNull(enclave_info_parsed.value,
       "Failed to parse the enclave info, badly formed JSON");

   JSON_Object* enclave_info_object = \
       json_value_get_object(enclave_info_parsed);
   tcf::error::ThrowIfNull(enclave_info_object,
       "Invalid enclave_info, expecting object");

   const char* svalue = nullptr;
   svalue = json_object_dotget_string(enclave_info_object, "verifying_key");
   tcf::error::ThrowIfNull(svalue, "Invalid verifying_key");

   svalue = json_object_dotget_string(enclave_info_object, "encryption_key");
   tcf::error::ThrowIfNull(svalue, "Invalid encryption_key");

   // Parse proof data
   svalue = json_object_dotget_string(enclave_info_object, "proof_data");
   std::string proof_data(svalue);
   JsonValue proof_data_parsed(json_parse_string(proof_data.c_str()));
   tcf::error::ThrowIfNull(proof_data_parsed.value,
       "Failed to parse the proofData, badly formed JSON");
   JSON_Object* proof_object = json_value_get_object(proof_data_parsed);
   tcf::error::ThrowIfNull(proof_object, "Invalid proof, expecting object");

   //Parse verification report
   svalue = json_object_dotget_string(proof_object, "verification_report");
   tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
   const std::string verification_report(svalue);

   ByteArray quote = Base64EncodedStringToByteArray(verification_report);
   // Set nonce
   memcpy(qve_report_info.nonce.rand, rand_nonce, sizeof(rand_nonce));

   // Get target info of the current Enclave.
   // QvE will target the generated report to this enclave.
   sgx_status_t get_target_info_ret;
   sgx_ret = ecall_get_target_info(enclave_id,
        &get_target_info_ret, &qve_report_info.app_enclave_target_info);
   tcf::error::ThrowSgxError(sgx_ret,
       "Failed to get target info while verifying DCAP quote");

   //this->InitQuote(qve_report_info.app_enclave_target_info);

   // Call DCAP quote verify library to set QvE loading policy
   dcap_ret = sgx_qv_set_enclave_load_policy(SGX_QL_DEFAULT);
   tcf::error::ThrowIf<tcf::error::ValueError>(dcap_ret != SGX_QL_SUCCESS,
       "Error: failed to set quote verifying enclave load policy");

   // Call DCAP quote verify library to get supplemental data size
   dcap_ret = sgx_qv_get_quote_supplemental_data_size(&supplemental_data_size);
   if (dcap_ret == SGX_QL_SUCCESS) {
       p_supplemental_data = (uint8_t*)malloc(supplemental_data_size);
   }
   else {
       tcf::error::ThrowIf<tcf::error::ValueError>(dcap_ret != SGX_QL_SUCCESS,
           "Error: failed to get quote supplement data size");
   }

   // Set current time. This is only for sample purposes,
   // in production mode a trusted time should be used.
   current_time = time(NULL);

   // Call DCAP quote verify library for quote verification
   // Here we can choose 'trusted' or 'untrusted' quote verification
   // by specifying parameter '&qve_report_info'
   // If '&qve_report_info' is NOT NULL, this API will call Intel QvE to verify quote
   // If '&qve_report_info' is NULL, this API will call 'untrusted quote verify lib'
   // to verify quote, this mode doesn't rely on SGX capable system,
   // but the results can not be cryptographically authenticated.

   std::string err_str1 = "Error: Dcap Quote verification "
       "failed with error code ";
   dcap_ret = sgx_qv_verify_quote(
       quote.data(), (uint32_t)quote.size(),
       NULL,
       current_time,
       &collateral_expiration_status,
       &quote_verification_result,
       &qve_report_info,
       supplemental_data_size,
       p_supplemental_data);
   err_str1 += std::to_string(static_cast<int>(dcap_ret));
   tcf::error::ThrowIf<tcf::error::ValueError>(dcap_ret != SGX_QL_SUCCESS,
       err_str1.c_str());

   // Threshold of QvE ISV SVN.
   // The ISV SVN of QvE used to verify quote must be greater or
   // equal to this threshold
   // e.g. You can get latest QvE ISVSVN in QvE Identity JSON file from
   // https://api.trustedservices.intel.com/sgx/certification/v2/qve/identity
   // Make sure you are using trusted & latest QvE ISV SVN as threshold

   sgx_isv_svn_t qve_isvsvn_threshold = 3;

   std::string err_str2 = "Error: Dcap Quote verifying enclave indentity "
       "is failed with ";
   // Call sgx_dcap_tvl API in SampleISVEnclave to verify QvE's
   // report and identity
   sgx_ret = sgx_tvl_verify_qve_report_and_identity(enclave_id,
           &verify_qveid_ret,
           quote.data(),
           (uint32_t) quote.size(),
           &qve_report_info,
           current_time,
           collateral_expiration_status,
           quote_verification_result,
           p_supplemental_data,
           supplemental_data_size,
           qve_isvsvn_threshold);

   std::string sgx_err_code = std::to_string(static_cast<int>(sgx_ret));
   std::string qve_err_code = std::to_string(static_cast<int>(
       verify_qveid_ret));
   err_str2 += " SGX error " + sgx_err_code + " QVE error " + qve_err_code;
   tcf::error::ThrowIf<tcf::error::ValueError>(
       (sgx_ret != SGX_SUCCESS || verify_qveid_ret != SGX_QL_SUCCESS),
       err_str2.c_str());

   // Check verification result
   switch (quote_verification_result)
   {
       case SGX_QL_QV_RESULT_OK:
           result = TCF_SUCCESS;
           tcf::Log(TCF_LOG_INFO, "Verification completed successfully: %d\n",(int)quote_verification_result);
           break;
       case SGX_QL_QV_RESULT_CONFIG_NEEDED:
       case SGX_QL_QV_RESULT_OUT_OF_DATE:
       case SGX_QL_QV_RESULT_OUT_OF_DATE_CONFIG_NEEDED:
       case SGX_QL_QV_RESULT_SW_HARDENING_NEEDED:
       case SGX_QL_QV_RESULT_CONFIG_AND_SW_HARDENING_NEEDED:
           result = TCF_SUCCESS;
           tcf::Log(TCF_LOG_WARNING, "Verification completed with Non-terminal result: %x",
               (int)quote_verification_result);
           break;
       case SGX_QL_QV_RESULT_INVALID_SIGNATURE:
       case SGX_QL_QV_RESULT_REVOKED:
       case SGX_QL_QV_RESULT_UNSPECIFIED:
       default:
           tcf::error::ThrowIf<tcf::error::ValueError>(
               false,
               "Error: Quote Verification completed with Terminal result:");
           result = TCF_ERR_UNKNOWN;
           break;
   }
   return result;
} // VerifyEnclaveInfo
