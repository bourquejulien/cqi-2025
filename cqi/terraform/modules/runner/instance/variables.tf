variable "global_secrets" {
  description = "The ARN of the global secrets"
  type = object({
    ssh_private_key = string
    github_token    = string
    namecheap_key   = string
  })
}

variable "ssh_key_name" {
  description = "The name of the SSH key"
  type        = string
}

variable "domain" {
  description = "The server domain"
  type = object({
    main_server = string
    game_runner = string
    address     = string
  })
}

variable "instance_profile_name" {
  description = "The name of the instance profile"
  type        = string
}

variable "instance_number" {
  description = "The id (number) of the instance"
  type        = number
}
