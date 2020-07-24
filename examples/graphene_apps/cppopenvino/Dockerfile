# Copyright 2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Build arguments used for various Docker build stages
ARG MODEL_DIR=model
# corresponds to tag "2019_R3"
ARG MODEL_COMMIT=acf297c73db8cb3f68791ae1fad4a7cc4a6039e5
ARG MODEL_NAME=VGG_VOC0712Plus_SSD_300x300_ft_iter_160000

ARG OPENVINO_DIR=openvino
# corresponds to tag "2019_R2"
ARG OPENVINO_COMMIT=ba6e22b1b5ee4cbefcc30e8d9493cddb0bb3dfdf
ARG OPENVINO_BUILD=Release


# Stage 1 - Build base image with necessary packages
FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    pkg-config \
    python3-dev \
    python3-pip \
    git \
    cmake \
    make \
    libusb-1.0-0-dev \
 && apt-get clean \ 
 && python3 -m pip install pyyaml numpy networkx==2.3 test-generator defusedxml protobuf requests

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python


# Stage 2 - git clone openvino
FROM base_image as openvino_clone

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

WORKDIR /home/openvino

RUN git clone https://github.com/opencv/dldt.git $OPENVINO_DIR \
    && cd $OPENVINO_DIR && git checkout $OPENVINO_COMMIT 

RUN cd $OPENVINO_DIR/inference-engine && git submodule init \
    && git submodule update --recursive


# Stage 3 - Build openvino
FROM openvino_clone as openvino_build

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

WORKDIR /home/openvino

RUN cd $OPENVINO_DIR/inference-engine && mkdir -p build \
    && cd build && cmake -DCMAKE_BUILD_TYPE=$OPENVINO_BUILD .. \ 
    && make -j4


# Stage 4 - git clone open model zoo
FROM openvino_build as openmodel_clone

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

WORKDIR /home/openvino

RUN git clone https://github.com/openvinotoolkit/open_model_zoo.git $MODEL_DIR \
    && cd $MODEL_DIR && git checkout $MODEL_COMMIT 

RUN  cd $MODEL_DIR/tools/downloader && python3 ./downloader.py \
     --name ssd300 -o /home/openvino/$MODEL_DIR


# Stage 5 - Build model file
FROM openmodel_clone as build_model

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

WORKDIR /home/openvino

# Convert the model to the OpenVino Intermediate Representation (IR)
RUN  cd $OPENVINO_DIR/model-optimizer && python3 ./mo.py \
    --input_model  /home/openvino/$MODEL_DIR/public/ssd300/models/VGGNet/VOC0712Plus/SSD_300x300_ft/$MODEL_NAME.caffemodel \
    --input_proto /home/openvino/$MODEL_DIR/public/ssd300/models/VGGNet/VOC0712Plus/SSD_300x300_ft/deploy.prototxt \
    --output_dir /home/openvino/$MODEL_DIR


# Stage 6 - Build final image
FROM build_model as final_image

ARG MODEL_DIR
ARG MODEL_COMMIT
ARG MODEL_NAME
ARG OPENVINO_DIR
ARG OPENVINO_COMMIT
ARG OPENVINO_BUILD

WORKDIR /home/openvino

# Install application dependencies - zmq, json libraries.
RUN apt-get install -y -q libzmq3-dev nlohmann-json-dev git

# Clone C++ toml git repo.
RUN mkdir -p toml \
  && cd toml \
  && git clone https://github.com/ToruNiina/toml11 -b v3.5.0 

# Below environment variables will be used by application cmake file
# to find openvino and opencv package and libraries.
ENV InferenceEngine_DIR="/home/openvino/openvino/inference-engine/build/"
ENV OpenCV_DIR="/home/openvino/openvino/inference-engine/temp/opencv_4.1.1_ubuntu18/cmake/"
ENV OPENVINO_LIB="/home/openvino/openvino/inference-engine/bin/intel64/Release/lib/"

COPY ./*.cpp ./
COPY ./*.h ./
COPY ./CMakeLists.txt ./

RUN mkdir -p build \
  && cd build \
  && cmake .. \
  && make

# Docker image optimization.
# Install only required files/binaries/libraries in final stage.
FROM base_image as openvino_bin_image

WORKDIR /home/openvino

COPY --from=final_image /home/openvino/model /home/openvino/model
COPY --from=final_image /home/openvino/openvino/inference-engine/bin/intel64/Release/lib /home/openvino/lib
COPY --from=final_image /home/openvino/openvino/inference-engine/temp/tbb/lib /home/openvino/lib
COPY --from=final_image /home/openvino/openvino/inference-engine/temp/opencv_4.1.1_ubuntu18/lib /home/openvino/lib

FROM openvino_bin_image as final_bin_image

RUN apt-get install -y -q libzmq3-dev nlohmann-json-dev\
    && python3 -m pip install pyzmq toml

COPY ./images /home/openvino/images
COPY ./config.toml /home/openvino/config.toml
COPY ./test/*.py /home/openvino/test/
COPY ./test/test_config.toml /home/openvino/test_config.toml

# Copy openvinowl binary
COPY --from=final_image /home/openvino/build/openvinowl /home/openvino/bin/openvinowl

WORKDIR /home/openvino

ENV PATH=$PATH:./bin:.
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./lib:.

CMD ["openvinowl"]
