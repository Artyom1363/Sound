package cutter

import (
	"fmt"
	_ "github.com/u2takey/ffmpeg-go"
	ffmpeg "github.com/u2takey/ffmpeg-go"
	"strings"
	"web/internal/app/connectors/transcribe"
)

func Run(inputPath string, transcription *transcribe.TranscribeText, badWordsMarkers []int, parasiteWordsMarkers []int) (string, error) {
	resultPath, err := processBadWords(inputPath, transcription, badWordsMarkers)
	if err != nil {
		return "", err
	}

	resultPath, err = processParasiteWords(resultPath, transcription, parasiteWordsMarkers)
	if err != nil {
		return "", err
	}

	return resultPath, nil
}

func processParasiteWords(inputPath string, transcription *transcribe.TranscribeText, parasiteWordsMarkers []int) (string, error) {
	if len(parasiteWordsMarkers) == 0 {
		return inputPath, nil
	}
	outputPath := getOutputPath(inputPath)
	err := ffmpeg.Input(inputPath).
		Filter("aselect", ffmpeg.Args{prepareCutFilterArgs(transcription.Words, parasiteWordsMarkers)}).
		Output(outputPath).
		OverWriteOutput().Run()
	if err != nil {
		return "", fmt.Errorf("fail to cut audio: %v", err)
	}
	return outputPath, nil
}

func processBadWords(inputPath string, transcription *transcribe.TranscribeText, badWordsMarkers []int) (string, error) {
	if len(badWordsMarkers) == 0 {
		return inputPath, nil
	}
	outputPath := getOutputBadPath(inputPath)

	audio := ffmpeg.Input(inputPath).
		Filter("volume", ffmpeg.Args{"0.25", "enable='between(t,1,2)+between(t,3,4)'"})
	var beeps []*ffmpeg.Stream
	for _, ind := range badWordsMarkers {
		delay := transcription.Words[ind].Start * 1000
		beeps = append(beeps,
			ffmpeg.Input("./static/media/duck.mp3").
				Filter("adelay", ffmpeg.Args{fmt.Sprintf("%f|%f", delay, delay)}),
		)
	}
	err := ffmpeg.Filter(append([]*ffmpeg.Stream{audio}, beeps...), "amix", ffmpeg.Args{fmt.Sprintf("inputs=%d", len(badWordsMarkers)+1), "duration=first"}).
		Output(outputPath).
		OverWriteOutput().ErrorToStdOut().Run()
	if err != nil {
		return "", err
	}

	return outputPath, nil
}

func getOutputPath(inputAudioPath string) string {
	return strings.TrimSuffix(inputAudioPath, ".mp3") + "_cut.mp3"
}

func getOutputBadPath(inputAudioPath string) string {
	return strings.TrimSuffix(inputAudioPath, ".mp3") + "_bad.mp3"
}

func prepareCutFilterArgs(transWords []transcribe.SingleWorld, wordsInds []int) string {
	parts := make([]string, 0, len(wordsInds))
	for _, ind := range wordsInds {
		part := fmt.Sprintf("between(t,%f,%f)", transWords[ind].Start, transWords[ind].End)
		parts = append(parts, part)
	}
	return "1-" + strings.Join(parts, "-")
}
