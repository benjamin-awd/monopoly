variable "ocbc_password" {
  description = "Password for encrypted OCBC PDFs"
  type        = string
  sensitive   = true
}

variable "hsbc_password_prefix" {
  description = "Prefix of password for encrypted HSBC PDFs"
  type        = string
  sensitive   = true
}

variable "gmail_address" {
  description = "Gmail address to which bank statements/transactions are sent"
  type        = string
  sensitive   = true
}

variable "trusted_emails" {
  description = "Trusted user emails"
  type        = list(any)
  sensitive   = true
}

variable "project_id" {
  description = "Google project ID"
  type        = string
}

variable "region" {
  description = "Google region"
  type        = string
}

variable "gmail_credential_secret" {
  description = "Name of secret containing client secret and token for Gmail account"
  type        = string
}
