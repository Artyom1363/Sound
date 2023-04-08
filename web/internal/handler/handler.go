package handler

import (
	"crypto/md5"
	"fmt"
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
	"web/internal/app/markers"
	"web/internal/app/pipeline"
	"web/internal/config"
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

		w.Write([]byte("/fileserver/" + handler.Filename))
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
	enrichedText := markers.EnrichTextWithMarkers(text, parasiteWords, []int{})

	w.WriteHeader(http.StatusOK)
	//w.Write([]byte("Hello from backend. I am <span style=\"background-color: rgb(255, 255, 0);\">golang</span> developer!"))
	w.Write([]byte(enrichedText))
}

func GetResultFile(w http.ResponseWriter, r *http.Request) {
	//resultID := r.URL.Query().Get("resultID")
}

//func GetResultText(w http.ResponseWriter, r *http.Request) {
//	resultID := r.URL.Query().Get("resultID")
//
//	text, err := getResultText(resultID)
//	if err != nil {
//		log.Println(err)
//		w.WriteHeader(http.StatusInternalServerError)
//		return
//	}
//
//	profanityIds := parseProfanityMarkers(text)
//
//	enrichedText := markers.EnrichTextWithMarkers(text.Text, []int{}, profanityIds)
//
//	w.Write([]byte(enrichedText))
//	w.WriteHeader(http.StatusOK)
//}
