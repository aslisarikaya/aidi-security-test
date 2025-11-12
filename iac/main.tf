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

# HTTP
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

# --- Create the compute instance (VM) ---
resource "exoscale_compute_instance" "app" {
  zone               = var.zone
  name               = var.instance_name
  type               = var.instance_type
  template_id        = data.exoscale_template.ubuntu.id
  disk_size          = 10
  security_group_ids = [exoscale_security_group.svc.id]
  ssh_key            = exoscale_ssh_key.local.name
  user_data          = file("${path.module}/cloud-init.yaml")
}

# --- Second compute instance (App Server 2) ---
resource "exoscale_compute_instance" "app2" {
  zone               = var.zone
  name               = "${var.instance_name}-2"
  type               = var.instance_type
  template_id        = data.exoscale_template.ubuntu.id
  disk_size          = 10
  security_group_ids = [exoscale_security_group.svc.id]
  ssh_key            = exoscale_ssh_key.local.name
  user_data          = file("${path.module}/cloud-init.yaml")
}

