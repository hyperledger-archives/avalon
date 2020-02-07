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
#include <cmath>
#include "heart_disease_evaluation_logic.h"

// Calculate risk of having heart disease given input parameters.

HeartDiseaseEvalLogic::HeartDiseaseEvalLogic() {}

HeartDiseaseEvalLogic::~HeartDiseaseEvalLogic() {}

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

// Compute a percentage near optimum (<=opt is 100%, >=max is 0%)
double HeartDiseaseEvalLogic::model_A(double max, double opt, double data) {
    double score = 0.0;
    if (data < opt)
        score = 100;
    else if (data < max)
        score = 100 * (max - data) / (max - opt);
    return score;
}

// Compute a percentage near or above max (<=opt is 0%, >=max is 100%)
double HeartDiseaseEvalLogic::model_B(double max, double opt, double data) {
    double score = 0.0;
    double delta = std::abs(data - opt);
    if ( delta < max - opt)
        score = 100 - 100 * delta / (max - opt);
    return score;
}

// Score several risk factors

double HeartDiseaseEvalLogic::score_age(double data) {
    return model_A(100, 18, data);
}

double HeartDiseaseEvalLogic::score_sex(int sex) {
    // Sex: 0=female, 1=male
    return (sex == 0) ? 100 : 0;
}

double HeartDiseaseEvalLogic::score_cp(int cp_type) {
    // Chest pain type
    double score = 0.0;
    switch (cp_type) {
        case 1: // typical angina
            score = 0.0;
            break;
        case 2: // atypical angina
            score = 12.0;
            break;
        case 3: // non-anginal pain
            score = 35.0;
            break;
        case 4: // asymptomatic
            score = 100.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEvalLogic::score_trestbps(double data) {
    // Resting blood pressure (mm Hg)
    return model_A(218, 108, data);
}

double HeartDiseaseEvalLogic::score_chol(double data) {
    // Serum cholesterol (mg/dl)
    return model_A(309, 126, data);
}

double HeartDiseaseEvalLogic::score_fbs(double data) {
    // Fasting blood sugar (mg/dl)
    return model_A(248, 98, data);
}

double HeartDiseaseEvalLogic::score_restecg(int type) {
    // Resting electrocardiographic results
    double score = 0.0;
    switch (type) {
        case 0: // normal
            score = 100.0;
            break;
        case 1: // ST-T wave abnormality
            score = 9.0;
            break;
        case 2: // hypertrophy
            score = 7.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEvalLogic::score_thalach(double data) {
    // Maximum heart rate achieved
    return model_B(198, 61, data);
}

double HeartDiseaseEvalLogic::score_exang(int type) {
    // Exercise induced angina
    double score = 0.0;
    switch (type) {
        case 0: // no
            score = 100.0;
            break;
        case 1: // yes
            score = 0.0;
            break;
        default:
            score = 100.0;
    }
    return score;
}

double HeartDiseaseEvalLogic::score_oldpeak(double depression) {
    // ST depression induced by exercise relative to rest
    return model_A(100.0, 0.0, depression);
}

double HeartDiseaseEvalLogic::score_slop(int type) {
    // Slope of the peak exercise ST segment
    double score = 0.0;
    switch (type) {
        case 0: // upsloping
            score = 49.0;
            break;
        case 1: // flat
            score = 100.0;
            break;
        case 2: // downsloping
        default:
            score = 63.0;
    }
    return score;
}

double HeartDiseaseEvalLogic::score_ca(int number) {
    // Number of major vessels colored by flouroscopy
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

double HeartDiseaseEvalLogic::score_thaldur(int durationMin) {
    // Thallium stress test
    double score = 0.0;
    // 3=normal, 6=fixed defect, 7=reversible defect
    if ((durationMin >= 3) && (durationMin < 6))
        score = 45.0;
    else if ((durationMin >= 6) && (durationMin < 8))
        score = 79.0;
    else if (durationMin >= 8)
        score = 100.0;
    return score;
}

double HeartDiseaseEvalLogic::score_num(int num) {
    // Diagnosis of heart disease
    double score = 0.0;
    if (num == 0) // <50% diameter narrowing
        score = 100.0;
    else // 1, >50% diameter narrowing
        score = 0.0;
    return score;
}

// Process work order input for heart disease risk factors
std::string HeartDiseaseEvalLogic::executeWorkOrder(
        std::string decrypted_user_input_str) {
    std::string resultString;
    // Variables to accumulate multiple results
    static int totalRisk = 0;
    static int count = 0;

    try {
        std::string dataString;
        std::vector<std::string> inputString =
            split(decrypted_user_input_str, ':');
        if (inputString.size() > 1)
            dataString = inputString[1];

        std::vector<std::string> medData = split(dataString, ' ');
        switch (medData.size()) {
        case 0: // return accumulated calculations
            if (count == 0) // do not divide by 0
                resultString = "No accumulated heart disease history";
            else
                resultString = "Heart disease risk is " +
                    std::to_string(totalRisk/count) + "% for " +
                    std::to_string(count) + " people";
            break;
        case 14: { // return individual calculation
            int risk = 100 -
                int(score_age(std::stoi(medData[0])) * 0.03
                + score_sex(std::stoi(medData[1])) * 0.01
                + score_cp(std::stoi(medData[2])) * 0.21
                + score_trestbps(std::stoi(medData[3])) * 0.05
                + score_chol(std::stoi(medData[4])) * 0.05
                + score_fbs(std::stoi(medData[5])) * 0.04
                + score_restecg(std::stoi(medData[6])) * 0.19
                + score_thalach(std::stoi(medData[7])) * 0.06
                + score_exang(std::stoi(medData[8])) * 0.18
                + score_oldpeak(std::stoi(medData[9])) * 0.05
                + score_slop(std::stoi(medData[10])) * 0.03
                + score_ca(std::stoi(medData[11])) * 0.04
                + score_thaldur(std::stoi(medData[12])) * 0.02
                + score_num(std::stoi(medData[13])) * 0.04);

            // Update accumulation
            totalRisk += risk;
            count++;

            // Format the result
            resultString = "You have a " + std::to_string(risk) +
                "% risk of heart disease";
            break;
            }
        default: // error
            return "Error with missing or incorrect input format";
        }
    } catch (...) {
        resultString = "Caught exception while processing workload data";
    }
    return resultString;
}
