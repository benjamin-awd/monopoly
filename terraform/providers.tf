terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.75.1"
    }
  }
}

provider "google" {
  project     = local.project_id
  region      = local.region
}
