FROM ubuntu:22.04 AS base

RUN apt-get update && apt-get install -y build-essential binutils curl lazarus

WORKDIR /build

COPY ./Makefile ./Makefile
RUN make prereq

COPY ./ ./
RUN make build

FROM busybox:glibc AS final

EXPOSE 11000

WORKDIR /run

COPY --from=base /build/main ./

ENTRYPOINT [ "/run/main" ]
