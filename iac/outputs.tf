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
