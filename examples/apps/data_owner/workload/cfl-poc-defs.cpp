//
// CFL_POC: cfl-poc-defs.h
// Common definitions for data owner and requster enclaves 
//

#include "cfl-poc-defs.h"


// this common functions reuasable by both Node and Requester enclaves

namespace cfl {

void AddOutput(int index,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    const ByteArray& data)
{
    int out_wo_data_size = out_work_order_data.size();
    // If the out_work_order_data has entry to hold the data
    if (index < out_wo_data_size) {
        tcf::WorkOrderData& out_wo_data = out_work_order_data.at(index);
        out_wo_data.decrypted_data = data;
    }
    else {
        // Create a new entry
        out_work_order_data.emplace_back(index, data);
    }
}

void AddOutput(int index,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    const std::string& str)
{
    ByteArray ba(str.begin(), str.end());
    AddOutput(index, out_work_order_data, ba);
}

void AddOutput(int index,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    int num)
{
    std::string num_str = std::to_string(num);
    AddOutput(index, out_work_order_data, num_str);
}

void AddOutput(int index,
    std::vector<tcf::WorkOrderData>& out_work_order_data,
    const char* ptr)
{
    std::string str = ptr;
    AddOutput(index, out_work_order_data, str);
}


void MergeOutput(ByteArray& output,
                 const std::vector<tcf::WorkOrderData>& out_work_order_data) 
{
    output.resize(0);

    for (size_t i = 0; i < out_work_order_data.size(); i++) 
    {
        if (i > 0)
	{
	    output.emplace_back(' ');
	}

	ByteArray decrypted_data = out_work_order_data.at(i).decrypted_data;
	output.insert(output.end(), decrypted_data.begin(), decrypted_data.end());
    }
}

} //namespace
