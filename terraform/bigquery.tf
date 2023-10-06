resource "google_bigquery_dataset" "default" {
  dataset_id                  = "monopoly"
  friendly_name               = "monopoly"
  location                    = "US"
}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = "credit_card_statements"

  external_data_configuration {
    source_uris   = ["gs://${google_storage_bucket.default.name}/*.csv"]
    source_format = "CSV"
    autodetect    = true

    csv_options {
      quote = "\""
    }

    hive_partitioning_options {
      mode              = "AUTO"
      source_uri_prefix = "gs://${google_storage_bucket.default.name}/"
    }
  }
}
