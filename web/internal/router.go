package internal

import (
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"time"
	"web/internal/config"
	"web/internal/handler"
	"web/internal/handler/middleware"
	"web/internal/handler/websocket"
)

func InitRouter() {
	websocket.InitStorage()

	r := mux.NewRouter()
	r.HandleFunc("/me", handler.MeHandler)
	r.HandleFunc("/", handler.Index)
	r.HandleFunc("/socket", websocket.SocketReaderCreate)
	r.HandleFunc("/getText", handler.GetText)
	r.HandleFunc("/getResultFile", handler.GetResultFile)
	//r.HandleFunc("/getResultText", handler.GetResultText)
	r.HandleFunc("/health/parasite", handler.HealthParasite)
	r.HandleFunc("/health/transcribe", handler.HealthTranscribe)

	r.HandleFunc("/upload", handler.Upload)
	r.HandleFunc("/process", handler.Process)

	r.Use(middleware.Session)

	//r.Handle("/", http.FileServer(http.Dir("./static")))
	r.PathPrefix("/fileserver/").Handler(http.StripPrefix("/fileserver/", http.FileServer(http.Dir("./fileserver"))))
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.PathPrefix("").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.HandleFunc("/articles", ArticlesHandler)

	srv := &http.Server{
		Handler: r,
		Addr:    config.BackendAddr,
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 5 * time.Minute,
		ReadTimeout:  5 * time.Minute,
	}

	log.Fatal(srv.ListenAndServe())
}
