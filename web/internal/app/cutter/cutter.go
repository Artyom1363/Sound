package cutter

import (
	"fmt"
	_ "github.com/u2takey/ffmpeg-go"
	ffmpeg "github.com/u2takey/ffmpeg-go"
	"strings"
	"web/internal/app/connectors/transcribe"
)

func Run(inputPath string, transcription *transcribe.TranscribeText, badWordsMarkers []int, parasiteWordsMarkers []int) (string, error) {
	outputPath := getOutputPath(inputPath)

	if len(parasiteWordsMarkers) > 0 {
		err := ffmpeg.Input(inputPath).
			Filter("aselect", ffmpeg.Args{prepareCutFilterArgs(transcription.Words, parasiteWordsMarkers)}).
			Output(outputPath).
			OverWriteOutput().Run()
		if err != nil {
			return "", fmt.Errorf("fail to cut audio: %v", err)
		}
	}

	return outputPath, nil
}

func getOutputPath(inputAudioPath string) string {
	return strings.TrimSuffix(inputAudioPath, ".mp3") + "_cut.mp3"
}

func prepareCutFilterArgs(transWords []transcribe.SingleWorld, wordsInds []int) string {
	parts := make([]string, 0, len(wordsInds))
	for _, ind := range wordsInds {
		part := fmt.Sprintf("between(t,%f,%f)", transWords[ind].Start, transWords[ind].End)
		parts = append(parts, part)
	}
	return "1-" + strings.Join(parts, "-")
}
