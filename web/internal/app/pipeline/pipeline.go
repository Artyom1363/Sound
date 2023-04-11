package pipeline

import (
	"fmt"
	"log"
	"web/internal/app/connectors/mezdo"
	"web/internal/app/connectors/parasite"
	"web/internal/app/connectors/transcribe"
	"web/internal/app/cutter"
	"web/internal/app/files"
	"web/internal/app/markers"
	"web/internal/handler/websocket"
)

type Pipeline struct {
	userSession         string
	sourceAudioFilePath string

	transcribeResultID int

	parasiteWordsInds []int
	badWordsInds      []int

	transcription *transcribe.TranscribeText

	resultAudioFilePath    string
	resultCutAudioFilePath string
	resultTextFilePath     string
	resultAudioMarkers     string
}

func New(session string, srcFilePath string) *Pipeline {
	return &Pipeline{
		userSession:         session,
		sourceAudioFilePath: srcFilePath,
	}
}

func (p *Pipeline) Start() {
	var err error
	p.resultTextFilePath, p.resultAudioFilePath, p.transcription, p.badWordsInds, p.transcribeResultID, err = transcribe.Run(p.sourceAudioFilePath)
	if err != nil {
		log.Printf("transpile: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "error":"%s"}`, err)
		websocket.SendMessage(p.userSession, mess)
		return
	}

	p.parasiteWordsInds, err = parasite.Run(p.transcription.Text)
	if err != nil {
		log.Printf("parasite: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "error":"%s"}`, err)
		websocket.SendMessage(p.userSession, mess)
		return
	}

	p.resultAudioMarkers, err = mezdo.Run(p.transcribeResultID)
	if err != nil {
		log.Printf("mezdo: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "error":"%s"}`, err)
		websocket.SendMessage(p.userSession, mess)
		return
	}

	p.transcription.Text = markers.EnrichTextWithMarkers(p.transcription.Text, p.parasiteWordsInds, p.badWordsInds)
	p.resultTextFilePath, err = files.SaveToTextFile([]byte(p.transcription.Text))
	if err != nil {
		log.Printf("save result: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "error":"%s"}`, err)
		websocket.SendMessage(p.userSession, mess)
		return
	}

	p.resultCutAudioFilePath, err = cutter.Run(p.resultAudioFilePath, p.transcription, p.badWordsInds, p.parasiteWordsInds)
	if err != nil {
		log.Printf("cut audio: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "error":"%s"}`, err)
		websocket.SendMessage(p.userSession, mess)
		return
	}

	mess := fmt.Sprintf(`{"status":"success", "source":"process", "audio":"%s", "cutAudio":"%s", "text":"%s", "audioMarkers":"%s"}`, p.resultAudioFilePath, p.resultCutAudioFilePath, p.resultTextFilePath, p.resultAudioMarkers)
	websocket.SendMessage(p.userSession, mess)
	log.Printf("pipline finished")
}
