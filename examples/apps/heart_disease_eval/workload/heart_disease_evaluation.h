/* Copyright 2018 Intel Corporation
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

#include <string>
#include <vector>

#include "work_order_data.h"
#include "work_order_processor_interface.h"

double model_A(double max, double opt, double data);

double model_B(double max, double opt, double data);

double score_age(double data);

double score_sex(int sex);

double score_cp(int cp_type);

double score_trestbps(double data);

double score_chol(double data);

double score_fbs(double data);

double score_restecg(int type);

double score_thalach(double data);

double score_exang_oldpeak(int type);

double score_slop(int type);

double score_ca(int number);

double score_thaldur(int durationMin);

double score_num(int num);

//std::string executeWorkOrder(std::string decrypted_user_input_str);

class HeartDiseaseEval: public tcf::WorkOrderProcessorInterface {
private:
        std::string executeWorkOrder(std::string decrypted_user_input_str);
        double model_A(double max, double opt, double data);
        double model_B(double max, double opt, double data);
        double score_age(double data);
        double score_sex(int sex);
        double score_cp(int cp_type);
        double score_trestbps(double data);
        double score_chol(double data);
        double score_fbs(double data);
        double score_restecg(int type);
        double score_thalach(double data);
        double score_exang_oldpeak(int type);
        double score_slop(int type);
        double score_ca(int number);
        double score_thaldur(int durationMin);
        double score_num(int num);

public:
        HeartDiseaseEval(void);
        virtual ~HeartDiseaseEval(void);

        void ProcessWorkOrder(
                std::string workload_id,
                const ByteArray& participant_address,
                const ByteArray& enclave_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data);
};
