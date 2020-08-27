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
- `Videos`_
- `Glossary`_


Hyperledger Avalon in General
=============================

What is Hyperledger Avalon?
---------------------------
Hyperledger Avalon enables privacy in blockchain transactions, moving
intensive processing from a main blockchain to improve scalability and latency,
and to support attested Oracles.

What is the Off-Chain Trusted Compute Specification?
----------------------------------------------------
The Off-Chain Trusted Compute Specification (TCS) defines off-chain
compute transactions that can be computed in private and trusted to be correct.
These transactions may or may not be associated with a blockchain.
Avalon implements the TCS.

The TCS is defined by the Enterprise Ethereum Alliance (EEA) Task Force and
is at
https://entethalliance.github.io/trusted-computing/spec.html

What is the difference between Proxy Mode and Direct Mode?
----------------------------------------------------------
Proxy Mode is where the requester (client) executes a smart contract
(or chaincode or similar) on the blockchain.
The smart contract event invokes Avalon and Avalon executes an
Avalon workload processor through the Blockchain Connector
interface for that blockchain platform (Ethereum, Fabric, etc.).
Direct mode is where the requester (client) operates directly with
Avalon workload processors (via the HTTP JRPC listener), without a blockchain.

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

What is Trusted Compute Framework (TCF)?
----------------------------------------
*TCF* is the former name for Hyperledger Avalon.

How do I add a question and answer to this FAQ?
-----------------------------------------------
File a Pull Request (PR) against this file in the
Avalon source code. See
https://github.com/hyperledger/avalon/blob/master/CONTRIBUTING.md

How do I raise a defect or a new feature request to the Hyperledger Avalon community?
-------------------------------------------------------------------------------------
You can log any new feature request OR issues/defects you find with the
Avalon code here:
https://github.com/hyperledger/avalon/issues

How many nodes does Avalon support?
-----------------------------------
One, specifically the Avalon blockchain connector that connects to
a blockchain node. In the future Avalon will support processing
multiple work orders in parallel, but there will still be one connector.
No other Avalon component connects to the blockchain.

Another Avalon instance unrelated to any other Avalon instance may connect
independently to the blockchain.

What synchronization modes does Avalon Support?
-----------------------------------------------
The Off-Chain Trusted Compute Spec has three modes (asynchronous,
notify, and synchronous). Avalon currently supports async mode.
Synchronous mode using ZMQ is available for Singleton Mode workers. 

Is the LMBD database available for application use?
---------------------------------------------------
No, that is not the intention. LMDB is dedicated for internal use by Avalon.
Application data can be stored in a separate database or in files.
The only potential external use that should be made of LMDB is by an
Avalon hosting service for its monitoring and administration tools.

Is there a mechanism to auto-trim the LMDB database?
----------------------------------------------------
Avalon is supposed to auto-trim LMDB after exceeding a maximum threshold
by removing old entries. It may not be fuly implemented yet,
but that is the plan. There is also an explicit API to delete a specific
workorder, so the orchestrator app can explicitly remove completed workorders.
This is especially useful to remove large, obsolete responses so as to not
exhaust the database. This API mitigates the LMDB size but is not intended as
a replacement for auto-clean up.

In the future, a clean up tool may be added.

Does Avalon support a Library OS (LibOS)?
-----------------------------------------
Avalon does not support a LibOS now, but support is planned in the future,
initially with Graphene.

Does the Avalon Enclave Manager support multiple workers?
---------------------------------------------------------
Currently Avalon is hard-coded to suport one Enclave worker.
Support for multiple workers running in parallel is planned in the future.

How can Avalon workers coordinate in Direct Mode (without a blockchain)?
------------------------------------------------------------------------
In Proxy Mode, Avalon workers can coordinate with blockchain entries.
In Direct Mode, one possible solution is to write a
"coordinator" or "governor" worker that acts as a trusted server and stores
any global registry information (such as data access rights and dataset keys)
required by all the enclave workers.
In essence this mimics blockchain functionality through some sort of
distributed database or ledger.


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

