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

// This demo application predicts the probability of heart disease.

#include <string>
#include <cmath>

#include "heart_disease_evaluation.h"

REGISTER_WORKLOAD_PROCESSOR("heart-disease-eval",HeartDiseaseEval)

HeartDiseaseEval::HeartDiseaseEval() {}

HeartDiseaseEval::~HeartDiseaseEval() {}

template<typename Out>
void split(const std::string &str, char delim, Out result) {
        std::size_t current, previous = 0;

        current = str.find(delim);
        while (current != std::string::npos) {
                std::string item = str.substr(previous, current - previous);
                if (item.compare("") != 0)
                        *(result++) = item; 
                previous = current + 1;
                current = str.find(delim, previous);
        }

        std::string item = str.substr(previous, current - previous);
        if (item.compare("") != 0)
                *(result++) = item;
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, std::back_inserter(elems));
    return elems;
}

double HeartDiseaseEval::model_A(double max, double opt, double data) {
    double score = 0.0;
    if (data < opt)
        score = 100;
    else if (data < max)
        score = 100 * (max - data) / (max - opt);
    return score;
}

double HeartDiseaseEval::model_B(double max, double opt, double data) {
    double score = 0.0;
    double delta = std::abs(data - opt);
    if ( delta < max - opt)
        score = 100 - 100 * delta / (max - opt);
    return score;
}

double HeartDiseaseEval::score_age(double data) {
    return model_A(100, 18, data);
}

double HeartDiseaseEval::score_sex(int sex) {
    return (sex == 0) ? 100 : 0;
}

double HeartDiseaseEval::score_cp(int cp_type) {
    double score = 0.0;
    switch (cp_type) {
        case 1:
            score = 0.0;
            break;
        case 2:
            score = 12.0;
            break;
        case 3:
            score = 35.0;
            break;
        case 4:
            score = 100.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEval::score_trestbps(double data) {
    return model_A(218, 108, data);
}

double HeartDiseaseEval::score_chol(double data) {
    return model_A(309, 126, data);
}

double HeartDiseaseEval::score_fbs(double data) {
    return model_A(248, 98, data);
}

double HeartDiseaseEval::score_restecg(int type) {
    double score = 0.0;
    switch (type) {
        case 0:
            score = 100.0;
            break;
        case 1:
            score = 9.0;
            break;
        case 2:
            score = 7.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEval::score_thalach(double data) {
    return model_B(198, 61, data);

}

double HeartDiseaseEval::score_exang_oldpeak(int type) {
    double score = 0.0;
    switch (type) {
        case 0:
            score = 100.0;
            break;
        case 1:
            score = 0.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEval::score_slop(int type) {
    double score = 0.0;
    switch (type) {
        case 0:
            score = 49.0;
            break;
        case 1:
            score = 100.0;
            break;
        default:
            score = 63.0;
    }
    return score;
}

double HeartDiseaseEval::score_ca(int number) {
    double score = 0.0;
    switch (number) {
        case 0:
            score = 0.0;
            break;
        case 1:
            score = 35.0;
            break;
        case 2:
            score = 70.0;
            break;
        case 3:
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEval::score_thaldur(int durationMin) {
    double score = 0.0;
    if ((durationMin >= 3) && (durationMin < 6))
        score = 45.0;
    else if ((durationMin >= 6) && (durationMin < 8))
        score = 79.0;
    else if (durationMin >= 8)
        score = 100.0;
    return score;
}

double HeartDiseaseEval::score_num(int num) {
    double score = 0.0;
    if (num == 0)
        score = 100.0;
    else
        score = 0.0;
    return score;
}

ByteArray ConvertStringToByteArray(std::string s) {
    ByteArray ba(s.begin(), s.end());
    return ba;
}

std::string HeartDiseaseEval::executeWorkOrder(std::string decrypted_user_input_str) {
    // Variables to accumulate multiple results
    static int totalRisk = 0;
    static int count = 0;

    // Clear accumulation data if input is empty
    if (decrypted_user_input_str.empty()) {
        totalRisk = count = 0;
        return "";
    }

    std::string dataString;
    std::vector<std::string> inputString = split(decrypted_user_input_str, ':');
    if (inputString.size() > 1)
        dataString = inputString[1];

    std::vector<std::string> medData = split(dataString, ' ');
    if (medData.size() != 14)
        return "Error with missing or incorrect input format";

    int risk = 100 -
        int( score_age(std::stoi(medData[0])) * 0.03
        + score_sex(std::stoi(medData[1])) * 0.01
        + score_cp(std::stoi(medData[2])) * 0.21
        + score_trestbps(std::stoi(medData[3])) * 0.05
        + score_chol(std::stoi(medData[4])) * 0.05
        + score_fbs(std::stoi(medData[5])) * 0.04
        + score_restecg(std::stoi(medData[6])) * 0.19
        + score_thalach(std::stoi(medData[7])) * 0.06
        + score_exang_oldpeak(std::stoi(medData[8])) * 0.18
        + score_exang_oldpeak(std::stoi(medData[9])) * 0.05
        + score_slop(std::stoi(medData[10])) * 0.03
        + score_ca(std::stoi(medData[11])) * 0.04
        + score_thaldur(std::stoi(medData[12])) * 0.02
        + score_num(std::stoi(medData[13])) * 0.04 );

    // Update accumulation
    totalRisk += risk;
    count++;

    // Use accumulated data to calculate the result
    std::string resultString = "You have a risk of " + std::to_string(totalRisk/count) + "% to have heart disease.";
    return resultString;
}

void HeartDiseaseEval::ProcessWorkOrder(
        std::string workload_id,
        const ByteArray& requester_id,
        const ByteArray& worker_id,
        const ByteArray& work_order_id,
        const std::vector<tcf::WorkOrderData>& in_work_order_data,
        std::vector<tcf::WorkOrderData>& out_work_order_data) {
    std::string result_str;
    int out_wo_data_size = out_work_order_data.size();

    // Clear state - to reset totalRisk and count
    executeWorkOrder("");
    for (auto wo_data : in_work_order_data) {
        std::string inputData =
              ByteArrayToString(wo_data.decrypted_data);
        try {
            result_str = executeWorkOrder(inputData);
        } catch(...) {
            result_str = "Failed to process workorder data";
        }
    }

    // If the out_work_order_data has entry to hold the data
    if (out_wo_data_size) {
        tcf::WorkOrderData& out_wo_data = out_work_order_data.at(0);
        out_wo_data.decrypted_data =
                    ConvertStringToByteArray(result_str);
    } else {
        // Create a new entry
        out_work_order_data.emplace_back(
                    0, ConvertStringToByteArray(result_str));
    }

}
