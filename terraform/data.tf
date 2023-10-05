data "google_secret_manager_secret_version" "default" {
  secret   = "monopoly-gmail-token"
  project  = var.project_id
}
