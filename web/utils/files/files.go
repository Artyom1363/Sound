package files

import (
	"fmt"
	"os"
	"web/utils/generator"
)

func SaveToTextFile(data []byte) (string, error) {
	filePath := "fileserver/" + generator.GenString(10) + ".txt"
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		return "", fmt.Errorf("fail open: %v", err)
	}
	defer f.Close()
	_, err = f.Write(data)
	if err != nil {
		return "", fmt.Errorf("fail write: %v", err)
	}
	return filePath, nil
}

func SaveToAudioFile(data []byte) (string, error) {
	filePath := "fileserver/" + generator.GenString(10) + ".mp3"
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		return "", fmt.Errorf("fail open: %v", err)
	}
	defer f.Close()
	_, err = f.Write(data)
	if err != nil {
		return "", fmt.Errorf("fail write: %v", err)
	}
	return filePath, nil
}

func genTextFilePath() {

}

func readFromFile() {

}
