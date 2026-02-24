terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

# ==========================================
# SNS TOPICS
# ==========================================
resource "aws_sns_topic" "weather_events" {
  name = "SNSWeatherEvents"
}

resource "aws_sns_topic" "weather_alerts" {
  name = "WeatherAlertNotifications"
}

# ==========================================
# DYNAMODB TABLES
# ==========================================
resource "aws_dynamodb_table" "alpinista_events" {
  name           = "alpinista_events"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }
}

resource "aws_dynamodb_table" "ciclista_events" {
  name           = "ciclista_events"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }
}

resource "aws_dynamodb_table" "dron_events" {
  name           = "dron_events"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }
}

resource "aws_dynamodb_table" "weather_alarmas" {
  name           = "weather_alarmas"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "eventId"

  attribute {
    name = "eventId"
    type = "S"
  }
}

# Nota: Para desplegar los Lambdas y SQS es necesario añadir archive_file, aws_iam_role, y aws_lambda_function. 
# Esto sirve de plantilla base y evidencia de conocimientos de IaC.
