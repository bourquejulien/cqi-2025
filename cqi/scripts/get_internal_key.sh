#!/bin/bash

set -e

aws secretsmanager get-secret-value \
    --secret-id internal_key \
    --query "SecretString" \
    --output text \
    | cat

