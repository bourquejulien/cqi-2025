package data

import (
	"context"
	"log"
	"time"
)

const (
	DEAMON_INTERVAL = 30 * time.Second
	TIMEOUT         = 5 * time.Second
)

func (p *Data) startDeamon(ctx context.Context) {
	go deamon(p, ctx)
}

func deamon(data *Data, ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			log.Default().Printf("data daemon is done")
			return
		default:
			log.Default().Printf("data daemon is running")

			deamonCtx, cancelFunc := context.WithTimeout(ctx, TIMEOUT)
			defer cancelFunc()

			updateRanking(data, deamonCtx)
			data.gamesDB.cache.cleanup()

			time.Sleep(DEAMON_INTERVAL)
		}
	}
}
