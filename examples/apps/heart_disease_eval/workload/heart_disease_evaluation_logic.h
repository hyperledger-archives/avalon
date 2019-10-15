/* Copyright 2019 Intel Corporation
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

class HeartDiseaseEvalLogic {
private:
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
        double score_exang(int type);
        double score_oldpeak(double depression);
        double score_slop(int type);
        double score_ca(int number);
        double score_thaldur(int durationMin);
        double score_num(int num);

public:
        HeartDiseaseEvalLogic(void);
        ~HeartDiseaseEvalLogic(void);

        std::string executeWorkOrder(std::string decrypted_user_input_str);
};
