FROM golang:1.23.3 AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w"

FROM gcr.io/distroless/base-debian11 AS final

ENV PORT=8000
ENV CONNECTION_STRING=""

WORKDIR /app

COPY --from=build /app/cqiprog ./server

USER nonroot:nonroot

ENTRYPOINT ["/app/server"]
