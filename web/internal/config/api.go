package config

const ParasiteAddr = "http://91.142.74.200:8000"
const TranscribeAddr = "http://95.64.151.158:8000"
const MezdoAddr = "http://62.113.117.121:8001"

const (
	ParasiteAPIHealth = ParasiteAddr + "/health"
	ParasiteAPI       = ParasiteAddr + "/predict/"
)

const (
	TranscribeAPIHealth     = TranscribeAddr + "/ready/"
	TranscribeAPI           = TranscribeAddr + "/transcribe/"
	TranscribeAPIResultText = TranscribeAddr + "/get_text_by_id"
	TranscribeAPIResultFile = TranscribeAddr + "/get_file_by_id"
)

const (
	MezdoApi = MezdoAddr + "/predict/"
)
