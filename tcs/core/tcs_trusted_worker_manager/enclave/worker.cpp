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

#include "enclave_t.h"

#include <string>
#include <vector>

#include "sgx_thread.h"
#include "worker.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Worker::Worker(long thread_id) {
    thread_id_ = thread_id;
    current_state_ = WORKLOAD_DONE;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void Worker::InitializeWorkload(void) {
    sgx_thread_mutex_lock(&mutex_);

    if (current_state_ == WORKLOAD_DONE) {
        if (workload_ != NULL) {
            delete workload_;
        }


        WorkloadProcessor workload;

        current_state_ = WORKLOAD_READY;
        sgx_thread_cond_signal(&ready_cond_);
    }

    sgx_thread_mutex_unlock(&mutex_);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void Worker::WaitForCompletion(void) {
    sgx_thread_mutex_lock(&mutex_);

    while (current_state_ != WORKLOAD_DONE) {
        sgx_thread_cond_wait(&done_cond_, &mutex_);
    }

    sgx_thread_mutex_unlock(&mutex_);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WorkloadProcessor* Worker::GetInitializedWorkload(void) {
    sgx_thread_mutex_lock(&mutex_);

    while (current_state_ != WORKLOAD_READY) {
        sgx_thread_cond_wait(&ready_cond_, &mutex_);
    }

    current_state_ = WORKLOAD_BUSY;

    sgx_thread_mutex_unlock(&mutex_);

    return workload_;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
void Worker::MarkWorkloadDone(void) {
    sgx_thread_mutex_lock(&mutex_);
    current_state_ = WORKLOAD_DONE;
    sgx_thread_cond_signal(&done_cond_);
    sgx_thread_mutex_unlock(&mutex_);
}

