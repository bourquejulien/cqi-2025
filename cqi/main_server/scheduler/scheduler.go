package scheduler

import (
	"context"
	"cqiprog/infra"
	"time"
)

type Match struct {
	Id         string
	Team1Id    string
	Team2Id    string
	ImageTeam1 string
	ImageTeam2 string
	LaunchTime *time.Time
}

type Scheduler struct {
	isAutoplayEnabled bool
	ongoingMatches    []Match
	plannedMatches    []Match
	cancel            *context.CancelFunc
	infra             *infra.Infra
}

func New(infra *infra.Infra) (*Scheduler, error) {
	ctx, cancel := context.WithCancel(context.Background())
	schduler := Scheduler{false, make([]Match, 0), make([]Match, 0), &cancel, infra}

	go daemon(&schduler, ctx)

	return &schduler, nil
}

func (s *Scheduler) SetAutoplay(isEnabled bool) {
	s.isAutoplayEnabled = isEnabled
}

func (s *Scheduler) AddMatch(match Match) bool {
	return false
}

func (s *Scheduler) PopMatch(n int) []Match {
	return nil
}

func (s *Scheduler) Reset() {
	s.ongoingMatches = make([]Match, 0)
}

func (s *Scheduler) Close() {
	(*s.cancel)()
}

func daemon(scheduler *Scheduler, ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			println("scheduler daemon is done")
			return
		default:
			time.Sleep(1 * time.Second)
			println("hello world")
		}
	}
}
