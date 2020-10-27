#include <string.h>
#include <sgx_quote.h>

#include "data-owner-node-config.h"
#include "cfl-utils.h"

#include "verify-workers.h"
#include "parson.h"
#include "jsonvalue.h"
#include "error.h"
#include "tcf_error.h"
#include "types.h"
#include "verify-report.h"
#include "utils.h"


namespace CflPocDataOwner {

	extern DataOwnerNodeConfig dataOwnerNodeConfig;
}

using CflPocDataOwner::dataOwnerNodeConfig;

namespace cfl {

const char * cert_pem = "-----BEGIN CERTIFICATE-----\n"
"MIIEoTCCAwmgAwIBAgIJANEHdl0yo7CWMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV\n"
"BAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV\n"
"BAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0\n"
"YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwHhcNMTYxMTIyMDkzNjU4WhcNMjYxMTIw\n"
"MDkzNjU4WjB7MQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExFDASBgNVBAcMC1Nh\n"
"bnRhIENsYXJhMRowGAYDVQQKDBFJbnRlbCBDb3Jwb3JhdGlvbjEtMCsGA1UEAwwk\n"
"SW50ZWwgU0dYIEF0dGVzdGF0aW9uIFJlcG9ydCBTaWduaW5nMIIBIjANBgkqhkiG\n"
"9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqXot4OZuphR8nudFrAFiaGxxkgma/Es/BA+t\n"
"beCTUR106AL1ENcWA4FX3K+E9BBL0/7X5rj5nIgX/R/1ubhkKWw9gfqPG3KeAtId\n"
"cv/uTO1yXv50vqaPvE1CRChvzdS/ZEBqQ5oVvLTPZ3VEicQjlytKgN9cLnxbwtuv\n"
"LUK7eyRPfJW/ksddOzP8VBBniolYnRCD2jrMRZ8nBM2ZWYwnXnwYeOAHV+W9tOhA\n"
"ImwRwKF/95yAsVwd21ryHMJBcGH70qLagZ7Ttyt++qO/6+KAXJuKwZqjRlEtSEz8\n"
"gZQeFfVYgcwSfo96oSMAzVr7V0L6HSDLRnpb6xxmbPdqNol4tQIDAQABo4GkMIGh\n"
"MB8GA1UdIwQYMBaAFHhDe3amfrzQr35CN+s1fDuHAVE8MA4GA1UdDwEB/wQEAwIG\n"
"wDAMBgNVHRMBAf8EAjAAMGAGA1UdHwRZMFcwVaBToFGGT2h0dHA6Ly90cnVzdGVk\n"
"c2VydmljZXMuaW50ZWwuY29tL2NvbnRlbnQvQ1JML1NHWC9BdHRlc3RhdGlvblJl\n"
"cG9ydFNpZ25pbmdDQS5jcmwwDQYJKoZIhvcNAQELBQADggGBAGcIthtcK9IVRz4r\n"
"Rq+ZKE+7k50/OxUsmW8aavOzKb0iCx07YQ9rzi5nU73tME2yGRLzhSViFs/LpFa9\n"
"lpQL6JL1aQwmDR74TxYGBAIi5f4I5TJoCCEqRHz91kpG6Uvyn2tLmnIdJbPE4vYv\n"
"WLrtXXfFBSSPD4Afn7+3/XUggAlc7oCTizOfbbtOFlYA4g5KcYgS1J2ZAeMQqbUd\n"
"ZseZCcaZZZn65tdqee8UXZlDvx0+NdO0LR+5pFy+juM0wWbu59MvzcmTXbjsi7HY\n"
"6zd53Yq5K244fwFHRQ8eOB0IWB+4PfM7FeAApZvlfqlKOlLcZL2uyVmzRkyR5yW7\n"
"2uo9mehX44CiPJ2fse9Y6eQtcfEhMPkmHXI01sN+KwPbpA39+xOsStjhP9N1Y1a2\n"
"tQAVo+yVgLgV2Hws73Fc0o3wC78qPEA+v2aRs/Be3ZFDgDyghc/1fgU+7C+P6kbq\n"
"d4poyb6IW8KCJbxfMJvkordNOgOUUxndPHEi/tb/U7uLjLOgPA==\n"
"-----END CERTIFICATE-----\n"
"-----BEGIN CERTIFICATE-----\n"
"MIIFSzCCA7OgAwIBAgIJANEHdl0yo7CUMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV\n"
"BAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwLU2FudGEgQ2xhcmExGjAYBgNV\n"
"BAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQDDCdJbnRlbCBTR1ggQXR0ZXN0\n"
"YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwIBcNMTYxMTE0MTUzNzMxWhgPMjA0OTEy\n"
"MzEyMzU5NTlaMH4xCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEUMBIGA1UEBwwL\n"
"U2FudGEgQ2xhcmExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0aW9uMTAwLgYDVQQD\n"
"DCdJbnRlbCBTR1ggQXR0ZXN0YXRpb24gUmVwb3J0IFNpZ25pbmcgQ0EwggGiMA0G\n"
"CSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCfPGR+tXc8u1EtJzLA10Feu1Wg+p7e\n"
"LmSRmeaCHbkQ1TF3Nwl3RmpqXkeGzNLd69QUnWovYyVSndEMyYc3sHecGgfinEeh\n"
"rgBJSEdsSJ9FpaFdesjsxqzGRa20PYdnnfWcCTvFoulpbFR4VBuXnnVLVzkUvlXT\n"
"L/TAnd8nIZk0zZkFJ7P5LtePvykkar7LcSQO85wtcQe0R1Raf/sQ6wYKaKmFgCGe\n"
"NpEJUmg4ktal4qgIAxk+QHUxQE42sxViN5mqglB0QJdUot/o9a/V/mMeH8KvOAiQ\n"
"byinkNndn+Bgk5sSV5DFgF0DffVqmVMblt5p3jPtImzBIH0QQrXJq39AT8cRwP5H\n"
"afuVeLHcDsRp6hol4P+ZFIhu8mmbI1u0hH3W/0C2BuYXB5PC+5izFFh/nP0lc2Lf\n"
"6rELO9LZdnOhpL1ExFOq9H/B8tPQ84T3Sgb4nAifDabNt/zu6MmCGo5U8lwEFtGM\n"
"RoOaX4AS+909x00lYnmtwsDVWv9vBiJCXRsCAwEAAaOByTCBxjBgBgNVHR8EWTBX\n"
"MFWgU6BRhk9odHRwOi8vdHJ1c3RlZHNlcnZpY2VzLmludGVsLmNvbS9jb250ZW50\n"
"L0NSTC9TR1gvQXR0ZXN0YXRpb25SZXBvcnRTaWduaW5nQ0EuY3JsMB0GA1UdDgQW\n"
"BBR4Q3t2pn680K9+QjfrNXw7hwFRPDAfBgNVHSMEGDAWgBR4Q3t2pn680K9+Qjfr\n"
"NXw7hwFRPDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBADANBgkq\n"
"hkiG9w0BAQsFAAOCAYEAeF8tYMXICvQqeXYQITkV2oLJsp6J4JAqJabHWxYJHGir\n"
"IEqucRiJSSx+HjIJEUVaj8E0QjEud6Y5lNmXlcjqRXaCPOqK0eGRz6hi+ripMtPZ\n"
"sFNaBwLQVV905SDjAzDzNIDnrcnXyB4gcDFCvwDFKKgLRjOB/WAqgscDUoGq5ZVi\n"
"zLUzTqiQPmULAQaB9c6Oti6snEFJiCQ67JLyW/E83/frzCmO5Ru6WjU4tmsmy8Ra\n"
"Ud4APK0wZTGtfPXU7w+IBdG5Ez0kE1qzxGQaL4gINJ1zMyleDnbuS8UicjJijvqA\n"
"152Sq049ESDz+1rRGc2NVEqh1KaGXmtXvqxXcTB+Ljy5Bw2ke0v8iGngFBPqCTVB\n"
"3op5KBG3RjbF6RRSzwzuWfL7QErNC8WEy5yDVARzTA5+xmBc388v9Dm21HGfcC8O\n"
"DD+gT9sSpssq0ascmvH49MOgjt1yoysLtdCtJW/9FZpoOypaHx0R+mJTLwPXVMrv\n"
"DaVzWh5aiEx+idkSGMnX\n"
"-----END CERTIFICATE-----\n";


bool VerifyWorker(const char* worker_info, const ByteArray& nonce,  GrapheneWorker& worker)
{
    const char* svalue = nullptr;

    JsonValue worker_info_json(json_parse_string(worker_info));
    tcf::error::ThrowIfNull(worker_info_json.value, "Failed to parse the worker info, badly formed JSON");

    JSON_Object* worker_info_object = json_value_get_object(worker_info_json);
    tcf::error::ThrowIfNull(worker_info_object, "Invalid worker_info, expecting object");

    svalue = json_object_dotget_string(worker_info_object, "verifying_key");
    tcf::error::ThrowIfNull(svalue, "Invalid verifying_key");
    std::string verification_key(svalue);

    svalue = json_object_dotget_string(worker_info_object, "encryption_key");
    tcf::error::ThrowIfNull(svalue, "Invalid encryption_key");
    std::string encryption_key(svalue);

    // Parse proof data
    svalue = json_object_dotget_string(worker_info_object, "proof_data");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_data");
    std::string proof_data(svalue);
    JsonValue proof_data_json(json_parse_string(proof_data.c_str()));
    tcf::error::ThrowIfNull(proof_data_json.value, "Failed to parse the proofData, badly formed JSON");
    JSON_Object* proof_object = json_value_get_object(proof_data_json);
    tcf::error::ThrowIfNull(proof_object, "Invalid proof, expecting object");

    svalue = json_object_dotget_string(proof_object, "ias_report_signature");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_signature");
    const std::string proof_signature(svalue);

    //Parse verification report
    const char* verification_report = json_object_dotget_string(proof_object, "verification_report");
    tcf::error::ThrowIfNull(svalue, "Invalid proof_verification_report");
    JsonValue verification_report_json(json_parse_string(verification_report));
    tcf::error::ThrowIfNull(verification_report_json.value, "Failed to parse the verificationReport, badly formed JSON");
    JSON_Object* verification_report_object = json_value_get_object(verification_report_json);
    tcf::error::ThrowIfNull(verification_report_object, "Invalid verification_report, expecting object");

    if (!VerifyReportFields(verification_report_object))
    {
	return false;
    }

    if(!verify_enclave_quote_status(verification_report, strlen(verification_report), 1))
    {
	return false;
    }

    std::vector<char> proof_signature_vec(proof_signature.begin(), proof_signature.end());
    proof_signature_vec.push_back('\0');
    char* proof_signature_arr = &proof_signature_vec[0];
    if (!verify_ias_report_signature(cert_pem,
                                     verification_report,
                                     strlen(verification_report),
                                     proof_signature_arr,
                                     strlen(proof_signature_arr)))
    {
	return false;
    }
    if (!ExtractQuoteBody(verification_report_object, verification_key, encryption_key, nonce, worker))
    {
        return false;
    }

    worker.worker_vkey = Base64EncodedStringToByteArray(verification_key);
    worker.worker_ekey = StrToByteArray(encryption_key);

    return true;

}

bool VerifyReportFields(JSON_Object* verification_report_object)
{
    const char* svalue = nullptr;

    svalue = json_object_dotget_string(verification_report_object, "id");
    tcf::error::ThrowIfNull(svalue, "AVR does not contain id field");

    svalue = json_object_dotget_string(verification_report_object, "revocationReason");
    if (svalue != nullptr)
    {
	throw tcf::error::ValueError("AVR indicates the EPID group has been revoked");
    }

    svalue = json_object_dotget_string(verification_report_object, "isvEnclaveQuoteStatus");
    tcf::error::ThrowIfNull(svalue, "AVR does not include an enclave quote status");

    svalue = json_object_dotget_string(verification_report_object, "isvEnclaveQuoteBody");
    tcf::error::ThrowIfNull(svalue, "AVR does not contain quote body");

    svalue = json_object_dotget_string(verification_report_object, "epidPseudonym");
    tcf::error::ThrowIfNull(svalue, "AVR does not contain an EPID pseudonym");

    svalue = json_object_dotget_string(verification_report_object, "nonce");
    tcf::error::ThrowIfNull(svalue, "AVR does not contain a nonce");

    return true;
}

ByteArray CalculateReportData(const std::string& vkey, const std::string& ekey, const ByteArray & nonce)
{
    std::string vkey_pem = AddBeginEndBlockToVerificationKey(vkey);
    std::string concat_str = vkey_pem + ekey;
    ByteArray hash = tcf::crypto::ComputeMessageHash(StrToByteArray(concat_str));
    hash.insert(hash.end(), nonce.begin(), nonce.end());
    return hash;
}


bool ExtractQuoteBody(JSON_Object* verification_report_object, 
		    const std::string& vkey, 
		    const std::string& ekey, 
		    const ByteArray & nonce, 
		    GrapheneWorker& worker)
{
    const char* svalue = json_object_dotget_string(verification_report_object, "isvEnclaveQuoteBody");
    tcf::error::ThrowIfNull(svalue, "Invalid enclave_quote_body");
    const std::string enclave_quote_body(svalue);
    ByteArray enclave_quote_body_byte = Base64EncodedStringToByteArray(enclave_quote_body);

    sgx_quote_t* quote_body = reinterpret_cast<sgx_quote_t*>(enclave_quote_body_byte.data());

    //Verify treport dataaaaaaaaa
    sgx_report_body_t* report_body = &quote_body->report_body;
    uint8_t* expected_report_data = (report_body->report_data).d;
    ByteArray computed_report_data = CalculateReportData(vkey, ekey, nonce);
    ByteArray expected_report_data_byte(expected_report_data, expected_report_data + SGX_REPORT_DATA_SIZE);

    std::string error_msg = "Invalid Report data: computedReportData " + ByteArrayToHexEncodedString(computed_report_data) + " does not match expectedReportData " + ByteArrayToHexEncodedString(expected_report_data_byte);

    tcf::error::ThrowIf<tcf::error::ValueError>(
        memcmp(computed_report_data.data(), expected_report_data, SGX_REPORT_DATA_SIZE)  != 0,
        error_msg.c_str());

    const std::vector<WorkerMeasurement>& worker_measurements = dataOwnerNodeConfig.GetWorkerMeasurements();

    for(const WorkerMeasurement& meas: worker_measurements)
    {
	if (meas.mrenclave.size() != 0)
	{
	    if (memcmp(meas.mrenclave.data(), (report_body->mr_enclave).m, SGX_HASH_SIZE) != 0)
	    {
		continue;
	    }
	}

	if (meas.mrsigner.size() != 0)
        {
            if (memcmp(meas.mrsigner.data(), (report_body->mr_signer).m, SGX_HASH_SIZE) != 0)
            {
                continue;
            }
        }

	if (meas.isv_prod_id >= 0)
	{
	    uint16_t isv_prod_id = (uint16_t) report_body->isv_prod_id;	
	    if (meas.isv_prod_id != isv_prod_id)
	    {
		continue;
	    }
	}

	if (meas.isv_svn >= 0)
        {
            uint16_t isv_svn = (uint16_t) report_body->isv_svn;
            if (meas.isv_prod_id != isv_svn)
            {
                continue;
            }
        }

	worker.worker_mrenclave = ByteArray((report_body->mr_enclave).m, (report_body->mr_enclave).m + SGX_HASH_SIZE);
	worker.worker_mrsigner = ByteArray((report_body->mr_signer).m, (report_body->mr_signer).m + SGX_HASH_SIZE);
	worker.isv_prod_id = (uint16_t) report_body->isv_prod_id;
	worker.isv_svn = (uint16_t) report_body->isv_svn;

	return true;
    }


    return false;
}


} //namespace cfl
