package cutter

import (
	ffmpeg "github.com/u2takey/ffmpeg-go"
	"log"
	"testing"
)

func TestRun(t *testing.T) {
	audio := ffmpeg.Input("/home/nikita/Sound/web/static/media/example.mp3").
		Filter("volume", ffmpeg.Args{"0.25", "enable='between(t,1,2)+between(t,3,4)'"})
	//beep := ffmpeg.Input("/home/nikita/Sound/web/static/media/duck.mp3").
	//	Filter("volume", ffmpeg.Args{"0", "enable='1-between(t,1,2)-between(t,3,4)'"})
	beep := ffmpeg.Input("/home/nikita/Sound/web/static/media/duck.mp3").
		Filter("adelay", ffmpeg.Args{"1000|1000"})
	err := ffmpeg.Filter([]*ffmpeg.Stream{audio, beep}, "amix", ffmpeg.Args{"inputs=2", "duration=first"}).
		Output("/home/nikita/Sound/web/static/media/example_out.mp3").
		OverWriteOutput().ErrorToStdOut().Run()
	if err != nil {
		log.Fatal(err.Error())
	}
}
