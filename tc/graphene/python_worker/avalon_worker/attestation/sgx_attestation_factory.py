#!/usr/bin/python3

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
import sys
import logging
import graphene_sgx.graphene_sgx_attestation as graphene

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------------------------------------------------------


class SgxAttestationFactory():
    """
    Factory Class to create SGX attestation instance based on enclave type.
    """

# -------------------------------------------------------------------------
    # Class variables

    # Graphene SGX
    GRAPHENE = "graphene-sgx"
    # Only Graphene-SGX is supported by Avalon Python worker.
    # Below are other enclave types which can be supported in future.
    # Anjuna
    ANJUNA = "anjuna"
    # Fortanix
    FORTANIX = "fortanix"
    # SGX-LKL
    LKL = "sgx-lkl"
    # Occlum
    OCCLUM = "occlum"
    # Scone
    SCONE = "scone"

# -------------------------------------------------------------------------

    def create(self, enclave_type):
        """
        Create SGX Attestation instance based on enclave type.

        Parameters :
            enclave_type: SGX enclave type
        Returns :
            SGX Attestation class instance for the corresponding enclave type.
        """
        if enclave_type == SgxAttestationFactory.GRAPHENE:
            return graphene.GrapheneSGXAttestation()
        else:
            logger.error("Unsupported Enclave Type")
            return None

# -------------------------------------------------------------------------
