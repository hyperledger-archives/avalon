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
#include <iostream>
#include "zmq_listener.h"

/**
*  ZmqListener constructor.
*
*  @param zmq_url ZMQ URL.
*  @param process_wo work order processor object.
*/
ZmqListener::ZmqListener(const std::string zmq_url, ProcessWorkOrder process_wo)
        :zmq_url(zmq_url),process_wo(process_wo) {  
}


/**
*  Start listening for requests at ZMQ endpoint.
*/
void ZmqListener::start_zmq_listener() {    
    zmq::context_t context;
    zmq::socket_t socket(context, ZMQ_REP);
    socket.bind(this->zmq_url.c_str());

    while(1) {
         std::cout<< "Waiting for request" << std::endl;
         std::string message = s_recv(socket);
         if(message.empty()) {
            std::cout<< "Received empty message" << std::endl; 
            continue;
         }
         std::string result = process_wo.process_work_order(message);
         std::cout << result << std::endl;
         // Send result.
         s_send(socket, result);
         std::cout<< "Sent response" << std::endl;
    }
}

/**
*  Receive data.
*
*  @param socket ZMQ socket.
*  @return data received as string. empty string in case of error.
*/
std::string ZmqListener::s_recv(zmq::socket_t &socket) {
    zmq::message_t message;
    bool ret = socket.recv(&message);
    if(ret) {
        return std::string(static_cast<char*>(message.data()),
                           message.size());
    } else {
        return "";
    }
}


/**
*  Send data.
*
*  @param socket ZMQ socket.
*  @param data to send as string.
*  @return boolean.
*/
bool ZmqListener::s_send(zmq::socket_t &socket, 
                         const std::string &string) {
    zmq::message_t message(string.size());
    memcpy(message.data(), string.data(), string.size());
    bool ret = socket.send(message);
    return ret;
}
