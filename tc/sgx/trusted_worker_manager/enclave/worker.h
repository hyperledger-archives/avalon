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

#pragma once

#include "error.h"
#include "sgx_thread.h"

#include "enclave_utils.h"
#include "work_order_processor_interface.h"
#include "workload_processor.h"

class Worker {

protected:
    enum worker_state {
        WORKLOAD_READY = 0,
        WORKLOAD_BUSY = -1,
        WORKLOAD_DONE = 1
    };

    worker_state current_state_;

    sgx_thread_mutex_t mutex_ = SGX_THREAD_MUTEX_INITIALIZER;
    sgx_thread_cond_t ready_cond_ = SGX_THREAD_COND_INITIALIZER;
    sgx_thread_cond_t done_cond_ = SGX_THREAD_COND_INITIALIZER;

    WorkloadProcessor *workload_ = NULL;
    
public:

    long thread_id_;
    Worker(long thread_id);

    void InitializeWorkload(void);
    void WaitForCompletion(void);

    WorkloadProcessor *GetInitializedWorkload(void);

    void MarkWorkloadDone(void);
};

class InitializedWorkload {

public:
    Worker *worker_ = NULL;

    WorkloadProcessor *workload_ = NULL;

    InitializedWorkload(Worker* worker) {
        worker_ = worker;
        workload_ = worker_->GetInitializedWorkload();
    }

    ~InitializedWorkload(void) {
        worker_->MarkWorkloadDone();
    }
};

