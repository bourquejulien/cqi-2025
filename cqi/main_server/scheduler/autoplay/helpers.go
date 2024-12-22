package autoplay

import "math"

func computeMean(values []float64) float64 {
	if len(values) == 0 {
		return 0.0
	}

	var sum float64 = 0.0
	for _, value := range values {
		sum += value
	}

	return sum / float64(len(values))
}

func computeVariance(values []float64, mean float64) float64 {
	if len(values) == 0 {
		return 0.0
	}

	sum := 0.0
	for _, value := range values {
		diff := float64(value) - mean
		sum += math.Pow(diff, 2)
	}

	return sum / float64(len(values))
}

func computeStandardDeviation(values []float64, mean float64) float64 {
	return math.Sqrt(computeVariance(values, mean))
}

