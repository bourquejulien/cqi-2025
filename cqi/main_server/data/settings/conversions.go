package settings

import (
	"strconv"
	"time"
)

func intToString(value int) string {
	return strconv.Itoa(value)
}

func fromMap(s *SettingsEntries, m map[string]*string) error {
	if value, ok := m["endTime"]; ok {
		endTime, err := time.Parse(time.RFC3339, *value)
		if err != nil {
			return nil
		}
		s.EndTime = &endTime
	}

	if value, ok := m["rankingPeriod"]; ok {
		rankingPeriod, err := time.ParseDuration(*value)
		if err != nil {
			return nil
		}
		s.RankingPeriod = rankingPeriod
	}

	if value, ok := m["maxConcurrentMatch"]; ok {
		maxConcurrentMatch, err := strconv.Atoi(*value)
		if err != nil {
			return nil
		}
		s.MaxConcurrentMatch = maxConcurrentMatch
	}

	if value, ok := m["maxMatchPerRunner"]; ok {
		maxMatchPerRunner, err := strconv.Atoi(*value)
		if err != nil {
			return nil
		}
		s.MaxMatchPerRunner = maxMatchPerRunner
	}

	if value, ok := m["matchTimeout"]; ok {
		matchTimeout, err := time.ParseDuration(*value)
		if err != nil {
			return nil
		}
		s.MatchTimeout = matchTimeout
	}

	return nil
}
