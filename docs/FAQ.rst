..
   Copyright 2020 Intel Corporation

   Licensed under Creative Commons Attribution 4.0 International License.

Hyperledger Avalon FAQ
===================================================

Answers to frequently asked questions for Hyperledger Avalon.
Many questions and answers originated from the
`Avalon mailing list <https://lists.hyperledger.org/g/avalon>`_
and the
`#avalon Rocket.Chat channel <https://chat.hyperledger.org/channel/avalon>`_

Avalon FAQ Sections
-------------------
- `Hyperledger Avalon in General`_
- `Installation and Configuration`_
- `Software Development`_
- `Docker and Containers`_
- `TEEs and Intel® SGX`_

Hyperledger Avalon in General
=============================

What is Hyperledger Avalon?
---------------------------
Hyperledger Avalon enables privacy in blockchain transactions, moving
intensive processing from a main blockchain to improve scalability and latency,
and to support attested Oracles.

What is the Off-Chain Trusted Compute Specification?
----------------------------------------------------
The Off-Chain Trusted Compute Specification (TCS) is defines off-chain
compute transactions that can be computed in private and trusted to be correct.
These transactions may or may not be associated with a blockchain.
Avalon implements the TCS.

The TCS is defined by the Enterprise Ethereum Alliance (EEA) Task Force and
is at
https://entethalliance.github.io/trusted-computing/spec.html

How is Avalon source code licensed?
-----------------------------------
As with all Hyperledger projects, Avalon is Apache 2.0 licensed.
Apache 2.0 is a permissive license that allows reuse of the software,
including commercial use.
For details, see the license at
https://github.com/hyperledger/avalon/blob/master/LICENSE

Hyperledger Avalon documentation is licensed under the
Creative Commons Attribution 4.0 International License.
You may obtain a copy of the license at
http://creativecommons.org/licenses/by/4.0/.

Where are some introductory overviews about Avalon?
---------------------------------------------------
- `Introducing Hyperledger Avalon (Dan Middleton and Eugene Yarmosh, 2019)
  <https://www.hyperledger.org/blog/2019/10/03/introducing-hyperledger-avalon>`_
- `New Confidential Computing Solutions Emerge on the
  Hyperledger Avalon Trusted Compute Framework (Michael Reed, 2019)
  <https://software.intel.com/en-us/articles/new-confidential-computing-solutions-emerge-on-the-hyperledger-avalon-trusted-compute>`_
- `Hyperledger Avalon Proposal (Eugene Yarmosh et al., 2019)
  <https://wiki.hyperledger.org/pages/viewpage.action?pageId=16324764>`_

Do you have a developers forum?
-------------------------------
Yes, we host it biweekly online using
`Zoom <https://zoom.us/>`_ at
https://zoom.us/my/hyperledger.community.backup
(meeting ID 622-333-6701).
For details see:
https://lists.hyperledger.org/g/avalon/topic/68762393
or
https://wiki.hyperledger.org/display/avalon/Hyperledger+Avalon

Where are videos about Hyperledger Avalon?
------------------------------------------
- `Hyperledger Avalon
  (Manoj Gopalakrishnan, 2019, 20 minutes, begins at 55:57)
  <https://www.youtube.com/watch?v=N02vxA6qFPg&feature=youtu.be&t=3357>`_
- `Hyperledger Avalon Developer Forum videos
  <https://wiki.hyperledger.org/display/avalon/Meetings>`_
  including:
  - `Introduction to Hyperledger Avalon
    (Eugene Yarmosh, 2019, 55:54)
    <https://wiki.hyperledger.org/display/avalon/2019-12-03+Avalon+Introduction>`_
  - `Hyperledger Avalon Developer Forum Kick-off
    (Eugene Yarmosh, 2019, 31:56)
    <https://wiki.hyperledger.org/display/avalon/2019-11-19+Kickoff>`_
- `Hyperledger Avalon Heart Disease Demo
  (Dan Anderson, 2019, 10:25)
  <https://youtu.be/6L_UOhi7Rxs>`_
- `iExec, Microsoft and Intel present Trusted Compute Framework [Avalon] at
  Devcon (EEA token & other uses)
  (Sanjay Bakshi and others, 2019, 1:38:18)
  <https://youtu.be/lveTxAQ6rmQ>`_

What is Trusted Compute Framework (TCF)?
----------------------------------------
*TCF* is the former name for Hyperledger Avalon.

How do I add a question and answer to this FAQ?
-----------------------------------------------
File a Pull Request (PR) against this file in the
Avalon source code. See
https://github.com/hyperledger/avalon/blob/master/CONTRIBUTING.md

Installation and Configuration
==============================

How do I install and configure Avalon?
--------------------------------------
- First setup your environment by following the instructions at
  https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md
- Then build and install Avalon by following the instructions at
  https://github.com/hyperledger/avalon/blob/master/BUILD.md

How to I resolve a build error for Avalon?
------------------------------------------
- First thing to do is check the version of your Ubuntu distribution.
  Currently, Avalon supports Ubuntu LTS 18.04 ("bionic").
- Next is check the versions of dependent libraries:
  OpenSSL and Intel SGX SDK and Driver versions are often incorrect.
- Also check the troubleshooting sections at
  https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md
  and
  https://github.com/hyperledger/avalon/blob/master/BUILD.md
  to see if your error is mentioned.
- Often a clean build solves problems, or, better yet,
  cloning a new repository to remove build artifacts.
- You can also post a question on the mailing list or chat channel:
  `mailing list <https://lists.hyperledger.org/g/avalon>`_
  or the
  `chat channel <https://chat.hyperledger.org/channel/avalon>`_


Software Development
====================

