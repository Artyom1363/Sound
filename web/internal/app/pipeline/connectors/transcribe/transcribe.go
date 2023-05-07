package transcribe

import (
	"bytes"
	"encoding/json"
	"fmt"
	gojson "github.com/goccy/go-json"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
	"web/config"
	"web/utils/files"
)

type Resp struct {
	FileID int `json:"file_id"`
}

func Run(filePath string) (string, string, *TranscribeText, []int, int, error) {
	client := &http.Client{
		Timeout: time.Minute * 2,
	}
	// New multipart writer.
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	fileName, found := strings.CutPrefix(filePath, "fileserver/")
	if !found {
		return "", "", nil, nil, 0, fmt.Errorf("fail to get filename: %s", filePath)
	}

	fw, err := writer.CreateFormFile("file", fileName)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to create file form: %v", err)
	}
	file, err := os.Open(filePath)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to open file: %v", err)
	}
	_, err = io.Copy(fw, file)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to copy file: %v", err)
	}
	writer.Close()

	req, err := http.NewRequest(http.MethodPost, config.TranscribeAPI, bytes.NewReader(body.Bytes()))
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to create request: %v", err)
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	rsp, err := client.Do(req)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to execute request: %v", err)
	}

	if rsp.StatusCode != http.StatusOK {
		return "", "", nil, nil, 0, fmt.Errorf("request failed with response code: %d", rsp.StatusCode)
	}

	rspBody, err := io.ReadAll(rsp.Body)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to read response: %v", err)
	}

	var resp Resp
	if err = json.Unmarshal(rspBody, &resp); err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail to unmarshal resp: %v", err)
	}

	err = waitResult(resp.FileID)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail wait result: %v", err)
	}

	textFilePath, rawText, err := getResultTextFile(resp.FileID)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail get result text file: %v", err)
	}

	audioFilePath, err := getResultAudioFile(resp.FileID)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail get result audio file: %v", err)
	}

	transcribeText, err := parseText(rawText)
	if err != nil {
		return "", "", nil, nil, 0, fmt.Errorf("fail parse text: %v", err)
	}

	badWordsIds := parseBadWords(transcribeText)

	return textFilePath, audioFilePath, transcribeText, badWordsIds, resp.FileID, nil
}

func waitResult(resultID int) error {
	timeout := time.After(5 * time.Minute)
	pollInt := time.Second

	for {
		select {
		case <-time.After(time.Second * 3):
			ok, err := tryGetResult(resultID)
			if err != nil {
				return fmt.Errorf("%v", err)
			}
			if ok {
				return nil
			}
			log.Printf("still wait")
		case <-timeout:
			return fmt.Errorf("timeout")
		}
		time.Sleep(pollInt)
	}
}

func tryGetResult(resultID int) (bool, error) {
	params := url.Values{}
	params.Add("file_id", strconv.Itoa(resultID))

	// Create the URL with the parameters
	url := config.TranscribeAPIResultText + "?" + params.Encode()

	respFile, err := http.Get(url)
	if err != nil {
		return false, fmt.Errorf("fail get: %v", err)
	}
	body, err := io.ReadAll(respFile.Body)
	if err != nil {
		return false, fmt.Errorf("fail to read resp: %v", err)
	}
	if string(body) == "\"file not ready!\"" {
		return false, nil
	}
	return true, nil
}

func getResultTextFile(resultID int) (string, string, error) {
	params := url.Values{}
	params.Add("file_id", strconv.Itoa(resultID))

	// Create the URL with the parameters
	url := config.TranscribeAPIResultText + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return "", "", fmt.Errorf("http get: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", fmt.Errorf("read resp: %v", err)
	}

	bodyStr, err := strconv.Unquote(string(body))
	if err != nil {
		return "", "", fmt.Errorf("fail unquote: %v", err)
	}

	if bodyStr == "file not ready!" {
		return "", "", fmt.Errorf("file not ready")
	}

	filePath, err := files.SaveToTextFile([]byte(bodyStr))
	if err != nil {
		return "", "", fmt.Errorf("save file: %v", err)
	}

	return filePath, bodyStr, nil

	//bodyStr := fmt.Sprintf(string(body))
	//var text TranscribeText
	//if err := gojson.Unmarshal([]byte(bodyStr), &text); err != nil {
	//	return nil, fmt.Errorf("unmarshal resp: %v", err)
	//}
}

func getResultAudioFile(resultID int) (string, error) {
	params := url.Values{}
	params.Add("file_id", strconv.Itoa(resultID))

	// Create the URL with the parameters
	url := config.TranscribeAPIResultFile + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return "", fmt.Errorf("http get: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("read resp: %v", err)
	}

	filePath, err := files.SaveToAudioFile(body)
	if err != nil {
		return "", fmt.Errorf("save file: %v", err)
	}

	return filePath, nil

}

type SingleWorld struct {
	Word        string  `json:"word"`
	Start       float64 `json:"start"`
	End         float64 `json:"end"`
	Probability float64 `json:"probability"`
	Tokens      []int   `json:"tokens"`
	IsProfanity bool    `json:"is_profanity"`
}

type TranscribeText struct {
	Text  string        `json:"text"`
	Words []SingleWorld `json:"words"`
}

func parseText(rawText string) (*TranscribeText, error) {
	//bodyStr := fmt.Sprintf(string(body))
	var text TranscribeText
	if err := gojson.Unmarshal([]byte(rawText), &text); err != nil {
		return nil, fmt.Errorf("unmarshal resp: %v", err)
	}
	text.Text = strings.TrimSpace(text.Text)

	return &text, nil
}

func parseBadWords(text *TranscribeText) []int {
	ids := make([]int, 0)
	for ind, word := range text.Words {
		if word.IsProfanity {
			ids = append(ids, ind)
		}
	}
	return ids
}
