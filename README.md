# Public Holidays Calendar

This project provides a minimal Flask backend that integrates with the Calendarific API to fetch public holidays by country and year, a simple Bootstrap frontend, Docker/Docker Compose setup, Terraform infra to provision an EC2 instance and S3 bucket, a Jenkinsfile for CI/CD, and Grafana/Prometheus monitoring.

## Features
- REST endpoints:
  - GET /api/holidays?country=IN&year=2025
  - GET /api/countries
- Prometheus metrics exposed at /metrics
- Dockerized Flask app and docker-compose with Prometheus and Grafana
- Terraform to provision EC2 and S3
- Jenkinsfile to build, push, and deploy via SSH

## Environment
- CALENDARIFIC_API_KEY: required for Calendarific API access

## Local run with Docker Compose
1. Copy or set CALENDARIFIC_API_KEY in environment, e.g. (PowerShell):

```powershell
$env:CALENDARIFIC_API_KEY = "your_api_key_here"
docker-compose up --build
```

The Flask app will be available at http://localhost:5000 and Grafana at http://localhost:3000 (admin/admin default for first run).

## Terraform
1. Configure AWS credentials in your environment (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. Set variables for `key_name` and `s3_bucket_name`. Example:

```powershell
terraform init
terraform apply -var "key_name=my-key" -var "s3_bucket_name=my-unique-bucket-name"
```

3. After apply, Terraform outputs the EC2 public IP. SSH to the instance and copy repository contents to `~/app`, then run `docker-compose up -d --build`.

## Jenkins
The `jenkins/Jenkinsfile` contains pipeline stages for building and pushing a Docker image and deploying to EC2. You need to configure credentials (dockerhub-credentials and ec2-ssh) and set `EC2_HOST` environment variable in Jenkins.

## Notes & Next steps
- This starter implementation uses a minimal in-memory country list. You can expand it or fetch a full list from Calendarific or another source.
- For production: secure Grafana, lock down security groups, configure IAM for S3 access, add proper logging and caching.