How do I build Avalon?
----------------------
- Follow the instructions to setup your build environment at
  https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md
- Then build
  https://github.com/hyperledger/avalon/blob/master/BUILD.md
- Intel SGX is not required to build or use Avalon.

Where are the Avalon libraries?
-------------------------------
Avalon libraries are provided in source form at
https://github.com/hyperledger/avalon/
and must be compiled.
The enclave libraries are in subdirectory ``tc/sgx/`` .
Client libraries are under ``examples/common``
with example client applications under ``examples/apps/``

What's the relationship between workload and worker?
----------------------------------------------------
- *Workload* - Your business logic
- *Worker* - A framework component which distributes work to the workloads

Do you have example applications?
---------------------------------
Yes, at
https://github.com/hyperledger/avalon/tree/master/examples/apps

Do you have programming tutorial?
---------------------------------
Yes, there is a simple Avalon worker application tutorial at
https://github.com/hyperledger/avalon/tree/master/docs/workload-tutorial


Is there a way to get more info about an execution?
---------------------------------------------------
Using ``export TCF_DEBUG_BUILD=1`` might help. See https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md#environment
Also look at the Avalon Listener and Enclave Manager output.
The output goes to the terminal. It can be redirected to a file if needed.

Must I use C++ to write application as a workload?
--------------------------------------------------
For now only C++ is supported for workers.
However, any other language can be added.
There was a PR to add Java, for example.

What TCP ports does Avalon use?
-------------------------------
- TCP 1947: connections to Avalon listener from Avalon clients
- TCP 9090: connections to LMDB listener for KV Storage

What cryptography does Avalon use?
----------------------------------
See
https://github.com/hyperledger/avalon/blob/master/tc/sgx/common/crypto/README.md

I get multiple Error 5 messages after submitting a work order: ``Work order is computing. Please query for WorkOrderGetResult to view the result``
-------------------------------------------------------------------
That's normal operation. Currently only pull model is implemented by Avalon.
The Client is expected to call ``WorkOrderGetResult`` periodically to poll
the work order result.


Docker and Containers
=====================

What is the purpose of using Docker, and what does it have to do with Intel SGX? I mean, are Intel SGX enclaves running in containers?
--------------------------------------------------------------------------------------------------------------------------------------
Docker is used only as a convenience. It has nothing to do with the Avalon
security model or Intel SGX enclaves. Docker makes it easier to
build and setup Avalon, but you can also build without Docker
(although it requires several more steps).


TEEs and Intel® SGX
===================

What is a Trusted Execution Environment?
----------------------------------------
A Trusted Execution Environment (TEE) is a secure area of a processor.
It ensures code and data is kept secure from the outside environment
and maintains integrity of input and output with authentication.

A TEE can be thought of as a "reverse sandbox". A traditional sandbox
restricts the software from accessing system or external resources on a
machine (such as a Java VM). A TEE "reverse sandbox" or enclave keeps the
system--other applications and even the OS kernel--from
accessing data inside the enclave.
Intel SGX is a hardware implementation of a TEE and is supported by Avalon.

Is Intel SGX required to use Avalon?
------------------------------------
No. You can use the Intel SGX simulator to simulate a TEE.
In the future we plan to add other trusted workers such as
other hardware TEEs, MPC (multi-party compute), and
ZK (zero-knowledge proofs).

What is the working principle of Intel SGX TEE Workers?
-------------------------------------------------------
At high level you design an application so the core business part resides in
the enclave, ensuring that even if your untrusted part is compromised the
trusted part cannot be.

Intel SGX guarantees code and data is kept private and that the results are
correct with confidentiality and integrity mechanisms.

The PDF link at this webpage gives a good technical overview of Intel SGX enclaves:
https://software.intel.com/en-us/blogs/2016/06/06/overview-of-intel-software-guard-extension-enclave


How can I create a TEE with Intel SGX using Avalon?
----------------------------------------------------------------------------------
Start with the examples and tutorial at https://github.com/hyperledger/avalon/tree/master/docs#tutorial
The technical details of Intel SGX enclaves are encapsulated in the Avalon libraries and Avalon Enclave Manager.
If you want to learn about low-level details, I would look at the Intel SGX SDK and example programs.


I get the message ``intel_sgx: SGX is not enabled`` in ``/var/log/syslog``
--------------------------------------------------------------------------
Intel SGX needs to be enabled in BIOS.

Is there a maximum size of input data when using Intel SGX?
-----------------------------------------------------------
Avalon doesn’t expect application-specific code to use SGX sealed data.
Avalon uses sealed data internally for storing private enclave signing and
encryption keys.
As result application specific data size is not dependent on the sealed data
storage.
It is indirectly limited by the maximum Enclave Page Cache (EPC) size
(enclave includes both data and code).
The maximum EPC size is limited to 128 Mbytes on Intel Xeon E3 and
256 Mbytes on Intel Xeon E Mehlow-R.
The EPC can be bigger but it results in swapping in and out of the enclave,
which greatly slows things down.

Is there a SDK for work order submissions?
------------------------------------------
We don’t have a client SDK for Avalon yet which can be used by Avalon clients
to submit work order requests to Avalon. So there is no formal documentation
available. The Client SDK for Avalon is work in progress.
The Generic client uses some utility functions to create and submit work order.
Documentation is currently limited to code comments.

When starting Avalon with Intel SGX why do I get an error SGX_ERROR_BUSY from the Avalon Listener?
--------------------------------------------------------------------------------------------------
If you are behind a corporate proxy, make sure you have ``proxy type`` and
``aesm proxy`` lines set in ``/etc/aesmd.conf`` .
This file may be overwritten if you reinstall Intel SGX SDK.


© Copyright 2020, Intel Corporation.
