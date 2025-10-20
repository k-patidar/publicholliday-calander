variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "key_name" {
  description = "Name of the existing AWS key pair to use for EC2 SSH"
  type        = string
}

variable "s3_bucket_name" {
  type = string
}
