resource "google_service_account" "service_account" {
  account_id   = "monopoly"
  display_name = "Monopoly"
}

module "gmail" {
  source = "./modules/gmail"
}
