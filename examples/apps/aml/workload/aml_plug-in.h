#include <string>
#include <vector>
#include <memory>

#include "workload_processor.h"
#include "aml_logic.h"

class AmlResult: public WorkloadProcessor {

public:
    AmlResult(void);
    virtual ~AmlResult(void);

    IMPL_WORKLOAD_PROCESSOR_CLONE(AmlResult)

    void ProcessWorkOrder(
                std::string workload_id,
                const ByteArray& requester_id,
                const ByteArray& worker_id,
                const ByteArray& work_order_id,
                const std::vector<tcf::WorkOrderData>& in_work_order_data,
                std::vector<tcf::WorkOrderData>& out_work_order_data);


private:
    AmlResultLogic* aml_result_logic = new AmlResultLogic();
};