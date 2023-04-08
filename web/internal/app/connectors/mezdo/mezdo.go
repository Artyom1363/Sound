package mezdo

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"web/internal/app/files"
	"web/internal/config"
)

func Run(resultID int) (string, error) {

	params := url.Values{}
	params.Add("request", strconv.Itoa(resultID))

	// Create the URL with the parameters
	url := config.MezdoApi + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return "", fmt.Errorf("http get: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("read body: %v", err)
	}
	unqBody, err := strconv.Unquote(string(body))
	if err != nil {
		return "", fmt.Errorf("fail unquote: %v", err)
	}

	filePath, err := files.SaveToTextFile([]byte(unqBody))
	if err != nil {
		return "", fmt.Errorf("fail save to file: %v", err)
	}

	return filePath, nil
}
