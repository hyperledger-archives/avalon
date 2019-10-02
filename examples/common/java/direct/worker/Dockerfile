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