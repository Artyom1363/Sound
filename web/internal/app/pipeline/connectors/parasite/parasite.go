package parasite

import (
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
	url := config.ParasiteAPI + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("http get: %v", err)
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