How do I fix this error installing Avalon on Azure ACC with Intel SGX: "/dev/isgx": no such file or directory
--------------------------------------------------------------------------------------------------------------------------------------
Azure Confidential Computing (ACC) installs the ``/dev/sgx`` driver
on their cloud instances with Intel SGX.
Avalon uses ``/dev/isgx`` instead.
So if you use Avalon with Intel SGX hardware mode enabled
on ACC without ``/dev/isgx`` installed you get this error:

   .. code:: none

       ERROR: for avalon-sgx-enclave-manager  Cannot start service
       avalon-sgx-enclave-manager: error gathering device information while
       adding custom device "/dev/isgx": no such file or directory

The fix is to remove ``/dev/sgx`` then install ``/dev/isgx``
For instructions on how to do tis, see "Intel SGX in Hardware Mode" at
https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md#sgx

How can I prevent a worker from using old keys when I restart a KME or a Singleton worker?
------------------------------------------------------------------------------------------
By default, workers use the same signing and encryption key pairs (asymmetric keys) across
restarts to ensure validity of historical work order requests/responses. This is also done
to ensure a smooth functioning in case of abrupt failures of the worker. Sealed data from
respective worker enclaves are used to recover keys across restarts.
However, this default behavior can be overriden if fresh pairs of aforementioned keys are
desired. For this, it has to be ensured that the sealed data created during previous
startup of the enclave manager (KME or Singleton) is cleaned up before starting again.
This has been provisioned in the docker mode already. Prepend ``CLEAN_SEALED_DATA=1`` to
the docker-compose command. For example -

   .. code:: none

       CLEAN_SEALED_DATA=1 docker-compose up -d

You could also update the value of ``CLEAN_SEALED_DATA`` to ``1`` in the ``.env`` file at project root directory.


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
Using ``export TCF_DEBUG_BUILD=1`` might help. See
https://github.com/hyperledger/avalon/blob/master/PREREQUISITES.md#environment
Also look at the Avalon Listener and Enclave Manager output.
The output goes to the terminal. It can be redirected to a file if needed.

Must I use C++ to write application as a workload?
--------------------------------------------------
For now only C++ is supported for workers.
However, any other language can be added.
There was a PR to add Java, for example.

What TCP ports does Avalon use?
-------------------------------
- TCP 1947: connections to Avalon listener from Avalon clients.
  The URL is ``http://localhost:1947/`` or, for Docker,
  ``http://avalon-listener:1947/``
- TCP 9090: connections to LMDB listener for KV Storage.
  The URL is ``http://localhost:9090/`` or, for Docker,
  ``http://avalon-lmdb:9090/``
- TCP 5555: ZMQ connections to Avalon Enclave Manager from Avalon Listener.
  This is used by Avalon singleton enclave workers using Synchronous Mode.
  The URL is ``tcp://localhost:5555`` or, for Docker,
  ``tcp://avalon-enclave-manager:5555``
- TCP 7777: ZMQ socket port used by Avalon Graphene Enclave Manager
  to communicate with Graphene Python Worker.
  The URL is ``tcp://localhost:7777`` or, for Docker,
  ``tcp://graphene-python-worker:7777``
- TCP 1948: connections to Avalon Key Management Enclave (KME).
  Used only for Worker Pool Mode (not Singleton Mode).
  The URL is ``tcp://localhost:1948`` or, for Docker,
  ``tcp://avalon-kme:1948``

What cryptography does Avalon use?
----------------------------------
See
https://github.com/hyperledger/avalon/blob/master/tc/sgx/common/crypto/README.md

I get multiple Error 5 messages after submitting a work order: ``Work order is computing. Please query for WorkOrderGetResult to view the result``
-------------------------------------------------------------------
That's normal operation. Currently only pull model is implemented by Avalon.
The client is expected to call ``WorkOrderGetResult`` periodically to poll
the work order result.

Where are error codes defined?
------------------------------
See file
https://github.com/hyperledger/avalon/blob/master/common/python/error_code/error_status.py
For example, workorder error 5 is ``PENDING``.

How is the JRPC Request ID in work orders used?
-----------------------------------------------
The ``jrpc_req_id`` is used to verify the context of a response received after
posting a JRPC request.
We recommend using a UUID for the request ID.
Currently it is not being verified in Avalon's SDK as the communication is over
HTTP and only a single call is included in each call.
When there is significant traffic, multi-call JRPC requests might be possible
in a single HTTP request. This field would play a role there to map requests
to responses. A shift from HTTP (synchronous request-response) would also
require proper handling of this field.

