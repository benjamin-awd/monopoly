variable "ocbc_password" {
  description = "Password for encrypted OCBC PDFs"
  type        = string
  sensitive   = true
}

variable "hsbc_password" {
  description = "Password for encrypted HSBC PDFs"
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
  type        = list
  sensitive   = true
}
