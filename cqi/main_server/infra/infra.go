package infra

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecr"
	"github.com/aws/aws-sdk-go-v2/service/rds"
	"github.com/aws/aws-sdk-go-v2/service/rds/types"
	"github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

const (
	INTERNAL_KEY_NAME = "internal_key"
	DB_SECRET_NAME    = "database"
	BOT_IMAGE_URL     = "ghcr.io/bourquejulien"
)

type Infra struct {
	config        aws.Config
	ecr           *ecr.Client
	secretManager *secretsmanager.Client
	rdsClient     *rds.Client
}

type Image struct {
	Tag     string
	Digest  string
	FullUrl string
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
	rdsClient := rds.NewFromConfig(config)

	return &Infra{config: config, ecr: client, secretManager: secretManager, rdsClient: rdsClient}, nil
}

func (p *Infra) GetInternalKey(ctx context.Context) (string, error) {
	result, err := p.secretManager.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{SecretId: aws.String(INTERNAL_KEY_NAME)})

	if err != nil {
		return "", fmt.Errorf("failed to get secret value, %v", err)
	}

	return *result.SecretString, nil
}

func (p *Infra) GetRdsInstanceById(ctx context.Context, instanceId string) (*types.DBInstance, error) {
	input := &rds.DescribeDBInstancesInput{
		DBInstanceIdentifier: aws.String(instanceId),
	}
	result, err := p.rdsClient.DescribeDBInstances(ctx, input)
	if err != nil {
		return nil, fmt.Errorf("failed to describe DB instance, %v", err)
	}

	if len(result.DBInstances) == 0 {
		return nil, fmt.Errorf("no DB instance found with ID %s", instanceId)
	}

	return &result.DBInstances[0], nil
}

func (p *Infra) GetRdsConnectionString(ctx context.Context) (string, error) {
	result, err := p.secretManager.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{SecretId: aws.String(DB_SECRET_NAME)})

	if err != nil {
		return "", fmt.Errorf("failed to get secret value, %v", err)
	}

	var secrets map[string]string
	json.Unmarshal([]byte(*result.SecretString), &secrets)

	var identifier, password string
	var ok bool

	if identifier, ok = secrets["identifier"]; !ok {
		return "", fmt.Errorf("failed to get secret value, %v", err)
	}

	if password, ok = secrets["password"]; !ok {
		return "", fmt.Errorf("failed to get secret value, %v", err)
	}

	instance, err := p.GetRdsInstanceById(ctx, identifier)

	if err != nil {
		return "", fmt.Errorf("failed to get RDS instance, %v", err)
	}

	instanceEndpoint := *instance.Endpoint.Address
	dbName := *instance.DBName
	username := *instance.MasterUsername

	filepath, err := downloadRdsCert()
	if err != nil {
		return "", fmt.Errorf("failed to download RDS certificate: %v", err)
	}

	return fmt.Sprintf("user=%s password=%s dbname=%s sslmode=require sslrootcert=%s host=%s", username, password, dbName, filepath, instanceEndpoint), nil
}

func (s *Infra) ListBotImages(ids []string) []*TeamImage {
	teamImages := make([]*TeamImage, 0, len(ids))
	for _, id := range ids {
		imageUrl := fmt.Sprintf("%s/%s:latest", BOT_IMAGE_URL, id)
		teamImages = append(teamImages, &TeamImage{TeamId: id, Images: []Image{{Tag: "latest", FullUrl: imageUrl}}})
	}

	return teamImages
}

func (p *Infra) ListImages(teamsIds []string, tags []string, ctx context.Context) ([]*TeamImage, error) {
	if len(teamsIds) == 0 {
		return make([]*TeamImage, 0), nil
	}

	input := &ecr.DescribeRepositoriesInput{}

	result, err := p.ecr.DescribeRepositories(ctx, input)
	if err != nil {
		return nil, fmt.Errorf("failed to describe repositories, %v", err)
	}

	teamImages := make([]*TeamImage, 0, len(result.Repositories))
	for _, repo := range result.Repositories {
		isValid := false
		for _, teamId := range teamsIds {
			if repo.RepositoryName != nil && *repo.RepositoryName == teamId {
				isValid = true
				break
			}
		}

		if !isValid {
			continue
		}

		listImagesInput := &ecr.ListImagesInput{RepositoryName: repo.RepositoryName}
		images, err := p.ecr.ListImages(ctx, listImagesInput)

		if err != nil {
			return nil, fmt.Errorf("failed to list images, %v", err)
		}

		teamImage := &TeamImage{TeamId: *repo.RepositoryName, Images: make([]Image, 0, len(images.ImageIds))}

		for _, image := range images.ImageIds {
			for _, tag := range tags {
				if image.ImageTag == nil || image.ImageDigest == nil {
					continue
				}

				if *image.ImageTag == tag {
					fullUrl := *repo.RepositoryUri + ":" + *image.ImageTag
					teamImage.Images = append(teamImage.Images, Image{Tag: *image.ImageTag, Digest: *image.ImageDigest, FullUrl: fullUrl})
					break
				}
			}
		}

		if len(teamImage.Images) == 0 {
			continue
		}

		teamImages = append(teamImages, teamImage)
	}

	return teamImages, nil
}
