package data

import (
	"context"
	"log"
	"time"
)

type RankingResult struct {
	TeamID      string `json:"teamId"`
	TotalGames  int    `json:"totalGames"`
	TotalWins   int    `json:"totalWins"`
	TotalDraws  int    `json:"totalDraws"`
	TotalLosses int    `json:"totalLosses"`
}

type RankingInfo struct {
	UpdatePeriod int             `json:"updatePeriod"`
	Results      []*RankingResult `json:"results"`
}

func updateRanking(data *Data, ctx context.Context) {
	rankingPeriod := data.settings.GetSettings().RankingPeriod

	ranking := RankingInfo{
		UpdatePeriod: int(rankingPeriod.Milliseconds()),
		Results:      make([]*RankingResult, 0, len(data.teams)),
	}

	games, err := data.gamesDB.getGamesSince(ctx, time.Now().Add(-rankingPeriod))

	if err != nil {
		log.Printf("Error getting games since %v: %v", time.Now().Add(-rankingPeriod), err)
		return
	}

	teams := map[string]*RankingResult{}
	for _, team := range data.teams {
		teams[team.ID] = &RankingResult{
			TeamID:      team.ID,
			TotalGames:  0,
			TotalWins:   0,
			TotalDraws:  0,
			TotalLosses: 0,
		}
	}

	for _, gameData := range games {
		teams[gameData.Team1Id].TotalGames++
		teams[gameData.Team2Id].TotalGames++

		if gameData.IsError {
			continue
		}

		if gameData.WinnerId == nil {
			teams[gameData.Team1Id].TotalDraws++
			teams[gameData.Team2Id].TotalDraws++
			continue
		}

		teams[*gameData.WinnerId].TotalWins++
		if *gameData.WinnerId == gameData.Team1Id {
			teams[gameData.Team2Id].TotalLosses++
		} else {
			teams[gameData.Team1Id].TotalLosses++
		}
	}

	for _, team := range teams {
		ranking.Results = append(ranking.Results, team)
	}

	data.rankingInfo = &ranking
}

func (p *Data) GetRanking() *RankingInfo {
	return p.rankingInfo
}
