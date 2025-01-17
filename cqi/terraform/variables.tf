variable "team_names" {
  description = "List of team names"
  type        = list(string)
  default = [
    "ets",
    "poly",
    "concordia",
    "sherbrooke",
    "chicout",
    "rimouski",
    "uqtr",
    "laval",
    # "uqat",
    "mcgill",
    "mcgill2",
    "impossible"
  ]
}

variable "domain" {
  description = "The server domain"
  type = object({
    main_server = string
    game_runner = string
    address     = string
  })
  default = {
    main_server = "server"
    game_runner = "runner"
    address     = "cqiprog.info"
  }
}

variable "persisted_bucket_arn" {
  type = string
  default = "arn:aws:s3:::cqi-persisted"
}

variable "global_secret_arn" {
  type = string
  default = "arn:aws:secretsmanager:us-east-1:481665101132:secret:global_secrets-crxtcU"
}

variable "runner_count" {
  description = "The number of runner instances to create"
  type        = number
  default     = 3
}
