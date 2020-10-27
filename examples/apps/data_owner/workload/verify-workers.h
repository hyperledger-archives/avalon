#pragma once

#include "parson.h"
#include "cfl-utils.h"

namespace cfl {


    bool VerifyWorker(const char* enclave_data, const ByteArray& nonce, GrapheneWorker& worker);
    ByteArray CalculateReportData(const std::string& vkey, const std::string& ekey, const ByteArray & nonce);
    bool VerifyReportFields(JSON_Object* verification_report_object);
    bool ExtractQuoteBody(JSON_Object* verification_report_object, 
		          const std::string& vkey, 
			  const std::string& ekey, 
			  const ByteArray& nonce, 
			  GrapheneWorker& worker);
}

