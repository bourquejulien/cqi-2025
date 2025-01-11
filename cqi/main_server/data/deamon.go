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
	updateRanking(p, ctx)
	
	go deamon(p, ctx)
}

func deamon(data *Data, ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			log.Printf("data daemon is done")
			return
		default:
			deamonCtx, cancelFunc := context.WithTimeout(ctx, TIMEOUT)
			defer cancelFunc()

			updateRanking(data, deamonCtx)
			data.gamesDB.cache.cleanup()

			time.Sleep(DEAMON_INTERVAL)
		}
	}
}
