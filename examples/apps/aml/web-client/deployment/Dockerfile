# Copyright 2019 Banco Santander S.A.
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

FROM nginx:1.9.15

LABEL maintainer="Santander Blockchain Team"

#Install Curl
RUN apt-get update
RUN apt-get install curl -y

#nginx configuration disable defaults
RUN mv /etc/nginx/conf.d/default.conf default.conf.disabled

#Copy the custom configuration
COPY nginx.conf /etc/nginx/nginx.conf

#Copy the application distribution
COPY dist /usr/share/nginx/html
