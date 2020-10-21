FROM ubuntu:bionic

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-toml \
    gcc \
 && python3 -m pip install pyzmq pycryptodomex ecdsa\
 && apt-get clean 

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

COPY ./tc/graphene/python_worker/  /home/python_worker/
COPY ./common/python /home/python_worker/common/python
COPY ./common/crypto_utils /home/python_worker/common/crypto_utils
COPY ./bin/get_version /home/python_worker/bin/get_version
COPY ./VERSION /home/python_worker/VERSION

WORKDIR /home/python_worker/common/python

RUN echo "Building Avalon Common Python\n" \
 && make && make install

WORKDIR /home/python_worker/common/crypto_utils

# Build common python crypto utils
RUN echo "Building Avalon Common Crypto Python\n" \
 && make && make install

WORKDIR /home/python_worker/

#Build and install python worker
RUN make && make install

# GSC (Graphene Shielded Container) docker image build depends on child
# application manifest files.
# Python worker makes use of Python Cryptodomex which indirectly depends on
# multiple applications and manifest files has to be listed in GSC build.
# gcc depends on collect2 and GSC build exits with below message.
# "Command 'which collect2' returned non-zero exit status 1".
# Add a temporary workaround to add collect2 to path.
ENV PATH=$PATH:/usr/lib/gcc/x86_64-linux-gnu/7.5.0/

# Pass python file as docker command line argument
# This is required for Graphene.
CMD ["python"]

