terraform {
  required_providers {
    namecheap = {
      source  = "namecheap/namecheap"
      version = ">= 2.0.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

provider "namecheap" {
  user_name   = var.namecheap_username
  api_user    = var.namecheap_username
  api_key     = var.namecheap_key
  use_sandbox = false
}
