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


#include <pthread.h>
#include <queue>


namespace tcf {
    namespace enclave_queue {
        class EnclaveQueue {
        public:

            int pop();

            void push(const int& item);

        private:
            std::queue<int> queue_;
            pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
            pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

        };  // class EnclaveQueue


        /*
          Class ReadyEnclave stores index of next available enclave in an object.
          Ensures enclave is placed back in queue if exception is thrown.
        */
        class ReadyEnclave {
        public:

            int enclaveIndex_;
            EnclaveQueue *queue_;

            ReadyEnclave(EnclaveQueue *queue);

            ~ReadyEnclave();

            int getIndex() {
                return enclaveIndex_;
            }

        };  // class ReadyEnclave

    }  /* namespace enclave_queue */

}  /* namespace tcf */



