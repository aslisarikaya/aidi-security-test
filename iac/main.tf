terraform {
  required_version = ">= 1.6.0"

  required_providers {
    exoscale = {
      source  = "exoscale/exoscale"
      version = ">= 0.51.0"
    }
  }
}

provider "exoscale" {
  key    = var.exoscale_api_key
  secret = var.exoscale_api_secret
}

# --- Template lookup (Ubuntu image) ---
data "exoscale_template" "ubuntu" {
  zone = var.zone
  name = var.template_name
}

# --- Register SSH key ---
resource "exoscale_ssh_key" "local" {
  name       = "${var.instance_name}-ssh"
  public_key = var.ssh_public_key
}

# --- Security group ---
resource "exoscale_security_group" "svc" {
  name        = "${var.instance_name}-sg"
  description = "Allow SSH, HTTP, HTTPS, and all outbound"
}

# SSH
resource "exoscale_security_group_rule" "allow_ssh" {
  security_group_id = exoscale_security_group.svc.id
  description       = "Allow SSH"
  type              = "INGRESS"
  protocol          = "TCP"
  start_port        = 22
  end_port          = 22
  cidr              = "0.0.0.0/0"
}

# HTTP (Container is running on port 80)
resource "exoscale_security_group_rule" "allow_http" {
  security_group_id = exoscale_security_group.svc.id
  description       = "Allow HTTP"
  type              = "INGRESS"
  protocol          = "TCP"
  start_port        = 80
  end_port          = 80
  cidr              = "0.0.0.0/0"
}

# HTTPS
resource "exoscale_security_group_rule" "allow_https" {
  security_group_id = exoscale_security_group.svc.id
  description       = "Allow HTTPS"
  type              = "INGRESS"
  protocol          = "TCP"
  start_port        = 443
  end_port          = 443
  cidr              = "0.0.0.0/0"
}

# Allow all outbound traffic
resource "exoscale_security_group_rule" "egress_all" {
  security_group_id = exoscale_security_group.svc.id
  description       = "Allow all outbound"
  type              = "EGRESS"
  protocol          = "TCP"
  start_port        = 1
  end_port          = 65535
  cidr              = "0.0.0.0/0"
}

# --- Create the single compute instance (VM) ---
# FIX APPLIED: Using 'templatefile' to correctly pass GHCR variables into cloud-init.yaml
resource "exoscale_compute_instance" "app" {
  zone               = var.zone
  name               = var.instance_name
  type               = var.instance_type
  template_id        = data.exoscale_template.ubuntu.id
  disk_size          = 10
  security_group_ids = [exoscale_security_group.svc.id]
  ssh_key            = exoscale_ssh_key.local.name
  
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    github_username   = var.github_username
    ghcr_pull_token   = var.ghcr_pull_token
    ghcr_image_path   = var.ghcr_image_path
    ghcr_image_tag    = var.ghcr_image_tag
  })
}

# --- Second compute instance "app2" has been removed as requested ---