terraform {
  backend "s3" {
    bucket = "tf-state-store-20251016261abcd"
    key    = "recommender-system/terraform.tfstate"
    region = "eu-central-1"
  }
}