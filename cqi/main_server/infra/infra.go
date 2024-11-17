package infra

import (
	"context"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecr"
	"github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

const (
	INTERNAL_KEY_NAME string = "internal_key"
)

type Infra struct {
	config        aws.Config
	ecr           *ecr.Client
	secretManager *secretsmanager.Client
}

type Image struct {
	Tag    string
	Digest string
}

type TeamImage struct {
	TeamId string
	Images []Image
}

func New(ctx context.Context) (*Infra, error) {
	config, err := config.LoadDefaultConfig(ctx, config.WithRegion("us-east-1"))
	if err != nil {
		return nil, fmt.Errorf("failed to load configuration, %v", err)
	}

	client := ecr.NewFromConfig(config)
	secretManager := secretsmanager.NewFromConfig(config)

	return &Infra{config: config, ecr: client, secretManager: secretManager}, nil
}

func (p *Infra) GetInternalKey(ctx context.Context) (string, error) {
	result, err := p.secretManager.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{SecretId: aws.String(INTERNAL_KEY_NAME)})

	if err != nil {
		return "", fmt.Errorf("failed to get secret value, %v", err)
	}

	return *result.SecretString, nil
}

func (p *Infra) ListImages(teamsIds []string, ctx context.Context) ([]*TeamImage, error) {
	input := &ecr.DescribeRepositoriesInput{RepositoryNames: teamsIds}

	results, err := p.ecr.DescribeRepositories(ctx, input)
	if err != nil {
		return nil, fmt.Errorf("failed to describe repositories, %v", err)
	}

	teamImages := make([]*TeamImage, len(results.Repositories))
	for _, repo := range results.Repositories {
		listImagesInput := &ecr.ListImagesInput{RepositoryName: repo.RepositoryName}
		images, err := p.ecr.ListImages(ctx, listImagesInput)

		if err != nil {
			return nil, fmt.Errorf("failed to list images, %v", err)
		}

		teamImage := &TeamImage{TeamId: *repo.RepositoryName, Images: make([]Image, len(images.ImageIds))}

		for _, image := range images.ImageIds {
			teamImage.Images = append(teamImage.Images, Image{Tag: *image.ImageTag, Digest: *image.ImageDigest})
		}

		teamImages = append(teamImages, teamImage)
	}

	return teamImages, nil
}
