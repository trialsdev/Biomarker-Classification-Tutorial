variable "billing_account_name" {

    default = "" #enter billing account name here

}

variable "user" {
    
    default = "" #enter user email address here

}

locals {

    project_name = "classificationtutorial${random_id.id.hex}" #enter your project name
    project = "${local.project_name}"
    region = "us-east1"

    #storage bucket names
    input_bucket = "bc_input_bucket" #enter your input bucket name
    output_bucket = "bc_output_bucket" #enter your output bucket name
    data_bucket = "bc_data_bucket" #enter your data bucket name

    #container image name and container image uri
    container_image_name = "bc-image" #enter your container image name
    image_name = "gcr.io/${local.project}/${local.container_image_name}"
    image_tag = "latest"
    image_uri = "${local.image_name}:${local.image_tag}"

    #cloud run service name
    cloudrun_name = "bc-cloudrun"

    #pubsub topic name
    pubsub_name = "bc-pubsub"

}


resource "random_id" "id" {

    byte_length = 2

}
