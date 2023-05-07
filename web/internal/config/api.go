package config

// const ParasiteAddr = "http://195.133.60.176:8000"
const ParasiteAddr = "http://95.64.151.158:8080"
const TranscribeAddr = "http://95.64.151.158:8000"
const MezdoAddr = "http://195.133.60.176:8001"
const CutterAddr = "http://195.133.60.176:8002"

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
	MezdoAPIHealth = MezdoAddr + "/health"
	MezdoApi       = MezdoAddr + "/predict/"
)

const (
	CutterAPIHealth = CutterAddr + "/health"
	CutterAPI       = CutterAddr + "/cut"
)
