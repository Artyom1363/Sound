package parasite

import (
	"bytes"
	"fmt"
	gojson "github.com/goccy/go-json"
	"io"
	"net/http"
	"net/url"
	"web/config"
)

func Run(text string) ([]int, error) {
	//var textBytes []byte

	params := url.Values{}
	params.Add("request", text)

	// Create the URL with the parameters
	//url := config.ParasiteAPI + "?" + params.Encode()

	req := fmt.Sprintf(`{"text":"%s"}`, text)
	reqReader := bytes.NewReader([]byte(req))

	resp, err := http.Post(config.ParasiteAPI, "application/json", reqReader)
	if err != nil {
		return nil, fmt.Errorf("http post: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body: %v", err)
	}

	var parasiteWords []int
	if err := gojson.Unmarshal(body, &parasiteWords); err != nil {
		return nil, fmt.Errorf("unmarshal parasiteWords: %v", err)
	}

	return parasiteWords, nil
}
