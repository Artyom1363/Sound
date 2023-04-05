package internal

import (
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"time"
	"web/internal/handler"
	"web/internal/handler/config"
	"web/internal/handler/middleware"
	"web/internal/handler/websocket"
)

func InitRouter() {
	websocket.InitStorage()

	r := mux.NewRouter()
	r.HandleFunc("/me", handler.MeHandler)
	r.HandleFunc("/socket", websocket.SocketReaderCreate)
	r.HandleFunc("/upload", handler.Upload)
	r.HandleFunc("/process", handler.Process)
	r.HandleFunc("/getText", handler.GetText)

	r.Use(middleware.Session)

	//r.Handle("/", http.FileServer(http.Dir("./static")))
	r.PathPrefix("/fileserver/").Handler(http.StripPrefix("/fileserver/", http.FileServer(http.Dir("./fileserver"))))
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.PathPrefix("").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.HandleFunc("/articles", ArticlesHandler)

	srv := &http.Server{
		Handler: r,
		Addr:    config.Domain + ":" + config.Port,
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Fatal(srv.ListenAndServe())
}
