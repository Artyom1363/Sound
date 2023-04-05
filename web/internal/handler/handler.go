package handler

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
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

	go func() {
		time.Sleep(time.Second * 2)
		mess := fmt.Sprintf(`{"status":"success", "source":"process", "audio":"%s"}`, fileLink)
		websocket.SendMessage(session.Value, mess)
	}()

	w.WriteHeader(http.StatusOK)
}

const parasiteModelAPI = "http://91.142.74.200:8000/predict/"

func GetText(w http.ResponseWriter, r *http.Request) {
	//var textBytes []byte
	text := r.URL.Query().Get("text")

	params := url.Values{}
	params.Add("request", text)

	// Create the URL with the parameters
	url := parasiteModelAPI + "?" + params.Encode()

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
	if err := json.Unmarshal(body, &parasiteWords); err != nil {
		log.Printf("fail to unmarshal resp from parasite API: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	enrichedText := enrichTextWithMarkers(text, parasiteWords)

	w.WriteHeader(http.StatusOK)
	//w.Write([]byte("Hello from backend. I am <span style=\"background-color: rgb(255, 255, 0);\">golang</span> developer!"))
	w.Write([]byte(enrichedText))
}

const markerParasite = "<span style=\"background-color: rgb(255, 255, 0);\">%s</span>"

func enrichTextWithMarkers(text string, parasiteMarkers []int) string {
	words := strings.Split(text, " ")
	for _, marker := range parasiteMarkers {
		words[marker] = fmt.Sprintf(markerParasite, words[marker])
	}
	return strings.Join(words, " ")
}