What does this error mean: ``avalon_sdk.http_client.http_jrpc_client] operation failed: [Errno 99] Cannot assign requested address``?
-------------------------------------------------------------------------------------------------------------------------------------
The requester (client) could not communicate with the Avalon Listener.
This could be caused by Avalon Listener not running or by not specifying the
URI of the Avalon Listener. The default URI for the Avalon Listener is
``http://localhost:1947`` .
If using Docker, specify the URI as the name of the Docker container running
the Avalon Listener:  ``http://avalon-listener:1947`` on the
command line (the option is usually ``--uri`` or ``--service-uri``).

How do I fix ``RuntimeError`` when I make changes to trusted code in enclave managers (KME or Singleton) and try to run?
------------------------------------------------------------------------------------------------------------------------
An error stack similar to the one below can be seen if changes are made to the trusted
code and the enclave manager (KME or Singleton) is restarted.

   .. code:: none

       [02:28:05 ERROR   avalon_enclave_manager.base_enclave_manager] failed to initialize/signup enclave;
       Traceback (most recent call last):
       ...
       RuntimeError

Note that this is only the beginning and end of the error stack. This happens because
some sealed data from respective enclave is used across enclave lifetimes now. The
change in the enclave itself across 2 lifetimes, with the second enclave trying to use
the sealed data from the previous run causes this. The solution is to remove the sealed
data before starting again. Refer to the steps mentioned in ``prevent a worker from
using old keys`` in `Installation and Configuration`_ to achieve cleanup.


Docker and Containers
=====================

What is the purpose of using Docker, and what does it have to do with Intel SGX? I mean, are Intel SGX enclaves running in containers?
--------------------------------------------------------------------------------------------------------------------------------------
Docker is used only as a convenience. It has nothing to do with the Avalon
security model or Intel SGX enclaves. Docker makes it easier to
build and setup Avalon, but you can also build without Docker
(although it requires several more steps).

How do I fix this docker-compose error: ``Invalid interpolation format for "build" option``
-------------------------------------------------------------------------------------------
Your docker-compose is too old. Version 1.17.1 works OK.

How do I open a TCP port in Docker?
-----------------------------------
With the ``ports:`` line. For example, if you want to open TCP port 1947, used by the
Avalon Listener, to the outside world (outside the host and Docker containers), add these
two lines in your ``docker-compose.yaml`` file (or similarly named file)

   .. code:: none

       ports:
        - "1947:1947"

This allows you to connect to TCP port 1947 from the host or external to the host.
Beware that this may allow access to port 1947 from the outside world (Internet)
if your firewall rules allow it. You can also map the port to another port on the host.
For example, ``- "80:1947"`` maps Docker port 1947 to host port 80 (http).

There is a similar line (``expose:``) that opens up ports between Docker containers on the
internal Docker container network. This should already be present:

   .. code:: none

       expose:
        - 1947

Why are some Docker Compose .yaml files in $TCF_HOME and others in $TCF_HOME/docker/compose?
--------------------------------------------------------------------------------------------
The usual convention is to have a default ``docker-compose.yaml`` file
in the base source directory so that a newbie can just run the command
``docker-compose up`` and a bare minimal setup should be running.
The other flavors of .yaml files, be it for proxy or worker pool,
have been moved from $TCF_HOME to ward off confusion and cluttering
in the base source directory.

What is the equivalent of "make clean" using Docker build?
----------------------------------------------------------
The closest to that is running ``git clean`` to remove all generated files.


Videos
========

- Introduction
  - `Hyperledger Avalon [Introduction] (Eugene Yarmosh, 2020)
    <https://youtu.be/I16EhP23HTg>`_
    (from Hyperledger Denver Meetup) (1:00:44)
  - `Introduction to Hyperledger Avalon (Manoj Gopalakrishnan, 2019)
    <https://youtu.be/YRXfzHzJVaU>`_
    (from Hyperledger India Meetup) (20:24)
  - `Introduction and Architecture (Eugene Yarmosh, 2020)
    <https://www.youtube.com/watch?v=ex5k5QPSXdU>`_
    (from Hyperledger Global Forum) (19:19)
  - `Hyperledger Avalon Introduction (Eugene Yarmosh, 2019)
    <https://youtu.be/KCa0Z2-Yins>`_
    (from Avalon Developer Forum) (49:26)

