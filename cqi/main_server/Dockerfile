FROM golang:1.23.3 AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w"

FROM busybox AS builder

ARG BUSYBOX_VERSION=1.31.0-i686-uclibc
ADD https://busybox.net/downloads/binaries/$BUSYBOX_VERSION/busybox_WGET /wget
RUN chmod a+x /wget

FROM gcr.io/distroless/base-debian11 AS final

ENV PORT=8000
ENV CONNECTION_STRING=""

HEALTHCHECK --interval=30s \
            --timeout=5s \
            CMD ["/usr/bin/wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/health"]

WORKDIR /app

COPY --from=builder /wget /usr/bin/wget
COPY --from=build /app/cqiprog ./server

USER nonroot:nonroot

ENTRYPOINT ["/app/server"]
