package markers

import (
	"fmt"
	"strings"
)

const markerParasite = "<span style=\"background-color: rgb(255, 255, 0);\">%s</span>"
const markerProfanity = "<span style=\"background-color: rgb(255, 0, 0);\">%s</span>"

func EnrichTextWithMarkers(text string, parasiteMarkers []int, profanityMarkers []int) string {
	text = strings.TrimSpace(text)
	words := strings.Split(text, " ")
	for _, marker := range parasiteMarkers {
		words[marker] = fmt.Sprintf(markerParasite, words[marker])
	}

	for _, marker := range profanityMarkers {
		words[marker] = fmt.Sprintf(markerProfanity, words[marker])
	}
	return strings.Join(words, " ")
}
