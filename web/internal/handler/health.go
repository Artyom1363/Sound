package handler

import (
	"io"
	"net/http"
	"time"
	"web/internal/config"
)

const (
	HealthStatusUnavailable = "unavailable"
	HealthStatusNotReady    = "not ready"
	HealthStatusOk          = "success"
)

func HealthParasite(w http.ResponseWriter, r *http.Request) {
	client := http.Client{Timeout: time.Second * 5}
	resp, err := client.Get(config.ParasiteAPIHealth)
	if err != nil {
		w.Write([]byte(HealthStatusUnavailable))
		return
	}

	rspBody, err := io.ReadAll(resp.Body)
	if err != nil {
		w.Write([]byte(HealthStatusNotReady))
		return
	}
	if string(rspBody) != "\"Model is ready\"" {
		w.Write([]byte(HealthStatusNotReady))
		return
	}

	w.Write([]byte(HealthStatusOk))
}

func HealthMezdo(w http.ResponseWriter, r *http.Request) {
	client := http.Client{Timeout: time.Second * 5}
	resp, err := client.Get(config.MezdoAPIHealth)
	if err != nil {
		w.Write([]byte(HealthStatusUnavailable))
		return
	}

	rspBody, err := io.ReadAll(resp.Body)
	if err != nil {
		w.Write([]byte(HealthStatusNotReady))
		return
	}
	if string(rspBody) != "\"Model is ready\"" {
		w.Write([]byte(HealthStatusNotReady))
		return
	}

	w.Write([]byte(HealthStatusOk))
}

func HealthCutter(w http.ResponseWriter, r *http.Request) {
	client := http.Client{Timeout: time.Second * 5}
	resp, err := client.Get(config.CutterAPIHealth)
	if err != nil {
		w.Write([]byte(HealthStatusUnavailable))
		return
	}

	rspBody, err := io.ReadAll(resp.Body)
	if err != nil {
		w.Write([]byte(HealthStatusNotReady))
		return
	}
	if string(rspBody) != "\"Service is ready\"" {
		w.Write([]byte(HealthStatusNotReady))
		return
	}

	w.Write([]byte(HealthStatusOk))
}

func HealthTranscribe(w http.ResponseWriter, r *http.Request) {
	client := http.Client{Timeout: time.Second * 5}
	resp, err := client.Get(config.TranscribeAPIHealth)
	if err != nil {
		w.Write([]byte(HealthStatusUnavailable))
		return
	}

	rspBody, err := io.ReadAll(resp.Body)
	if err != nil {
		w.Write([]byte(HealthStatusNotReady))
		return
	}
	if string(rspBody) != "true" {
		w.Write([]byte(HealthStatusNotReady))
		return
	}

	w.Write([]byte(HealthStatusOk))
}
