package cutter

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strings"
	"time"
	"web/internal/app/audiomarkers"
	"web/internal/app/files"
	"web/internal/config"
)

type CutterRequest struct {
	Redundants []CutterItem `json:"redundants"`
}

type CutterItem struct {
	Start  float64 `json:"start"`
	End    float64 `json:"end"`
	Filler string  `json:"filler"`
}

func Run(filePath string, markers audiomarkers.AudioMarkers) (string, error) {
	client := &http.Client{
		Timeout: time.Minute * 2,
	}
	// New multipart writer.
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	if err := prepareFile(writer, filePath); err != nil {
		return "", err
	}
	if err := prepareMarkers(writer, markers); err != nil {
		return "", err
	}
	writer.Close()

	req, err := http.NewRequest(http.MethodPost, config.CutterAPI, bytes.NewReader(body.Bytes()))
	if err != nil {
		return "", fmt.Errorf("fail to create request: %v", err)
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	rsp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("fail to execute request: %v", err)
	}

	if rsp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("request failed with response code: %d", rsp.StatusCode)
	}

	rspBody, err := io.ReadAll(rsp.Body)
	if err != nil {
		return "", fmt.Errorf("read resp: %v", err)
	}

	resultFilePath, err := files.SaveToAudioFile(rspBody)
	if err != nil {
		return "", fmt.Errorf("save file: %v", err)
	}

	return resultFilePath, nil
}

func prepareFile(writer *multipart.Writer, filePath string) error {
	fileName, found := strings.CutPrefix(filePath, "fileserver/")
	if !found {
		return fmt.Errorf("fail to get filename: %s", filePath)
	}

	fw, err := writer.CreateFormFile("request", fileName)
	if err != nil {
		return fmt.Errorf("fail to create file form: %v", err)
	}
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("fail to open file: %v", err)
	}
	_, err = io.Copy(fw, file)
	if err != nil {
		return fmt.Errorf("fail to copy file: %v", err)
	}
	return nil
}

func prepareMarkers(writer *multipart.Writer, markers audiomarkers.AudioMarkers) error {
	req := CutterRequest{}
	for _, marker := range markers {
		filler := "empty"
		if marker.Type == audiomarkers.TypeBad {
			filler = "bleep"
		}
		req.Redundants = append(req.Redundants, CutterItem{
			Start:  marker.Start,
			End:    marker.End,
			Filler: filler,
		})
	}

	markersBytes, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("fail marshal: %v", err)
	}

	fw, err := writer.CreateFormFile("request", "config.json")
	if err != nil {
		return fmt.Errorf("fail to create file form: %v", err)
	}

	//file, err := os.Open(filePath)
	//if err != nil {
	//	return "", fmt.Errorf("fail to open file: %v", err)
	//}

	_, err = fw.Write(markersBytes)
	//_, err = io.Copy(fw, markersBytes)
	if err != nil {
		return fmt.Errorf("fail to copy file: %v", err)
	}
	return nil
}
