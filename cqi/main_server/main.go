package main

import (
    "context"
    "cqiprog/data"
    "cqiprog/infra"
    "cqiprog/scheduler"
    "cqiprog/server"
    "fmt"
    "log"
    "os"
    "os/signal"
    "syscall"
    "time"
)

const (
    DEFAULT_CONNECTION_STRING = "user=postgres password=postgres dbname=postgres sslmode=disable host=localhost"
)

func ListenAndServe(server *server.Server, port string) error {
    serverCtx, serverStopCtx := context.WithCancel(context.Background())

    sig := make(chan os.Signal, 1)
    signal.Notify(sig, syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)
    go func() {
        <-sig

        shutdownCtx, _ := context.WithTimeout(serverCtx, 10*time.Second)

        go func() {
            <-shutdownCtx.Done()
            if shutdownCtx.Err() == context.DeadlineExceeded {
                log.Fatal("graceful shutdown timed out.. forcing exit.")
            }
        }()

        err := server.Stop(shutdownCtx)
        if err != nil {
            log.Fatal(err)
        }
        serverStopCtx()
    }()

    server.Init()

    fmt.Printf("Server started on port %s\n", port)
    if err := server.Start(8000); err != nil {
        return err
    }

    <-serverCtx.Done()

    return nil
}

func getConnectionString(i *infra.Infra, ctx context.Context) (string, error) {
    connectionString := os.Getenv("CONNECTION_STRING")

    if connectionString != "" {
        return connectionString, nil
    }

    if !infra.IsRunningOnEC2() {
        return DEFAULT_CONNECTION_STRING, nil
    }

    result, err := i.GetRdsConnectionString(ctx)

    if err != nil {
        return "", err
    }

    return result, nil
}

func main() {
    port := os.Getenv("PORT")

    if port == "" {
        port = "8000"
    }

    infra, err := infra.New(context.Background())
    if err != nil {
        log.Fatal(err)
    }

    connectionString, err := getConnectionString(infra, context.Background())
    if err != nil {
        log.Fatal(err)
    }

    data, err := data.New(connectionString, context.Background())
    if err != nil {
        log.Fatal(err)
    }

    defer data.Close(context.Background())

    scheduler, err := scheduler.New(infra, data)
    if err != nil {
        log.Fatal(err)
    }

    defer scheduler.Close()

    internalKey, err := infra.GetInternalKey(context.Background())
    if err != nil {
        log.Fatal(err)
    }

    server := server.Server{Data: data, Scheduler: scheduler, InternalKey: internalKey}

    err = ListenAndServe(&server, port)
    if err != nil {
        log.Println(err)
    }
}
