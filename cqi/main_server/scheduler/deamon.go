package scheduler

import (
	"context"
	"cqiprog/scheduler/autoplay"
	b64 "encoding/base64"
	"encoding/json"
	"log"
	"time"

	"github.com/google/uuid"
	"golang.org/x/exp/rand"
)

type ErrorData struct {
	ErrorType string `json:"errorType"`
}

func daemon(scheduler *Scheduler, ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			println("scheduler daemon is done")
			return
		default:
			time.Sleep(1 * time.Second)

			deamonCtx, cancelFunc := context.WithTimeout(ctx, 5*time.Second)
			defer cancelFunc()

			autoAddMatch(scheduler, deamonCtx)
			cleanupMatches(scheduler, deamonCtx)
		}
	}
}

func autoAddMatch(scheduler *Scheduler, ctx context.Context) {
	if !scheduler.isAutoplayEnabled {
		return
	}

	teamImages, err := scheduler.infra.ListImages(scheduler.data.GetTeamIds(false), []string{DEFAULT_TAG}, ctx)

	if err != nil {
		log.Println(err)
		return
	}

	if len(teamImages) == 0 {
		return
	}

	botImages := scheduler.infra.ListBotImages(scheduler.data.GetTeamIds(true))

	allImages := append(teamImages, botImages...)

	if len(allImages) < 2 {
		return
	}

	scheduler.lock.Lock()
	defer scheduler.lock.Unlock()

	countToAdd := max(min(scheduler.data.GetSettings().MaxConcurrentMatch-len(scheduler.plannedMatches), len(teamImages)), 0)

	if countToAdd <= 0 {
		return
	}

	rankingInfo := scheduler.data.GetRanking()
	getPlannedMatchesTeamIds := func(plannedMatches []*Match) []string {
		ids := make([]string, 0, 2*len(plannedMatches))
		for _, match := range plannedMatches {
			ids = append(ids, match.Team1Id, match.Team2Id)
		}

		return ids
	}

	for i := 0; i < countToAdd; i++ {
		teamImage := autoplay.GetNextTeam(rankingInfo, teamImages, getPlannedMatchesTeamIds(scheduler.plannedMatches))
		if teamImage == nil {
			continue
		}

		otherImageIndex := rand.Intn(len(allImages))

		for teamImage.TeamId == allImages[otherImageIndex].TeamId {
			otherImageIndex = rand.Intn(len(allImages))
		}

		otherImage := allImages[otherImageIndex]
		match := Match{
			Id:         uuid.NewString(),
			Team1Id:    teamImage.TeamId,
			Team2Id:    otherImage.TeamId,
			ImageTeam1: teamImage.Images[0].FullUrl,
			ImageTeam2: otherImage.Images[0].FullUrl,
			LaunchTime: nil,
		}

		scheduler.plannedMatches = append(scheduler.plannedMatches, &match)
	}
}

func cleanupMatches(scheduler *Scheduler, ctx context.Context) {
	scheduler.lock.Lock()
	defer scheduler.lock.Unlock()

	getTimeoutErrorData := func() string {
		errorData := ErrorData{
			ErrorType: "timeout",
		}

		jsonData, err := json.Marshal(errorData)
		if err != nil {
			panic(err)
		}

		return b64.StdEncoding.EncodeToString(jsonData)
	}

	errorData := getTimeoutErrorData()

	timeout := scheduler.data.GetSettings().MatchTimeout
	timeout += time.Minute + 30 * time.Second // Give some extra time for the game runner to get the results
	for id, match := range scheduler.ongoingMatches {
		if match.LaunchTime.Add(timeout).Before(time.Now().UTC()) {
			gameResult := &GameResult{
				Id:        id,
				IsError:   true,
				ErrorData: &errorData,
			}
			scheduler.addResult(gameResult, ctx)
		}
	}
}
