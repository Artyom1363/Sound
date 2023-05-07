package pipeline

import (
	"fmt"
	"log"
	"web/internal/app/pipeline/audiomarkers"
	"web/internal/app/pipeline/connectors/cutter"
	"web/internal/app/pipeline/connectors/mezdo"
	"web/internal/app/pipeline/connectors/parasite"
	"web/internal/app/pipeline/connectors/transcribe"
	"web/internal/app/pipeline/textmarkers"
	"web/internal/handler/websocket"
)

type Pipeline struct {
	userSession         string
	sourceAudioFilePath string

	transcribeResultID int

	parasiteWordsInds []int
	badWordsInds      []int
	mezdoSegments     mezdo.MezdoItems
	audioMarkers      audiomarkers.AudioMarkers

	transcription *transcribe.TranscribeText

	resultAudioFilePath    string
	resultCutAudioFilePath string
	resultTextFilePath     string
	resultAudioMarkersPath string

	checker *Checker
}

func New(session string, srcFilePath string) *Pipeline {
	return &Pipeline{
		sourceAudioFilePath: srcFilePath,
		userSession:         session,
	}
}

func (p *Pipeline) Start() {
	var err error
	checker := NewChecker(p.userSession)

	if p.resultTextFilePath, p.resultAudioFilePath, p.transcription, p.badWordsInds, p.transcribeResultID, err =
		transcribe.Run(p.sourceAudioFilePath); !checker.processErr(err, "transpile") {
		return
	}

	if p.parasiteWordsInds, err =
		parasite.Run(p.transcription.Text); !checker.processErr(err, "parasite") {
		return
	}

	if p.mezdoSegments, err =
		mezdo.Run(p.transcribeResultID); !checker.processErr(err, "mezdo") {
		return
	}

	if p.resultTextFilePath, err =
		textmarkers.Run(p.transcription.Text, p.parasiteWordsInds, p.badWordsInds); !checker.processErr(err, "textmarkers") {
		return
	}

	if p.audioMarkers, p.resultAudioMarkersPath, err =
		audiomarkers.Run(p.transcription, p.parasiteWordsInds, p.badWordsInds, p.mezdoSegments); !checker.processErr(err, "audiomarkers") {
		return
	}

	//if p.resultCutAudioFilePath, err =
	//	cutter.Run(p.resultAudioFilePath, p.transcription, p.badWordsInds, p.parasiteWordsInds); !checker.processErr(err, "cutter") {
	//	return
	//}
	if p.resultCutAudioFilePath, err =
		cutter.Run(p.resultAudioFilePath, p.audioMarkers); !checker.processErr(err, "cutter") {
		return
	}

	mess := fmt.Sprintf(
		`{"status":"success", "source":"process", "audio":"%s", "cutAudio":"%s", "text":"%s", "audioMarkers":"%s"}`,
		p.sourceAudioFilePath, p.resultCutAudioFilePath, p.resultTextFilePath, p.resultAudioMarkersPath)
	websocket.SendMessage(p.userSession, mess)
	log.Printf("pipline finished")
}

type Checker struct {
	userSession string
}

func NewChecker(us string) *Checker {
	return &Checker{
		userSession: us,
	}
}

func (c *Checker) processErr(err error, module string) bool {
	if err != nil {
		log.Printf("module: %v", err)
		mess := fmt.Sprintf(`{"status":"error", "source":"process", "module":"%s", "error":"%s"}`, module, err)
		websocket.SendMessage(c.userSession, mess)
		return false
	}
	mess := fmt.Sprintf(`{"status":"info", "source":"process", "module":"%s"}`, module)
	websocket.SendMessage(c.userSession, mess)
	return true
}
