resource "google_service_account" "default" {
  account_id   = "monopoly"
  display_name = "Monopoly"
}

resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "default" {
  name          = "monopoly-${random_id.bucket_prefix.hex}"
  location      = "US"
  storage_class = "STANDARD"
}

resource "google_artifact_registry_repository" "default" {
  location      = var.region
  repository_id = "monopoly"
  format        = "DOCKER"
}

resource "google_secret_manager_secret_iam_binding" "default" {
  secret_id = data.google_secret_manager_secret_version.default.secret
  project   = data.google_secret_manager_secret_version.default.project
  role      = "roles/secretmanager.secretAccessor"

  members = [
    "serviceAccount:${google_service_account.default.email}"
  ]
}

resource "google_storage_bucket_iam_member" "default" {
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.default.email}"
}

resource "google_cloud_run_v2_job" "default" {
  name     = "monopoly-tf"
  location = var.region

  template {
    template {
      service_account = google_service_account.default.email
      max_retries     = 1

      containers {
        image = local.container_uri

        env {
          name  = "PUBSUB_TOPIC"
          value = google_pubsub_topic.default.id
        }
        env {
          name  = "GMAIL_ADDRESS"
          value = var.gmail_address
        }
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.default.name
        }
        env {
          name  = "SECRET_ID"
          value = var.gmail_credential_secret
        }
        env {
          name  = "TRUSTED_USER_EMAILS"
          value = jsonencode(var.trusted_emails)
        }
        env {
          name  = "OCBC_PDF_PASSWORD"
          value = var.ocbc_password
        }
        env {
          name  = "HSBC_PDF_PASSWORD_PREFIX"
          value = var.hsbc_password
        }
      }
    }
  }
}

resource "google_cloud_scheduler_job" "default" {
  name             = "hourly-bank-statement-extraction"
  description      = "Extracts bank statements"
  schedule         = "0 * * * *"
  time_zone        = "UTC"

  http_target {
    http_method = "POST"
      uri = "${local.cloud_run_scheduler_prefix}/jobs/${google_cloud_run_v2_job.default.name}:run"
    oauth_token {
      service_account_email = google_service_account.default.email
    }
  }
}

resource "google_project_iam_binding" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:${google_service_account.default.email}"
  ]
}
