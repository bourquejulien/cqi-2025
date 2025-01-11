package settings

import (
	"fmt"
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
			return err
		}

		s.EndTime = &endTime
	}

	if value, ok := m["rankingPeriod"]; ok {
		rankingPeriod, err := time.ParseDuration(*value)
		if err != nil {
			return err
		}

		if rankingPeriod < 0 {
			return fmt.Errorf("rankingPeriod must be positive")
		}

		s.RankingPeriod = rankingPeriod
	}

	if value, ok := m["maxConcurrentMatch"]; ok {
		maxConcurrentMatch, err := strconv.Atoi(*value)
		if err != nil {
			return err
		}

		if maxConcurrentMatch < 0 {
			return fmt.Errorf("maxConcurrentMatch must be positive")
		}

		s.MaxConcurrentMatch = maxConcurrentMatch
	}

	if value, ok := m["maxMatchPerRunner"]; ok {
		maxMatchPerRunner, err := strconv.Atoi(*value)
		if err != nil {
			return err
		}

		if maxMatchPerRunner < 1 {
			return fmt.Errorf("maxMatchPerRunner must be > 1")
		}

		s.MaxMatchPerRunner = maxMatchPerRunner
	}

	if value, ok := m["matchTimeout"]; ok {
		matchTimeout, err := time.ParseDuration(*value)
		if err != nil {
			return err
		}

		if matchTimeout < 0 {
			return fmt.Errorf("matchTimeout must be positive")
		}

		s.MatchTimeout = matchTimeout
	}

	return nil
}
