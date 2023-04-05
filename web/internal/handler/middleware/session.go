package middleware

import (
	"math/rand"
	"net/http"
	"time"
	"web/internal/handler/config"
)

func Session(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if _, err := r.Cookie("session"); err != nil {
			cookie := &http.Cookie{
				Name:    "session",
				Domain:  config.Domain,
				Path:    "/",
				Expires: time.Now().Add(time.Hour * 24),
				Value:   RandStringRunes(20),
			}
			r.AddCookie(cookie)
			http.SetCookie(w, cookie)
		}
		h.ServeHTTP(w, r)
	})
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func RandStringRunes(n int) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = letterRunes[rand.Intn(len(letterRunes))]
	}
	return string(b)
}
