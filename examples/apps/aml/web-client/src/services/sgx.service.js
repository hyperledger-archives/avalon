/* Copyright 2019 Banco Santander S.A.
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

import axios from 'axios';
import config from '../config.js'

export default {

    getWorkerList() {
        return new Promise((resolve, reject) => {
            axios.post(`${config.SERVER_URL}${config.API_PATH}`,

                {
                    jsonrpc: "2.0",
                    method: "WorkerLookUp",
                    id: 1,
                    params: {
                        workerType: 1,
                        workOrderId: null
                    }
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    resolve(response.data.result.ids.map(el => ({ 'Worker_ID_public_EC_key': el })));
                })
                .catch(e => {
                    reject(e);
                })
        })
    },

    getWorkerDetails(workerPK) {
        return new Promise((resolve, reject) => {
            axios.post(`${config.SERVER_URL}${config.API_PATH}`,

                {
                    jsonrpc: "2.0",
                    method: "WorkerRetrieve",
                    id: 2,
                    params: {
                        workerId: workerPK
                    }
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    resolve(response.data);
                })
                .catch(e => {
                    reject(e);
                })
        })
    },

    submitWorkOrder(parsedFile) {
        return new Promise((resolve, reject) => {
            axios.post(`${config.SERVER_URL}${config.API_PATH}`,
            parsedFile,
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            )
            .then(response => {
                resolve(response.data);
            })
            .catch(e => {
                reject(e);
            })
        })
    },

    getWorkerOrderResult(workOrderId) {
        return new Promise((resolve, reject) => {
            axios.post(`${config.SERVER_URL}${config.API_PATH}`,

                {
                    jsonrpc: "2.0",
                    method: "WorkOrderGetResult",
                    id: 11,
                    params: {
                        workOrderId: workOrderId
                    }
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    resolve(response.data);
                })
                .catch(e => {
                    reject(e);
                })
        })
    }
}
