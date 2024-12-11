package scheduler

import (
    "context"
    "cqiprog/data"
    "cqiprog/infra"
    "log"
    "sync"
    "time"

    "github.com/google/uuid"
    "golang.org/x/exp/rand"
)

const (
    DEFAULT_TAG         = "latest"
    MAX_PLANNED_MATCHES = 10
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
    schduler := Scheduler{false, make(map[string]*Match), make([]*Match, 0, MAX_PLANNED_MATCHES*2), &cancel, infra, data, sync.RWMutex{}}

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

    match, ok := s.ongoingMatches[gameResult.Id]

    if !ok {
        return false
    }

    delete(s.ongoingMatches, gameResult.Id)

    gameData := data.DbGame{
        Id:         gameResult.Id,
        StartTime:  *match.LaunchTime,
        EndTime:    time.Now(),
        Team1Id:    match.Team1Id,
        Team2Id:    match.Team2Id,
        WinnerId:   gameResult.WinnerId,
        IsError:    gameResult.IsError,
        Team1Score: gameResult.Team1Score,
        Team2Score: gameResult.Team2Score,
        ErrorData:  gameResult.ErrorData,
        GameData:   gameResult.GameData,
    }
    err := s.data.AddGame(&gameData, ctx)

    if err != nil {
        log.Println(err)
        return false
    }

    return true
}

func (s *Scheduler) ForceAddMatch(team1Id string, team2Id string, ctx context.Context) bool {
    realTeamIds := make([]string, 0, 2)
    botIds := make([]string, 0, 2)

    allBotIds := s.data.GetTeamIds(true)
    for _, id := range []string{team1Id, team2Id} {
        isBot := false
        for botId, _ := range allBotIds {
            if id == botId {
                isBot = true
                break
            }
        }

        if isBot {
            botIds = append(botIds, id)
        } else {
            realTeamIds = append(realTeamIds, id)
        }
    }

    teamImages, err := s.infra.ListImages(realTeamIds, []string{DEFAULT_TAG}, ctx)

    if err != nil {
        log.Println(err)
        return false
    }

    botImages := s.infra.ListBotImages(botIds)
    teamImages = append(teamImages, botImages...)

    s.lock.Lock()
    defer s.lock.Unlock()

    match := Match{uuid.NewString(), team1Id, team2Id, DEFAULT_TAG, DEFAULT_TAG, nil}

    for _, teamImage := range teamImages {
        if len(teamImage.Images) == 0 {
            return false
        }
    }

    s.plannedMatches = append(s.plannedMatches, &match)

    return true
}

func (s *Scheduler) PopMatch(n int, ctx context.Context) []Match {
    s.lock.Lock()
    defer s.lock.Unlock()

    if n > len(s.plannedMatches) {
        n = len(s.plannedMatches)
    }

    matches := make([]Match, n)
    launchTime := time.Now()
    for i, match := range s.plannedMatches[:n] {
        match.LaunchTime = &launchTime
        s.ongoingMatches[match.Id] = match

        matches[i] = *match
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

func daemon(scheduler *Scheduler, ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            println("scheduler daemon is done")
            return
        default:
            time.Sleep(1 * time.Second)
            autoAddMatch(scheduler, ctx)
        }
    }
}

func autoAddMatch(scheduler *Scheduler, ctx context.Context) {
    if !scheduler.isAutoplayEnabled {
        return
    }

    teamIds := make([]string, 0)
    for id := range scheduler.data.GetTeamIds(false) {
        teamIds = append(teamIds, id)
    }
    teamImages, err := scheduler.infra.ListImages(teamIds, []string{DEFAULT_TAG}, ctx)

    botIds := make([]string, 0)
    for id := range scheduler.data.GetTeamIds(true) {
        botIds = append(botIds, id)
    }
    botImages := scheduler.infra.ListBotImages(botIds)

    // TODO: Don't queue bot against bot
    teamImages = append(teamImages, botImages...)

    if err != nil {
        log.Println(err)
        return
    }

    if len(teamImages) < 2 {
        return
    }

    scheduler.lock.Lock()
    defer scheduler.lock.Unlock()

    countToAdd := MAX_PLANNED_MATCHES - len(scheduler.plannedMatches)

    if countToAdd <= 0 {
        return
    }

    for i := 0; i < countToAdd; i++ {
        team1Index := rand.Intn(len(teamImages))
        team2Index := rand.Intn(len(teamImages))
        for team1Index == team2Index {
            team2Index = rand.Intn(len(teamImages))
        }

        match := Match{
            Id:         uuid.NewString(),
            Team1Id:    teamImages[team1Index].TeamId,
            Team2Id:    teamImages[team2Index].TeamId,
            ImageTeam1: teamImages[team1Index].Images[0].FullUrl,
            ImageTeam2: teamImages[team2Index].Images[0].FullUrl,
            LaunchTime: nil,
        }

        scheduler.plannedMatches = append(scheduler.plannedMatches, &match)
    }
}