- *Hyperledger Avalon Hands-on Experience* at
  Hyperledger Global Forum 2020

  - `Entire presentation (parts 1-5)
    <https://youtu.be/EdYJ-8eTqNc>`_ (1:30:56)
  - Or view presentations split into five parts by speaker:
  - `Part 1: Introduction and Architecture (Eugene Yarmosh)
    <https://www.youtube.com/watch?v=ex5k5QPSXdU>`_ (19:19)
  - `Part 2: Cold Chain Supply Chain Case Study (Joshua Satten)
    <https://youtu.be/hPBRtUhO_w0>`_ (21:31)
  - `Part 3: Avalon Setup and Development Options (Dan Anderson)
    <https://youtu.be/DeKixYXddCE>`_ (9:24)
  - `Part 4: Hyperledger Fabric Development (Tong Li)
    <https://youtu.be/sA-J-4e--bE>`_ (27:45)
  - `Part 5: Hyperledger Besu Development (Jim Zhang)
    <https://youtu.be/WzI6XkJFtF8>`_ (12:50)
  - Part 6: Tutorial (Dan Anderson and Manjunath A C).
    Not recorded; instead see
    `tutorial instructions
    <https://github.com/hyperledger/avalon/tree/master/docs/workload-tutorial>`_
    and
    `tutorial video <https://youtu.be/yKDFJH9J3IU>`_
  - `Presentation description and speaker biographies
    <https://hgf20.sched.com/event/XogI/hands-on-experience-with-avalon-on-how-to-bridge-on-chain-and-off-chain-worlds-yevgeniy-yarmosh-dan-anderson-intel>`_
  - `PDF slideset for these presentations
    <https://static.sched.com/hosted_files/hgf20/e3/HLGF-AvalonWorkshop-T.pdf>`_

- `Hyperledger Avalon Installation Part 1: with Docker Containers
  (Dan Anderson, 2020) <https://youtu.be/uC4mAXrwgoc>`_ (19:22)
- `Hyperledger Avalon Installation Part 2: Standalone build (without Docker)
  (Dan Anderson, 2020) <https://youtu.be/XuSbKh0LOCg>`_ (17:06)
- `Hyperledger Avalon Application Development Tutorial
  (Dan Anderson, 2020) <https://youtu.be/yKDFJH9J3IU>`_ (39:56)

- `Hyperledger Avalon Developer Forum videos
  <https://wiki.hyperledger.org/display/avalon/Meetings>`_

  - `Hyperledger Avalon Developer Forum Kick-off
    (Eugene Yarmosh, 2019)
    <https://wiki.hyperledger.org/display/avalon/2019-11-19+Kickoff>`_ (31:56)

