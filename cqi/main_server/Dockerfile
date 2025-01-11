FROM golang:1.23.3 AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w"

FROM busybox:1.35.0-uclibc AS busybox

FROM gcr.io/distroless/base-debian11 AS final

ENV PORT=8000
ENV CONNECTION_STRING=""

COPY --from=busybox /bin/wget /bin/wget

HEALTHCHECK --interval=30s \
            --timeout=5s \
            CMD ["/bin/wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/health"]

WORKDIR /app

COPY --from=build /app/cqiprog ./server

USER nonroot:nonroot

ENTRYPOINT ["/app/server"]
