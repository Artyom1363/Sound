package audiomarkers

import (
	"fmt"
	"github.com/goccy/go-json"
	"web/internal/app/connectors/mezdo"
	"web/internal/app/connectors/transcribe"
	"web/internal/app/files"
)

type AudioMarkers []AudioMarker

type AudioMarker struct {
	Start float64
	End   float64
	Type  string
}

const (
	TypeParasite = "parasite"
	TypeBad      = "bad"
	TypeMezdo    = "mezdo"
)

func Run(transcription *transcribe.TranscribeText, parasiteMarkers []int, badMarkers []int, mezdoMarkers mezdo.MezdoItems) (AudioMarkers, string, error) {
	audioMarkers := make(AudioMarkers, 0, len(parasiteMarkers)+len(badMarkers)+len(mezdoMarkers))
	for _, marker := range parasiteMarkers {
		audioMarkers = append(audioMarkers, AudioMarker{
			Start: transcription.Words[marker].Start,
			End:   transcription.Words[marker].End,
			Type:  TypeParasite,
		})
	}

	for _, marker := range badMarkers {
		audioMarkers = append(audioMarkers, AudioMarker{
			Start: transcription.Words[marker].Start,
			End:   transcription.Words[marker].End,
			Type:  TypeBad,
		})
	}

	for _, marker := range mezdoMarkers {
		audioMarkers = append(audioMarkers, AudioMarker{
			Start: marker.Start,
			End:   marker.End,
			Type:  TypeMezdo,
		})
	}

	audioMarkersBytes, err := json.Marshal(audioMarkers)
	if err != nil {
		return nil, "", fmt.Errorf("fail unmarshal: %v", err)
	}
	filePath, err := files.SaveToTextFile(audioMarkersBytes)
	return audioMarkers, filePath, err
}