- `Hyperledger Avalon Heart Disease Demo


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

Intel SGX is a set of instructions that increases the security of application
code and data, giving them more protection from disclosure or modification.
Developers can partition sensitive information into Intel SGX enclaves,
which are areas of execution in memory with more security protection.

The PDF link at this webpage gives a good technical overview of Intel SGX
enclaves:
https://software.intel.com/en-us/blogs/2016/06/06/overview-of-intel-software-guard-extension-enclave

How can I create a TEE with Intel SGX using Avalon?
---------------------------------------------------
Start with the examples and tutorial at https://github.com/hyperledger/avalon/tree/master/docs#tutorial
The technical details of Intel SGX enclaves are encapsulated in the
Avalon libraries and Avalon Enclave Manager.
If you want to learn about low-level details, I would look at the
Intel SGX SDK and example programs.

I get the message ``intel_sgx: SGX is not enabled`` in ``/var/log/syslog``
--------------------------------------------------------------------------
Intel SGX needs to be enabled in BIOS.

Is there a maximum size of input data when using Intel SGX?
-----------------------------------------------------------
Avalon does not expect application-specific code to use Intel SGX sealed data.
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
We do not have a client SDK for Avalon yet which can be used by Avalon clients
to submit work order requests to Avalon. So there is no formal documentation
available. The Client SDK for Avalon is work in progress.
The Generic client uses some utility functions to create and submit work order.
Documentation is currently limited to code comments.

When starting Avalon with Intel SGX why do I get an error SGX_ERROR_BUSY from the Avalon Listener?
--------------------------------------------------------------------------------------------------
If you are behind a corporate proxy, make sure you have ``proxy type`` and
``aesm proxy`` lines set in ``/etc/aesmd.conf`` .
This file may be overwritten if you reinstall Intel SGX SDK.

How do I know I am in Intel SGX Hardware Mode?
----------------------------------------------
If you set ``SGX_MODE=HW`` in your environment and setup Intel SGX correctly,
Avalon will startup in Intel SGX Hardware Mode.
You know you are in Intel SGX Hardware Mode (SGX_MODE=HW) when you see messages
similar to this in the Avalon Enclave Manager output at startup:

   .. code:: none

       INFO avalon_enclave_manager.base_enclave_info] Running in Intel SGX HW mode


Videos
========

- Introduction

  - `Introduction to Hyperledger Avalon (Manoj Gopalakrishnan, 2019)
    <https://youtu.be/YRXfzHzJVaU>`_
    (from Hyperledger India Meetup) (20:24)
  - `Introduction and Architecture (Eugene Yarmosh, 2020)
    <https://www.youtube.com/watch?v=ex5k5QPSXdU>`_
    (from Hyperledger Global Forum) (19:19)
  - `Hyperledger Avalon Introduction (Eugene Yarmosh, 2019)
    <https://youtu.be/KCa0Z2-Yins>`_
    (from Avalon Developer Forum) (49:26)

- *Hyperledger Avalon Hands-on Experience* at
  Hyperledger Global Forum 2020

  - `Entire presentation (parts 1-5)
    <https://youtu.be/EdYJ-8eTqNc>`_ (1:30:56)
  - Or view presentations split into five parts by speaker:
  - `Part 1: Introduction and Architecture (Eugene Yarmosh)
    <https://www.youtube.com/watch?v=ex5k5QPSXdU>`_ (19:19)
  - `Part 2: Cold Chain Supply Chain Case Study (Joshua Satten)
    <https://youtu.be/hPBRtUhO_w0>`_ (21:31)
  - `Part 3: Avalon Setup and Development Options (Dan Anderson)
    <https://youtu.be/DeKixYXddCE>`_ (9:24)
  - `Part 4: Hyperledger Fabric Development (Tong Li)
    <https://youtu.be/sA-J-4e--bE>`_ (27:45)
  - `Part 5: Hyperledger Besu Development (Jim Zhang)
    <https://youtu.be/WzI6XkJFtF8>`_ (12:50)
  - Part 6: Tutorial (Dan Anderson and Manjunath A C).
    Not recorded; instead see
    `tutorial instructions
    <https://github.com/hyperledger/avalon/tree/master/docs/workload-tutorial>`_
    and
    `tutorial video <https://youtu.be/yKDFJH9J3IU>`_
  - `Presentation description and speaker biographies
    <https://hgf20.sched.com/event/XogI/hands-on-experience-with-avalon-on-how-to-bridge-on-chain-and-off-chain-worlds-yevgeniy-yarmosh-dan-anderson-intel>`_
  - `PDF slideset for these presentations
    <https://static.sched.com/hosted_files/hgf20/e3/HLGF-AvalonWorkshop-T.pdf>`_

- `Hyperledger Avalon Installation Part 1: with Docker Containers
  (Dan Anderson, 2020) <https://youtu.be/uC4mAXrwgoc>`_ (19:22)
- `Hyperledger Avalon Installation Part 2: Standalone build (without Docker)
  (Dan Anderson, 2020) <https://youtu.be/XuSbKh0LOCg>`_ (17:06)
- `Hyperledger Avalon Application Development Tutorial
  (Dan Anderson, 2020) <https://youtu.be/yKDFJH9J3IU>`_ (39:56)

- `Hyperledger Avalon Developer Forum videos
  <https://wiki.hyperledger.org/display/avalon/Meetings>`_

  - `Hyperledger Avalon Developer Forum Kick-off
    (Eugene Yarmosh, 2019)
    <https://wiki.hyperledger.org/display/avalon/2019-11-19+Kickoff>`_ (31:56)

