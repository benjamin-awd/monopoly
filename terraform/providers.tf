terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.75.1"
    }
  }
}

provider "google" {
  project     = "phonic-ceremony-394407"
  region      = "us-central1"
}
