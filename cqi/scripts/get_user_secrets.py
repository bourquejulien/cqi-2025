#! /usr/bin/env python3

import json
import boto3


def get_secret(secret_name: str) -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name="us-east-1"
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    return get_secret_value_response["SecretString"]


def main():
    SECRET_NAME = "user_secrets"
    secret = get_secret(SECRET_NAME)

    secret = json.loads(secret)
    print(json.dumps(secret, indent=4))


if __name__ == "__main__":
    main()
