package server

import "time"

type Stats struct {
	TotalGames int       `json:"totalGames"`
	EndTime    time.Time `json:"endTime"`
}

type Match struct {
	Id         string `json:"id"`
	Team1Id    string `json:"team1_id"`
	Team2Id    string `json:"team2_id"`
	ImageTeam1 string `json:"image_team1"`
	ImageTeam2 string `json:"image_team2"`
}