- `Hyperledger Avalon Heart Disease Demo
  (Dan Anderson, 2019)
  <https://youtu.be/6L_UOhi7Rxs>`_ (10:25)
- `iExec, Microsoft and Intel present Trusted Compute Framework [Avalon] at
  Devcon (EEA token & other uses)
  (Sanjay Bakshi and others, 2019)
  <https://youtu.be/lveTxAQ6rmQ>`_  (1:38:18)


Glossary
========

AES-GCM 256
    Avalon's authenticated encryption algorithm, with a 96b IV
    and 128b tag. Encrypts data within a work order request or response.
    Also used to encrypt a request digest and custom data encryption keys

Application type ID
    Identifier for a type of Avalon application. An Avalon worker supports
    one or more application types

Attestation
    Proof that something (such as code or data) was checked for validity
    (such as with signature validation)

Attested oracle
    A device that uses Trusted Compute to attest some data
    (e.g. environmental characteristics, financial values, inventory levels)

Base64
    base 64 numbers encoded with A-Z, a-z, 0-9, +, and /. Encodes
    binary data to be printable ASCII characters. Sometimes appended with
    one or two "=" padding characters representing unused bits. First used
    with MIME encoding to encode binary attachments in email

Besu
    Hyperledger Besu is an Ethereum client for public and private
    permissioned blockchains designed to be enterprise-friendly

Blockchain
    A single-link list of blocks used to record transactions. The
    blockchain is immutable, distributed, and cryptographically-secured

Burrow
    EVM compatible Ethereum smart contract platform

Chain code (CC)
    Signed, versioned, addressable programs that execute
    on a Hyperledger Fabric blockchain using the Fabric ledger as data

Client
    For Ethereum, it is any blockchain node. This is not the traditional
    meaning as used in client-server architecture.
    To avoid ambiguity, an Avalon client is properly referred to as a
    requester

Confidential computing
    Protection of data in use by performing computation within
    hardware-based trusted execution environments (TEEs)

DCAP
    Intel SGX Data Center Attestation Primitives. Allows an enterprise
    to provide their own attestation services for Intel SGX TEEs

Dapp (or ÐApp)
    Ethereum distributed application. Uses a smart contract for the back end
    and usually uses a web browser to execute the front end

DID
    Ethereum decentralized ID that is globally unique within a blockchain

DLT
    Distributed Ledger Technology; Blockchain is a DLT

Direct model
    Avalon work order execution model in which a requester application
    directly invokes a JSON RPC network API for work order execution in
    a Worker

Docker
    A light-weight OS-level VM technology which isolates processes into
    separate "containers"

ECDSA-SECP256K1 256
    Avalon's digital signing algorithm  Also used by
    Bitcoin and other blockchain platforms. Signs work order response
    digest and worker's encryption RSA-OAEP public key

Ethereum Enterprise Alliance (EEA)
    A consortium that seeks to use
    Ethereum software on a private enterprise blockchain instead of the
    Ethereum Mainnet

EEA Spec
    Off-Chain Trusted Compute Specification defined by EEA. Avalon
    is an implementation of this EEA specification

Enclave
    Instantiation of Trusted Compute within a hardware based
    TEE. Certain hardware based TEEs, including Intel SGX, allow multiple
    instances of Enclaves executing concurrently. For simplification, in
    this specification the terms TEE and Enclave are used interchangeably

Ether (ETH)
    Digital cryptocurrency used on the Ethereum network

Ethereum Virtual Machine (EVM)
    A virtual machine executes Ethereum smart contracts
    that have been compiled into EVM bytecode

Fabric
    Hyperledger Fabric. An enterprise blockchain platform technology
    contributed by IBM

Gas
    Ethereum cryptocurrency used to pay for an Ethereum transaction
    or smart contract execution

Ganache
    A personal blockchain software for Ethereum development

Graphene
    A Library OS (or "LibOS") that provides an Operating System
    environment in a userspace library to execute an application.
    It is used to execute code unmodified in a TEE such as Intel SGX.

Hyperledger
    An open source collaborative effort created to advance
    enterprise blockchain technologies. It is hosted by
    The Linux Foundation

