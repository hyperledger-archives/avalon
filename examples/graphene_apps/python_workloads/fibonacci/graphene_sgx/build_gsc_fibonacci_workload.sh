#! /bin/bash

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

# This is a helper script to build Graphenized docker image for python worker.

# Avalon python worker docker image name.
IMAGE_NAME=avalon-fibonacci-workload-dev
# Graphenized docker image name for python worker.
GSC_IMAGE_NAME=gsc-$IMAGE_NAME

# Check if TCF_HOME is set. If not exit.
if [ -z "$TCF_HOME" ]; then
  echo "TCF_HOME is not set. Please set it to avalon repo top level directory"
  echo "In the current shell: export TCF_HOME=<avalon top level directory>"
  exit
else
  echo "TCF_HOME is set to $TCF_HOME"
fi

# Check if GSC image exists. If so delete it first before building new image.
GSC_IMAGE_EXISTS=`sudo docker image inspect $GSC_IMAGE_NAME  >/dev/null 2>&1 && echo yes || echo no`
if [ "$GSC_IMAGE_EXISTS" = "yes" ]; then
  echo "Remove existing GSC image"
  sudo docker rmi $GSC_IMAGE_NAME --force
fi

# Manifest files
MANIFEST_FILE_DIR="${TCF_HOME}/tc/graphene/python_worker/graphene_sgx/manifest"
MANIFEST_FILES="python.manifest
sh.manifest
gcc.manifest
collect2.manifest
ld.manifest"
# Generate list of manifest files
LIST_MANIFEST_FILES=""
for f in $MANIFEST_FILES
do
  FILE_NAME=${MANIFEST_FILE_DIR}/$f
  if [ ! -f $FILE_NAME ]; then
    echo "ERROR:Manifest file $FILE_NAME doesn't exist"
    exit
  fi
  LIST_MANIFEST_FILES+=${MANIFEST_FILE_DIR}/$f
  LIST_MANIFEST_FILES+=" "
done
echo $LIST_MANIFEST_FILES

# Build image
echo "Build unsigned GSC image"
./gsc build --insecure-args $IMAGE_NAME $LIST_MANIFEST_FILES

# Generate signing key if it doesn't exists
SIGN_KEY_FILE=enclave-key.pem
if [ ! -f "$SIGN_KEY_FILE" ]; then
  openssl genrsa -3 -out $SIGN_KEY_FILE 3072
fi

# Sign image to generate final GSC image
echo "Generate Signed GSC image"
./gsc sign-image $IMAGE_NAME $SIGN_KEY_FILE
