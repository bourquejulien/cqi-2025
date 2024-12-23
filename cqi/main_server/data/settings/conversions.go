package settings

import (
	"strconv"
	"time"
)

func getTimeFromString(value string) (time.Time, error) {
	return time.Parse(time.RFC3339, value)
}

func timeToString(value time.Time) string {
	return value.Format(time.RFC3339)
}

func getDurationFromString(value string) (time.Duration, error) {
	return time.ParseDuration(value)
}

func durationToString(value time.Duration) string {
	return value.String()
}

func getIntFromString(value string) (int, error) {
	return strconv.Atoi(value)
}

func intToString(value int) string {
	return strconv.Itoa(value)
}
