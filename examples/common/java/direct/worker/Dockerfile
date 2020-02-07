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

FROM openjdk:8u191-jre-alpine3.9

RUN apk add --no-cache bash coreutils openssl zip

COPY build/resources/main/decrypt-dataset.sh    /decrypt-dataset.sh
COPY build/resources/main/encrypt-result.sh     /encrypt-result.sh
COPY build/resources/main/entrypoint.sh         entrypoint.sh

RUN chmod +x /decrypt-dataset.sh && \
    chmod +x /encrypt-result.sh && \
    chmod +x entrypoint.sh

COPY build/libs/eea-worker-@projectversion@.jar eea-tcf-worker.jar

ENTRYPOINT ["./entrypoint.sh"]
