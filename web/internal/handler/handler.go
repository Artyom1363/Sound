package handler

import (
	"bytes"
	"crypto/md5"
	"encoding/json"
	"fmt"
	gojson "github.com/goccy/go-json"
	"html/template"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"
	"web/internal/app/markers"
	"web/internal/handler/config"
	"web/internal/handler/websocket"
)

func MeHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, it's me!"))
}

func Index(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/static/", http.StatusTemporaryRedirect)
}

func Upload(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Метод:", r.Method)
	if r.Method == "GET" {
		crutime := time.Now().Unix()
		h := md5.New()
		io.WriteString(h, strconv.FormatInt(crutime, 10))
		token := fmt.Sprintf("%x", h.Sum(nil))

		t, _ := template.ParseFiles("upload.gtpl")
		t.Execute(w, token)
	} else {
		r.ParseMultipartForm(32 << 20)
		file, handler, err := r.FormFile("uploadfile")
		if err != nil {
			fmt.Println(err)
			return
		}
		defer file.Close()
		//fmt.Fprintf(w, "%v", handler.Header)
		filePath := "./fileserver/" + handler.Filename
		f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0666)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer f.Close()
		io.Copy(f, file)

		//w.WriteHeader(http.StatusOK)
		w.Write([]byte("http://localhost:8000/fileserver/" + handler.Filename))
	}
}

func Process(w http.ResponseWriter, r *http.Request) {
	session, err := r.Cookie("session")
	if err != nil {
		log.Printf("fail to get session: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
	}

	fileLink := r.URL.Query().Get("audio")

	client := &http.Client{
		Timeout: time.Minute * 2,
	}
	// New multipart writer.
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	fw, err := writer.CreateFormFile("file", "audio.mp3")
	if err != nil {
		log.Printf("fail to create file form: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	file, err := os.Open("static/media/example.mp3")
	if err != nil {
		log.Printf("fail to open file: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	_, err = io.Copy(fw, file)
	if err != nil {
		log.Printf("fail to copy file: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	writer.Close()
	req, err := http.NewRequest(http.MethodPost, config.TranscribeModelAPITranscribe, bytes.NewReader(body.Bytes()))
	if err != nil {
		log.Printf("fail to get session: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	rsp, _ := client.Do(req)
	if rsp.StatusCode != http.StatusOK {
		log.Printf("Request failed with response code: %d", rsp.StatusCode)
		return
	}

	rspBody, err := io.ReadAll(rsp.Body)
	if err != nil {
		log.Printf("read resp model API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	type Resp struct {
		FileID int `json:"file_id"`
	}

	var resp Resp
	if err := json.Unmarshal(rspBody, &resp); err != nil {
		log.Printf("fail to unmarshal resp from parasite API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	go func() {
		timeout := time.After(5 * time.Minute)
		//pollInt := time.Second
		log.Printf("%d", resp.FileID)

		mess := ""
		for {
			select {
			case <-time.After(time.Second * 2):
				params := url.Values{}
				params.Add("file_id", strconv.Itoa(resp.FileID))

				// Create the URL with the parameters
				url := config.TranscribeModelAPIResultText + "?" + params.Encode()

				respFile, err := http.Get(url)
				if err != nil {
					log.Printf("fail to get result file: %v", err)
				}
				body, err := io.ReadAll(respFile.Body)
				if err != nil {
					log.Printf("read resp from parasite API: %v", err)
					w.WriteHeader(http.StatusInternalServerError)
					return
				}

				if string(body) == "\"file not ready!\"" {
					log.Printf("not ready")
					break
				}

				log.Println("The end!")
				mess = fmt.Sprintf(`{"status":"success", "source":"process", "audio":"%s", "resultID": %d }`, fileLink, resp.FileID)
				websocket.SendMessage(session.Value, mess)
				return
			case <-timeout:
				log.Println("There's no more time to this. Exiting!")
				mess = fmt.Sprintf(`{"status":"error", "source":"process", "error":"timeout"}`)
				websocket.SendMessage(session.Value, mess)
				return
				//
				//default:
				//	fmt.Println("still waiting")
			}
			//time.Sleep(pollInt)
		}
	}()

	w.WriteHeader(http.StatusOK)
}

func GetText(w http.ResponseWriter, r *http.Request) {
	//var textBytes []byte
	text := r.URL.Query().Get("text")

	params := url.Values{}
	params.Add("request", text)

	// Create the URL with the parameters
	url := config.ParasiteModelAPI + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		log.Printf("get parasite API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("read resp from parasite API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	var parasiteWords []int
	if err := gojson.Unmarshal(body, &parasiteWords); err != nil {
		log.Printf("fail to unmarshal resp from parasite API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	enrichedText := markers.EnrichTextWithMarkers(text, parasiteWords, []int{})

	w.WriteHeader(http.StatusOK)
	//w.Write([]byte("Hello from backend. I am <span style=\"background-color: rgb(255, 255, 0);\">golang</span> developer!"))
	w.Write([]byte(enrichedText))
}

func GetResultFile(w http.ResponseWriter, r *http.Request) {
	//resultID := r.URL.Query().Get("resultID")
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

func getResultText(id string) (*TranscribeText, error) {
	params := url.Values{}
	params.Add("file_id", id)

	// Create the URL with the parameters
	url := config.TranscribeModelAPIResultText + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("http get: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read resp: %v", err)
	}
	//body = []byte("{\"text\": \" Столько лебучая, блять, дёргаешь! Хуй свой дёрний шаг, блять! Предокранительность невеста. Запомните, товарищи дебилы, блять!\"}")
	//bodyStr := strings.Trim(string(body), "\"")
	bodyStr, err := strconv.Unquote(string(body))

	if bodyStr == "file not ready!" {
		return nil, fmt.Errorf("file not ready")
	}

	//bodyStr := fmt.Sprintf(string(body))
	var text TranscribeText
	if err := gojson.Unmarshal([]byte(bodyStr), &text); err != nil {
		return nil, fmt.Errorf("unmarshal resp: %v", err)
	}

	return &text, nil
}

func parseProfanityMarkers(text *TranscribeText) []int {
	ids := make([]int, 0)
	for ind, word := range text.Words {
		if word.IsProfanity {
			ids = append(ids, ind)
		}
	}
	return ids
}

func GetResultText(w http.ResponseWriter, r *http.Request) {
	resultID := r.URL.Query().Get("resultID")

	text, err := getResultText(resultID)
	if err != nil {
		log.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	profanityIds := parseProfanityMarkers(text)

	enrichedText := markers.EnrichTextWithMarkers(text.Text, []int{}, profanityIds)

	w.Write([]byte(enrichedText))
	w.WriteHeader(http.StatusOK)
}
