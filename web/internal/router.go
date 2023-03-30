package internal

import (
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"time"
	"web/internal/handler"
)

func InitRouter() {
	r := mux.NewRouter()
	r.HandleFunc("/me", handler.MeHandler)
	r.HandleFunc("/upload", handler.Upload)
	//r.Handle("/", http.FileServer(http.Dir("./static")))
	r.PathPrefix("/fileserver/").Handler(http.StripPrefix("/fileserver/", http.FileServer(http.Dir("./fileserver"))))
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.PathPrefix("").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	//r.HandleFunc("/articles", ArticlesHandler)

	srv := &http.Server{
		Handler: r,
		Addr:    "127.0.0.1:8000",
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Fatal(srv.ListenAndServe())
}
