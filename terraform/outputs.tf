output "public_ip" {
  description = "Static public IP of the EC2 instance — set this as EC2_HOST in GitHub Actions secrets"
  value       = aws_eip.app.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh -i your-key.pem ubuntu@${aws_eip.app.public_ip}"
}
