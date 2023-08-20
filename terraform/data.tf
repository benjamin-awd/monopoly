data "google_secret_manager_secret_version" "default" {
  secret   = "monopoly-gmail-token"
  project  = "phonic-ceremony-394407"
}
