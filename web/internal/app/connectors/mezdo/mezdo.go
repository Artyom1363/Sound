package mezdo

import (
	"fmt"
	"github.com/goccy/go-json"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"web/internal/config"
)

type MezdoItems []MezdoItem

type MezdoItem struct {
	Start float64
	End   float64
	Label string
}

func Run(resultID int) (MezdoItems, error) {
	params := url.Values{}
	params.Add("request", strconv.Itoa(resultID))

	// Create the URL with the parameters
	url := config.MezdoApi + "?" + params.Encode()

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("http get: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body: %v", err)
	}
	unqBody, err := strconv.Unquote(string(body))
	if err != nil {
		return nil, fmt.Errorf("fail unquote: %v", err)
	}

	var mezdos MezdoItems
	if err = json.Unmarshal([]byte(unqBody), &mezdos); err != nil {
		return nil, fmt.Errorf("fail unmarshal: %v", err)
	}

	//filePath, err := files.SaveToTextFile([]byte(unqBody))
	//if err != nil {
	//	return "", fmt.Errorf("fail save to file: %v", err)
	//}

	return mezdos, nil
}
