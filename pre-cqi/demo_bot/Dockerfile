ARG NAME=pre-cqi

FROM rust:1.81-alpine3.20 AS build
ARG NAME

RUN apk add --no-cache musl-dev

RUN USER=root cargo new --bin $NAME
WORKDIR /$NAME

COPY ./Cargo.lock ./Cargo.lock
COPY ./Cargo.toml ./Cargo.toml

RUN cargo build --release

RUN rm src/*.rs
COPY ./src ./src

RUN rm -f ./target/release/deps/pre*
RUN cargo build --release

FROM alpine:3.20 AS release
ARG NAME

WORKDIR /app
COPY --from=build /$NAME/target/release/$NAME app

ENTRYPOINT ["/app/app"]
