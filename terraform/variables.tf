variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-north-1"
}

variable "ssh_public_key" {
  description = "SSH public key to install on the EC2 instance (corresponds to EC2_SSH_KEY secret)"
  type        = string
  sensitive   = true
}
