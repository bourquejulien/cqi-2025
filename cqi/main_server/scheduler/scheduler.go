package scheduler

import (
	"context"
	"cqiprog/data"
	"cqiprog/infra"
	"log"
	"slices"
	"sync"
	"time"

	"github.com/google/uuid"
)

const (
	DEFAULT_TAG   = "latest"
	MATCH_TIMEOUT = 3 * time.Minute
)

type Match struct {
	Id         string
	Team1Id    string
	Team2Id    string
	ImageTeam1 string
	ImageTeam2 string
	LaunchTime *time.Time
}

type GameResult struct {
	Id         string  `json:"id"`
	WinnerId   *string `json:"winner_id"`
	IsError    bool    `json:"is_error"`
	Team1Score float32 `json:"team1_score"`
	Team2Score float32 `json:"team2_score"`
	ErrorData  *string `json:"error_data"`
	GameData   *string `json:"game_data"`
}

type Scheduler struct {
	isAutoplayEnabled bool
	ongoingMatches    map[string]*Match
	plannedMatches    []*Match
	cancel            *context.CancelFunc
	infra             *infra.Infra
	data              *data.Data
	lock              sync.RWMutex
}

func New(infra *infra.Infra, data *data.Data) (*Scheduler, error) {
	ctx, cancel := context.WithCancel(context.Background())
	schduler := Scheduler{false, make(map[string]*Match), make([]*Match, 0, data.GetSettings().MaxConcurrentMatch*2), &cancel, infra, data, sync.RWMutex{}}

	go daemon(&schduler, ctx)

	return &schduler, nil
}

func (s *Scheduler) ListOngoing() []*Match {
	s.lock.RLock()
	defer s.lock.RUnlock()

	matches := make([]*Match, 0, len(s.ongoingMatches))
	for _, match := range s.ongoingMatches {
		matches = append(matches, match)
	}

	return matches
}

func (s *Scheduler) SetAutoplay(isEnabled bool) {
	s.isAutoplayEnabled = isEnabled
}

func (s *Scheduler) AddResult(gameResult *GameResult, ctx context.Context) bool {
	s.lock.Lock()
	defer s.lock.Unlock()

	return s.addResult(gameResult, ctx)
}

func (s *Scheduler) addResult(gameResult *GameResult, ctx context.Context) bool {
	match, ok := s.ongoingMatches[gameResult.Id]

	if !ok {
		return false
	}

	delete(s.ongoingMatches, gameResult.Id)

	gameData := data.DbGame{
		Id:         gameResult.Id,
		StartTime:  *match.LaunchTime,
		EndTime:    time.Now().UTC(),
		Team1Id:    match.Team1Id,
		Team2Id:    match.Team2Id,
		WinnerId:   gameResult.WinnerId,
		IsError:    gameResult.IsError,
		Team1Score: gameResult.Team1Score,
		Team2Score: gameResult.Team2Score,
		ErrorData:  compress(gameResult.ErrorData),
		GameData:   compress(gameResult.GameData),
	}
	err := s.data.AddGame(&gameData, ctx)

	if err != nil {
		log.Println(err)
		return false
	}

	return true
}

func (s *Scheduler) ForceAddMatch(team1Id string, team2Id string, ctx context.Context) (bool, string) {
	realTeamIds := make([]string, 0, 2)
	botIds := make([]string, 0, 2)

	if team1Id == team2Id {
		return false, "Teams must be different"
	}

	allBotIds := s.data.GetTeamIds(true)
	allTeamIds := s.data.GetTeamIds(false)

	for _, id := range []string{team1Id, team2Id} {
		if slices.Contains(allBotIds, id) {
			botIds = append(botIds, id)
		} else if slices.Contains(allTeamIds, id) {
			realTeamIds = append(realTeamIds, id)
		} else {
			return false, "Team not found: " + id
		}
	}

	teamImages, err := s.infra.ListImages(realTeamIds, []string{DEFAULT_TAG}, ctx)

	if err != nil {
		log.Println(err)
		return false, "Error getting images"
	}

	botImages := s.infra.ListBotImages(botIds)
	teamImages = append(teamImages, botImages...)

	if len(teamImages) < 2 {
		log.Println("Mismatch between images names and repositories")
		return false, "Repository not found for all teams"
	}

	match := Match{uuid.NewString(), team1Id, team2Id, "", "", nil}

	for _, teamImage := range teamImages {
		if len(teamImage.Images) == 0 {
			return false, "No images found for team: " + teamImage.TeamId
		}

		if teamImage.TeamId == team1Id {
			match.ImageTeam1 = teamImage.Images[0].FullUrl
		} else {
			match.ImageTeam2 = teamImage.Images[0].FullUrl
		}
	}

	s.lock.Lock()
	defer s.lock.Unlock()

	s.plannedMatches = append(s.plannedMatches, &match)

	return true, ""
}

func (s *Scheduler) PopMatch(n int, ctx context.Context) []*Match {
	s.lock.Lock()
	defer s.lock.Unlock()

	if n > len(s.plannedMatches) {
		n = len(s.plannedMatches)
	}

	n = max(0, min(n, s.data.GetSettings().MaxConcurrentMatch-len(s.ongoingMatches)))

	matches := make([]*Match, n)
	launchTime := time.Now().UTC()
	for i, match := range s.plannedMatches[:n] {
		match.LaunchTime = &launchTime
		s.ongoingMatches[match.Id] = match

		matches[i] = match
	}

	s.plannedMatches = s.plannedMatches[n:]

	return matches
}

func (s *Scheduler) Reset() {
	s.lock.Lock()
	defer s.lock.Unlock()
	s.ongoingMatches = make(map[string]*Match)
}

func (s *Scheduler) Close() {
	(*s.cancel)()
}
