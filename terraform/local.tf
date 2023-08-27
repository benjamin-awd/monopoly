locals {
    project_id = "phonic-ceremony-394407"
    region = "us-central1"
    gmail_credential_secret = "monopoly-gmail-token"
    container_uri = "${local.region}-docker.pkg.dev/${local.project_id}/monopoly/monopoly:main"
    cloud_run_scheduler_prefix = "https://${local.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${local.project_id}"
}
