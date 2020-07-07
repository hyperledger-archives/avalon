FROM ubuntu:bionic as base_image

# Ignore timezone prompt in apt
ENV DEBIAN_FRONTEND=noninteractive

# Add necessary packages
RUN apt-get update \
 && apt-get install -y -q \
    ca-certificates \
    pkg-config \
    python3-dev \
    python3-pip \
    gcc \
 && python3 -m pip install pyzmq pycryptodomex ecdsa\
 && apt-get clean 

# Make Python3 default
RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /home/pythonworker

COPY . .

RUN make && make install

# GSC (Graphene Shielded Container) docker image build depends on child
# application manifest files.
# Python worker makes use of Python Cryptodomex which indirectly depends on
# mutiple applications and manifest files has to be listed in GSC build.
# gcc depends on collect2 and GSC build exits with below message.
# "Command 'which collect2' returned non-zero exit status 1".
# Add a temporary workaround to add collect2 to path.
ENV PATH=$PATH:/usr/lib/gcc/x86_64-linux-gnu/7.5.0/

# Pass python file as docker command line argument
# This is required for Graphene.
CMD ["python"]

