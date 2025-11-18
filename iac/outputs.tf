output "vm_id" {
  value       = exoscale_compute_instance.app.id
  description = "ID of the created VM"
}

output "public_ip" {
  value       = exoscale_compute_instance.app.public_ip_address
  description = "Public IPv4 address of the VM"
}

output "ssh_command" {
  value       = "ssh ubuntu@${exoscale_compute_instance.app.public_ip_address}"
  description = "SSH command to connect to the VM"
}

# Exposes the public IP address of the deployed compute instance.
output "app_server_public_ip" {
  description = "The public IP address of the main application server."
  value       = exoscale_compute_instance.app.public_ip_address
}

# Exposes the URL where the service can be accessed via HTTP
output "app_service_url" {
  description = "The URL to access the deployed application service."
  value       = "http://${exoscale_compute_instance.app.public_ip_address}"
}