package handler

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"github.com/cassava/lackey/audio/mp3"
	gojson "github.com/goccy/go-json"
	"html/template"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
	"web/config"
	"web/internal/app/pipeline"
	"web/internal/app/pipeline/audiomarkers"
	"web/internal/app/pipeline/connectors/cutter"
	"web/internal/app/pipeline/textmarkers"
	"web/utils/generator"
)

const MaxAudioDuration = time.Minute * 3

func MeHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, it's me!"))
}

func Index(w http.ResponseWriter, r *http.Request) {
	//http.Redirect(w, r, "/static/", http.StatusTemporaryRedirect)
	http.ServeFile(w, r, "static/index.html")
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
		file, _, err := r.FormFile("uploadfile")
		if err != nil {
			fmt.Println(err)
			return
		}
		defer file.Close()
		//fmt.Fprintf(w, "%v", handler.Header)
		filePath := "./fileserver/" + generator.GenString(8) + ".mp3"
		f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0666)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer f.Close()
		io.Copy(f, file)

		meta, err := mp3.ReadMetadata(filePath)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte(fmt.Sprintf("Неверный формат файла. Загружайте только mp3!")))
			return
		}
		if meta.Length() > MaxAudioDuration {
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte(fmt.Sprintf("Лимит продолжительности аудио: 3 минуты. "+
				"Продолжительность загруженного файла: %f минут", meta.Length().Minutes(),
			)))
			return
		}
		log.Printf("Audio duration: %f minutes", meta.Length().Minutes())

		w.Write([]byte(strings.TrimLeft(filePath, ".")))
	}
}

func Process(w http.ResponseWriter, r *http.Request) {
	session, err := r.Cookie("session")
	if err != nil {
		log.Printf("fail to get session: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
	}

	fileLink := r.URL.Query().Get("audio")
	filePath := strings.Trim(fileLink, "/")

	worker := pipeline.New(session.Value, filePath)
	go worker.Start()

	w.WriteHeader(http.StatusOK)
}

func Render(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		log.Printf("read body: %v", err)
	}

	type Req struct {
		Filepath string
		Markers  audiomarkers.AudioMarkers
	}

	var req Req
	if err := json.Unmarshal(body, &req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		log.Printf("unmarshal body: %v", err)
	}

	resultPath, err := cutter.Run(req.Filepath, req.Markers)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		log.Printf("cutter: %v", err)
	}

	w.Write([]byte(resultPath))
}

func GetText(w http.ResponseWriter, r *http.Request) {
	//var textBytes []byte
	text := r.URL.Query().Get("text")

	params := url.Values{}
	params.Add("request", text)

	// Create the URL with the parameters
	url := config.ParasiteAPI + "?" + params.Encode()

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
	enrichedText := textmarkers.EnrichTextWithMarkers(text, parasiteWords, []int{})

	w.WriteHeader(http.StatusOK)
	//w.Write([]byte("Hello from backend. I am <span style=\"background-color: rgb(255, 255, 0);\">golang</span> developer!"))
	w.Write([]byte(enrichedText))
}

func GetResultFile(w http.ResponseWriter, r *http.Request) {
	//resultID := r.URL.Query().Get("resultID")
}
