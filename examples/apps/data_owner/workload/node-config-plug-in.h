//
// CFL POC: Plug-in.h
// Definitions for the workload registration and entry point
//

#pragma once

#include "workload_processor.h"

#include <algorithm>
#include <string>
#include <vector>
#include "cfl-poc-defs.h"

namespace cfl {

    class NodeConfigPlugin : public WorkloadProcessor {
    public:
	    IMPL_WORKLOAD_PROCESSOR_CLONE(NodeConfigPlugin)

            virtual void ProcessWorkOrder(
                std::string workload_id,
                const ByteArray& requester_id,
                const ByteArray& worker_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data);
    };

}  // namespace cfl


