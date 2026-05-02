terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # S3 state bucket: hzortech-tf-state (eu-north-1)
  backend "s3" {
    bucket = "hzortech-tf-state"
    key    = "hzortech/terraform.tfstate"
    region = "eu-north-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Security group ──────────────────────────────────────────────────────────

resource "aws_security_group" "app" {
  name        = "hzortech-sg"
  description = "Allow HTTP, HTTPS, SSH inbound; all outbound"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "k3s API (kubectl from CI)"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "hzortech-sg" }
}

# ── Key pair ────────────────────────────────────────────────────────────────

resource "aws_key_pair" "deploy" {
  key_name   = "hzortech-deploy"
  public_key = var.ssh_public_key
}

# ── AMI (latest Ubuntu 22.04 LTS) ───────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── EC2 instance — t2.micro (free tier: 750 hrs/month) ──────────────────────

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.deploy.key_name
  vpc_security_group_ids = [aws_security_group.app.id]

  root_block_device {
    volume_size = 20        # free tier allows up to 30 GB
    volume_type = "gp2"
    encrypted   = true
  }

  # Bootstrap: install k3s (lightweight k8s) + cert-manager on first boot.
  # GitHub Actions handles all subsequent app deployments via kubectl.
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install k3s — includes kubectl, Traefik ingress, and CoreDNS
    curl -sfL https://get.k3s.io | sh -

    # Wait for k3s API to be ready
    until /usr/local/bin/kubectl get nodes 2>/dev/null; do sleep 5; done

    # Give the ubuntu user kubectl access
    mkdir -p /home/ubuntu/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
    chown -R ubuntu:ubuntu /home/ubuntu/.kube

    # Install cert-manager (handles Let's Encrypt TLS automatically)
    /usr/local/bin/kubectl apply -f \
      https://github.com/cert-manager/cert-manager/releases/download/v1.14.3/cert-manager.yaml

    # Wait for cert-manager webhooks to be ready before any apply
    /usr/local/bin/kubectl rollout status \
      -n cert-manager deployment/cert-manager-webhook --timeout=120s

    # Set up app directory
    mkdir -p /opt/hzortech
    chown -R ubuntu:ubuntu /opt/hzortech
  EOF

  tags = { Name = "hzortech-app" }

  lifecycle {
    ignore_changes = [ami, user_data]
  }
}

# ── Elastic IP — free when attached to a running instance ───────────────────

resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = { Name = "hzortech-eip" }

  depends_on = [aws_instance.app]
}
