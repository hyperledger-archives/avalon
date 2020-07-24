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
#pragma once

#include <inference_engine.hpp>

using namespace InferenceEngine;

class SSDObjectDetection {

private:
	// Model related variables.
	std::string outputName;
	std::string imInfoInputName;
	std::string imageInputName;
	int maxProposalCount;
	int objectSize;
	ExecutableNetwork executable_network;
	CNNNetwork network;
	// Network topology inputs.
    InputsDataMap inputsInfo;
    InputInfo::Ptr inputInfo;

public:
	int load_model(const std::string &modelFile);
    int object_detection(const std::string &imageFileIn, 
    					 const std::string &imageFileOut);

};

