package data

import (
	"context"
	_ "embed"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Database struct {
	pool  *pgxpool.Pool
}

//go:embed init_data/init.sql
var initSQL string

func newDatabase(connectionString string, ctx context.Context) (*Database, error) {
	conn, err := pgxpool.New(ctx, connectionString)
	if err != nil {
		return nil, err
	}

	_, err = conn.Exec(ctx, initSQL)
	if err != nil {
		return nil, err
	}

	return &Database{conn}, nil
}

func (p *Database) acquireConnection(ctx context.Context) (*pgxpool.Conn, error) {
	conn, err := p.pool.Acquire(ctx)

	if err != nil {
		return nil, err
	}

	return conn, nil
}

func (p *Database) close() {
	p.pool.Close()
}
