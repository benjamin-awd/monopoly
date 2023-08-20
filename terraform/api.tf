# Enable APIs
resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "gmail" {
  service = "gmail.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy         = false
}
