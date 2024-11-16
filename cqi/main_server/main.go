package main

import (
	"context"
	"cqiprog/data"
	"cqiprog/scheduler"
	"cqiprog/server"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"
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

func main() {
	port := os.Getenv("PORT")
	connectionString := os.Getenv("CONNECTION_STRING")

	if port == "" {
		port = "8000"
	}

	if connectionString == "" {
		connectionString = "user=postgres password=postgres dbname=postgres sslmode=disable host=localhost"
	}

	data, err := data.New(connectionString)

	if err != nil {
		log.Fatal(err)
	}

	defer data.Close(context.Background())

	scheduler, err := scheduler.New()

	if err != nil {
		log.Fatal(err)
	}

	defer scheduler.Close()

	server := server.Server{Data: data, Scheduler: scheduler}

	err = ListenAndServe(&server, port)
	if err != nil {
		log.Println(err)
	}
}