ID
    Identifier

JSON RPC (JRPC)
    Remote procedure call interface that uses the HTTP
    protocol to send JSON-formatted strings. Avalon uses TCP port 1947 for
    this JRPC

JRPC error codes
    JSON RPC error code return values are:
    0 is success, 1 is unknown error, 2 is invalid parameter
    format or value, 3 is access denied, 4 is invalid signature,
    5 is no more lookup results remaining,
    6 is unsupported mode (synchronous, asynchronous, poll,
    or notification).
    Error codes -32768 to -3200 are reserved for pre-defined
    errors from the JSON RPC specification

K8S
    Kubernetes container platform

KECCAK-256
    One of Avalon's digest algorithms. Used for work order
    requests and responses or Ethereum raw transaction packet bytes. Bitcoin
    and other blockchains used an early form of Keccak, "submitted version
    3", before Keccak was standardized to SHA-3 (FIPS-202) and Keccak has
    minor variations from SHA-3

KME
    Key Management Enclave Avalon worker.
    KME is a part of the worker pool responsible for the key management.
    It has access to the worker's private keys and controls work order
    execution by the WPE. Compare to Singleton and WPE

KV
    simple key-value lookup database

Last lookup tag
    A tag returned by a function returning partial results
    (e.g., work orders or workers). If it is returned, it means that there
    are more matching results that can be retrieved by passing this tag as
    an input parameter to a matching function with "_next" appended to the
    function name

Library OS (LibOS)
    A LibOS encapsulates the services of an operating system into libraries.
    This may be done to have a single address space executable or to
    minimize the Trusted Computing Base (TCB). For Avalon a LibOS allows
    Avalon workers to execute in a TEE enclave with traditional operating
    system and library calls. It also allows workers to be implemented
    in interpretive languages such as Python.
   

LMDB
    Lightning Memory-mapped Database, which is implemented with
    sparse random-access files

Multi-party compute (mpc)
    secure computation that uses cryptography
    to compute a result using input from multiple parties, yet the input is
    kept private from these parties

Nonce
    A unique number that is guaranteed to be unique and never
    repeat. Usually generated from a long random number generator or a
    non-repeating hardware sequence number generator

Off-chain
    Information stored externally to the blockchain

On-chain
    Information stored internally in the blockchain

Organization ID
    For Avalon, the organization identifier of the organization that hosts
    the worker, e.g. a bank in the consortium or anonymous entity

Proxy model
    Avalon work order execution model in which a work order Invocation
    Proxy smart contract is used by an enterprise application smart contract
    to invoke work order execution in a Worker

Query only
    For Hyperledger Fabric, a parameter indicating if the
    function call will not result in a blockchain ledger change

Receipt
    For Avalon, a transaction proving a work order was processed
    by a worker

Receipt create status
    An Avalon work order receipt creation status with one of
    these values: 0 is pending, 1 is completed, 2 is processed, 3 is failed,
    and 4 is rejected. Values 5-254 are reserved. 255 means any status,
    and >255 are application-specific values. Defined in the EEA spec 7.1

Receipt status
    Status of an Avalon work order receipt

Registry
    For Avalon, a registry of workers for use in forwarding work
    orders to the proper worker

Registry status
    An Avalon worker registry status with one of these values:
    1 is active, 2 is temporarily off-line, and 3 is decommissioned

Request
    For Avalon, a JSON RPC message sent from the requester to
    an application or smart contract

Request ID
    For Avalon, a unique identifier that identifies a JSON RPC (JRPC) request

Requester
    Avalon entity that issues work orders using either an application or
    a smart contract. Requesters are identified by an Ethereum
    address or a DID that can be resolved to an Ethereum address

Requester ID
    For Avalon, a unique identifier that identifies a requester
    that generates work orders

Ropsten
    An Ethereum testnet. Allows one to test Ethereum smart contracts
    without spending Ether (ETH)

RSA-OAEP 3072
    Avalon's asymmetric encryption algorithm. Encrypts
    symmetric data encryption keys

SGX
    Intel Software Guard Extensions, Intel SGX, a hardware TEE implementation

SHA-256
    One of Avalon's digest algorithm for work order requests
    and responses

