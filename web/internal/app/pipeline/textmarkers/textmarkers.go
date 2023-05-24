package textmarkers

import (
	"fmt"
	"strings"
	"web/utils/files"
)

const parasite = "parasite"
const profanity = "profanity"

const markerParasite = "<span style=\"background-color: rgb(255, 255, 0);\" id=\"marker-%d\">%s</span>"
const markerProfanity = "<span style=\"background-color: rgb(255, 0, 0);\" id=\"marker-%d\">%s</span>"

type marker struct {
	t   string
	ind int
}

func EnrichTextWithMarkers(text string, parasiteMarkers []int, profanityMarkers []int) string {
	text = strings.TrimSpace(text)
	words := strings.Split(text, " ")
	//for _, word := range words {
	//	fmt.Printf("'%s', ", word)
	//}

	markers := make([]marker, 0, len(parasiteMarkers)+len(profanityMarkers))
	for _, m := range parasiteMarkers {
		markers = append(markers, marker{t: parasite, ind: m})
	}
	for _, m := range profanityMarkers {
		markers = append(markers, marker{t: profanity, ind: m})
	}

	for i, m := range markers {
		if len(words) > m.ind {
			switch m.t {
			case profanity:
				words[m.ind] = fmt.Sprintf(markerParasite, i, words[m.ind])
			case parasite:
				words[m.ind] = fmt.Sprintf(markerParasite, i, words[m.ind])

			}
		}
	}
	return strings.Join(words, " ")
}

func Run(text string, parasiteMarkers []int, profanityMarkers []int) (string, error) {
	enrichedText := EnrichTextWithMarkers(text, parasiteMarkers, profanityMarkers)
	return files.SaveToTextFile([]byte(enrichedText))
}
