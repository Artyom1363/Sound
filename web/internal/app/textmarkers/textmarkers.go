package textmarkers

import (
	"fmt"
	"strings"
	"web/internal/app/files"
)

const markerParasite = "<span style=\"background-color: rgb(255, 255, 0);\">%s</span>"
const markerProfanity = "<span style=\"background-color: rgb(255, 0, 0);\">%s</span>"

func EnrichTextWithMarkers(text string, parasiteMarkers []int, profanityMarkers []int) string {
	text = strings.TrimSpace(text)
	words := strings.Split(text, " ")
	for _, marker := range parasiteMarkers {
		if len(words) > marker {
			words[marker] = fmt.Sprintf(markerParasite, words[marker])
		}
	}

	for _, marker := range profanityMarkers {
		if len(words) > marker {
			words[marker] = fmt.Sprintf(markerProfanity, words[marker])
		}
	}
	return strings.Join(words, " ")
}

func Run(text string, parasiteMarkers []int, profanityMarkers []int) (string, error) {
	enrichedText := EnrichTextWithMarkers(text, parasiteMarkers, profanityMarkers)
	return files.SaveToTextFile([]byte(enrichedText))
}