Signature
    In Avalon a signature signs data, often concatenated, with
    a private key to help assure the generator is authentic. A signature is
    verified with the signer's corresponding public key

Signature rules
    In Avalon, defined hashing and signing algorithms. In Avalon the
    rules are separated by a forward slash (/)

Singleton
    Singleton Enclave Avalon worker. Single enclave manages both
    keys and workloads. The default Avalon worker type. Compare to KME and WPE

Smart contract address
    For Ethereum, an Ethereum address that runs a
    Worker Registry Smart Contract API smart contract for this registry. For
    Fabric, a Fabric chain code name

Smart contract (SC)
    Signed, addressable program that executes on an
    Ethereum blockchain using the Ethereum ledger as data

Solidity
    A smart contract-oriented programming language used to write
    Ethereum smart contracts.
    Solidity source is compiled into EVM bytecode

Tag
    In Avalon an identifier for an encryption key. Usually the requester
    ID is used instead

Truffle
    A popular Ethereum development environment

Trusted compute (TC)
    Trusted computational resource for work order
    execution. It preserves data confidentiality, execution integrity and
    enforces data access policies. All Workers described in this specification
    are also Trusted Compute. Trusted Compute may implement those assurances
    in various ways. For example, Trusted Compute can base its trust on
    software-based cryptographic security guarantees, a service's reputation,
    virtualization, or a hardware-based Trusted Execution Environment such
    as Intel's SGX

Trusted compute base (TCB)
    The hardware, firmware, and software resources used by trusted compute

Trusted compute service (TCS)
    A service that provides trusted compute
    functionality. Hyperledger Avalon is an example of a TCS


Trusted execution environment (TEE)
    Hardware-based technology that executes only validated tasks,
    produces attested results, provides protection from
    malicious host software, and ensures confidentiality of
    shared encrypted data

Worker
    For Avalon, an off-chain confidential compute processor for
    work order execution, usually executing in a TEE, such as Intel SGX,
    that takes input data and produces a result.
    A Worker may be identified by an Ethereum address or a DID

Worker ID
    A unique identifier that identifies an Avalon worker that processes
    work orders. For Fabric, a Fabric address. For Ethereum, it could be
    derived from the worker's DID

Worker service ID
    Worker service Identifier

Worker service
    Implementation-dependent middleware entity that acts as
    a bridge for communications between a blockchain and a worker. A
    worker service may belong to an enterprise, a cloud service provider,
    or an individual sharing his or her available computational resources
    (subject to provisioning)

Worker status
    The status of an Avalon worker with one of these values:
    1 is active, 2 is temporarily off-line, 3 is decommissioned, and 4
    is compromised

Worker type
    A characteristic or classification of Avalon workers.
    Currently defined types are "TEE-SGX" for Intel SGX TEE, "MPC"
    for multi-party compute, and "ZK" for zero-knowledge proofs

Work load ID
    A string identifying a class of workload in order to lookup the correct
    workload processor.

Work order (WO)
    For Avalon, a unit of work submitted by a requester to
    a Worker for execution. Work orders may include one or more inputs
    (e.g. messages, input parameters, state, and datasets) and one or
    more outputs. Work order inputs and outputs can be sent as part of the
    request or response body (a.k.a. inline) or as links to remote storage
    locations. Work order inputs and outputs are normally sent encrypted

Work order ID
    A unique identifier that identifies an Avalon work
    order. Generated in a work order submit request by a requester

Work order response
    A response generated by an Avalon worker to a work
    order. The response is a JSON string

Worker pool
    A pool of idle workers ready to to execute work orders for a particular
    workload ID

WPE
    Work order Processor Enclave Avalon worker.
    WPE is a part of the worker pool responsible for the work order processing.
    It doesn't has access to the worker's private keys and relies on the KME
    to provide necessary context for the work order processing.
    Compare with KME and Singleton

Zero-knowledge proofs (zk proofs)
    Proofs where one can be assured of a result without being aware
    of the input. For example, not knowing someone's age,
    but knowing if they are in an age range

ZMQ (aka 0MQ, ZeroMQ)
    Zero Message Queue. A message transport API available on Linux; used
    between Avalon Enclave Manager and Listener

© Copyright 2020, Intel Corporation.
