package scheduler

import (
	"bytes"
	"compress/gzip"
	"encoding/base64"
)

func compress(textData *string) *string {
	if (textData == nil) || (len(*textData) == 0) {
		return nil
	}

	data, err := base64.StdEncoding.DecodeString(*textData)

	if err != nil {
		return nil
	}

	var buffer bytes.Buffer
	w := gzip.NewWriter(&buffer)

	w.Write(data)
	w.Close()

	result := base64.StdEncoding.EncodeToString(buffer.Bytes())

	return &result
}
