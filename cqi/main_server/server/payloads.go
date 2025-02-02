package server

import (
	"cqiprog/data"
	"time"
)


type OngoingMatch struct {
	Id        string    `json:"id"`
	Team1Id   string    `json:"team1Id"`
	Team2Id   string    `json:"team2Id"`
	StartTime time.Time `json:"startTime"`
}

type Stats struct {
	TotalGames  int               `json:"totalGames"`
	EndTime     time.Time         `json:"endTime"`
	RankingInfo *data.RankingInfo `json:"rankingInfo"`
	OngoingMatches []OngoingMatch `json:"ongoingMatches"`
}

type Match struct {
	Id         string `json:"id"`
	Team1Id    string `json:"team1_id"`
	Team2Id    string `json:"team2_id"`
	ImageTeam1 string `json:"image_team1"`
	ImageTeam2 string `json:"image_team2"`
}

type MatchInfo struct {
	MaxConcurrentMatch  int      `json:"maxConcurrentMatch"`
	MatchTimeoutSeconds int      `json:"matchTimeoutSeconds"`
	Matches             []*Match `json:"matches"`
}

type GameResults struct {
	TotalGameCount int            `json:"totalGameCount"`
	Results        []*data.DbGame `json:"results"`
}

type LaunchData struct {
	TeamIdMapping map[string]string `json:"teamIdMapping"`
	EndTime       time.Time         `json:"endTime"`
}
