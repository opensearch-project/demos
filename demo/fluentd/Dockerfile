ARG FLUENTD_VERSION

FROM fluent/fluentd:${FLUENTD_VERSION}
USER root
RUN ["apk", "add", "ruby-dev"]
RUN ["fluent-gem", "install", "fluent-plugin-opensearch"]
RUN ["gem", "install", "fluent-plugin-kafka", "--no-document"]
