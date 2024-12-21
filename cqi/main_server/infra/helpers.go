package infra

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

const (
	RDS_CERT_URL        = "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem"
	RDS_FILE            = "rds-combined-ca-bundle.pem"
	ec2MetadataTokenURL = "http://169.254.169.254/latest/api/token"
	ec2MetadataURL      = "http://169.254.169.254/latest/meta-data/instance-id"
)

func IsRunningOnEC2() bool {
	token, err := getIMDSToken()
	if err != nil {
		return false
	}

	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	req, err := http.NewRequest("GET", ec2MetadataURL, nil)
	if err != nil {
		return false
	}

	req.Header.Set("X-aws-ec2-metadata-token", token)

	resp, err := client.Do(req)
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return false
	}

	_, err = io.ReadAll(resp.Body)
	return err == nil
}

func getIMDSToken() (string, error) {
	client := &http.Client{
		Timeout: 1 * time.Second,
	}

	req, err := http.NewRequest("PUT", ec2MetadataTokenURL, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request for IMDSv2 token: %v", err)
	}

	req.Header.Set("X-aws-ec2-metadata-token-ttl-seconds", "21600")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to get IMDSv2 token: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to get IMDSv2 token, status code: %d", resp.StatusCode)
	}

	token, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read IMDSv2 token response: %v", err)
	}

	return string(token), nil
}

func downloadRdsCert() (string, error) {
	resp, err := http.Get(RDS_CERT_URL)
	if err != nil {
		return "", fmt.Errorf("failed to download RDS certificate: %v", err)
	}
	defer resp.Body.Close()

	out, err := os.CreateTemp("", RDS_FILE)
	if err != nil {
		return "", fmt.Errorf("failed to create certificate file: %v", err)
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to save certificate file: %v", err)
	}

	return out.Name(), nil
}
