package data

import (
    "context"
    _ "embed"
    "sync"

    "time"
)

const (
    DEFAULT_END_TIME = "2025-01-17T14:00:00Z"
)

type settingsEntries struct {
    endTime time.Time
}

type settings struct {
    db        *Database
    statsLock sync.RWMutex
    entries   settingsEntries
}

func getSetting(db *Database, ctx context.Context, key string) (*string, error) {
    conn, err := db.acquireConnection(ctx)
    if err != nil {
        return nil, err
    }
    defer conn.Release()

    var value string
    err = conn.QueryRow(ctx, "SELECT value FROM settings WHERE key = $1", key).Scan(&value)
    if err != nil {
        return nil, nil
    }

    return &value, nil
}

func setSetting(db *Database, key string, value string, ctx context.Context) error {
    conn, err := db.acquireConnection(ctx)
    if err != nil {
        return err
    }

    defer conn.Release()

    _, err = conn.Exec(ctx, "INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2", key, value)
    if err != nil {
        return err
    }

    return nil
}

func newSettings(db *Database, ctx context.Context) (*settings, error) {
    settings := settings{db: db, entries: settingsEntries{}, statsLock: sync.RWMutex{}}
    endTime, err := getSetting(db, ctx, "end_time")

    if err != nil {
        return nil, err
    }

    if endTime == nil {
        defaultEndTime := DEFAULT_END_TIME
        endTime = &defaultEndTime

        setSetting(db, "end_time", *endTime, ctx)
    }

    settings.entries.endTime, err = time.Parse(time.RFC3339, *endTime)

    if err != nil {
        return nil, err
    }

    return &settings, nil
}

func (p *settings) EndTime() time.Time {
    p.statsLock.RLock()
    defer p.statsLock.RUnlock()

    return p.entries.endTime
}

func (p *settings) SetEndTime(endTime time.Time, ctx context.Context) error {
    p.statsLock.Lock()
    defer p.statsLock.Unlock()

    p.entries.endTime = endTime

    return setSetting(p.db, "end_time", endTime.Format(time.RFC3339), ctx)
}
