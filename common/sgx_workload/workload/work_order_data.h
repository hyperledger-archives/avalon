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

/**
 * @file
 * Defines class tcf::WorkOrderData for work order data submitted to
 * workload processors.
 * To use, #include "work_order_data.h"
 */

#pragma once

#include <string>
#include "types.h"

namespace tcf {
	/**
         * Wrapper class for work order data submitted to workload processors.
         */
	class WorkOrderData {
	public:

        WorkOrderData();
        explicit WorkOrderData(int in_index, ByteArray data);
		int index;
		// Initialize here to suppress Klocwork initialization error
		ByteArray decrypted_data = {};
	};
}  // namespace tcf
