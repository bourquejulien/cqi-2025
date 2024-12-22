package autoplay

import (
	"cqiprog/data"
	"cqiprog/infra"
	"log"
	"math/rand/v2"
)

type container struct {
	totalGames  int
	totalErrors int
	probability float64
	teamImage   *infra.TeamImage
}

type stats struct {
	totalCountMean      float64
	errorCountMean       float64
	totalVariation float64
	lostVariation  float64
}

func GetNextTeam(rankingInfo *data.RankingInfo, availableTeamImages []*infra.TeamImage, scheduledMatches []string) *infra.TeamImage {
	if len(availableTeamImages) == 0 {
		return nil
	}

	teamIdMapping := map[string]*container{}
	for _, team := range rankingInfo.Results {
		var currentTeamImage *infra.TeamImage
		for _, teamImage := range availableTeamImages {
			if teamImage.TeamId == team.TeamID {
				currentTeamImage = teamImage
				break
			}
		}

		if currentTeamImage == nil {
			continue
		}

		teamIdMapping[team.TeamID] = &container{
			totalGames:  team.TotalGames,
			totalErrors: team.TotalGames - team.TotalWins - team.TotalDraws,
			probability: 1.0 / float64(len(availableTeamImages)),
			teamImage:   currentTeamImage,
		}
	}

	if len(availableTeamImages) != len(teamIdMapping) {
		log.Println("Some teams are missing from the ranking info")
		return nil
	}

	for _, id := range scheduledMatches {
		if container, ok := teamIdMapping[id]; ok {
			container.totalGames++
		}
	}

	if len(teamIdMapping) == 1 {
		for _, container := range teamIdMapping {
			return container.teamImage
		}
	}

	containers := make([]*container, 0, len(teamIdMapping))
	for _, container := range teamIdMapping {
		containers = append(containers, container)
	}

	return computeNextTeam(containers)
}

func computeNextTeam(containers []*container) *infra.TeamImage {
	stats := GetStats(containers)

	for _, container := range containers {
		container.probability *= computeTeamProbabilityMultiplier(container.totalGames, container.totalErrors, stats)
	}

	return selectTeam(containers)
}

func GetStats(containers []*container) *stats {
	totalGameCounts := make([]float64, 0.0, len(containers))
	totalErrorCount := make([]float64, 0.0, len(containers))

	for _, container := range containers {
		totalGameCounts = append(totalGameCounts, float64(container.totalGames))
		totalErrorCount = append(totalErrorCount, float64(container.totalErrors))
	}

	totalCountMean := computeMean(totalGameCounts)
	errorCountMean := computeMean(totalErrorCount)

	return &stats{
		totalCountMean:      totalCountMean,
		errorCountMean:       errorCountMean,
		totalVariation: computeVariance(totalGameCounts, totalCountMean),
		lostVariation:  computeVariance(totalErrorCount, errorCountMean),
	}
}

func computeTeamProbabilityMultiplier(totalGames, totalErrors int, stats *stats) float64 {
	multiplier := 1.0

	if stats.totalCountMean <= 1 {
		return multiplier
	}

	if totalGames < int(stats.totalCountMean) {
		multiplier = 1.0 + (float64(int(stats.totalCountMean)-totalGames) / stats.totalCountMean)
	}

	if stats.errorCountMean <= 1 {
		return multiplier
	}

	if totalErrors > int(stats.errorCountMean + stats.lostVariation) {
		multiplier /= 2
	}

	return multiplier
}

func selectTeam(containers []*container) *infra.TeamImage {
	probabilitiesSum := 0.0
	for _, container := range containers {
		probabilitiesSum += container.probability
	}
	
	randomValue := rand.Float64() * probabilitiesSum
	accumulator := 0.0

	for _, container := range containers {
		accumulator += container.probability

		if accumulator >= randomValue {
			return container.teamImage
		}
	}

	return nil
}
