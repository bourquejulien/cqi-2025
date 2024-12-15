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
    "mcgill",
    "mcgill2",
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
