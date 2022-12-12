provider "google" {

    #add the cloud provider name
    project = local.project
    region = local.region

}

data "google_billing_account" "account" {

    #this needs to be the literal name of the billing account. Change the billing account name in the variables.tf file
    display_name = var.billing_account_name

}

resource "google_project" "project" {

    #create a new project in Google Cloud Platform. Project name is assigned in variables.tf
    name = local.project_name
    project_id = local.project
    billing_account = data.google_billing_account.account.id

}

resource "google_project_iam_member" "project_owner" {

    role = "roles/owner"
    member = "user:${var.user}"
    project = local.project_name

    depends_on = [
        google_project.project
    ]
}

resource "google_storage_bucket" "storage_input_bucket" {
    name = local.input_bucket
    location = "US"
    force_destroy = true
    
    depends_on = [
        google_project_iam_member.project_owner
    ]
}

resource "google_storage_bucket" "storage_output_bucket" {
    name = local.output_bucket
    location = "US"
    force_destroy = true

    depends_on = [
        google_project_iam_member.project_owner
    ]
}

resource "google_storage_bucket" "storage_data_bucket" {
    name = local.data_bucket
    location = "US"
    force_destroy = true

    depends_on = [
        google_project_iam_member.project_owner
    ]
}

resource "google_storage_bucket_object" "testing_files" {
    name = "sample_files.zip" #name of the file 
    source = "../data/sample_files.zip"

    bucket = local.data_bucket

    depends_on = [
        google_storage_bucket.storage_data_bucket,
    ]
}


resource "google_project_service" "cloud_registry_service" {
  service = "containerregistry.googleapis.com"
  disable_dependent_services = true

  depends_on = [
    google_project.project,
  ]
}

resource "google_project_service" "cloud_build_service" {
  service = "cloudbuild.googleapis.com"
  disable_dependent_services = true

  depends_on = [
    google_project.project,
    google_project_iam_member.project_owner
  ]
}

resource "google_project_service" "cloud_run_service" {
  service = "run.googleapis.com"
  disable_dependent_services = true

  depends_on = [
    google_project.project,
  ]
}

#create cloud run service using the image
resource "google_cloud_run_service" "default" {
    
    project = local.project_name
    name     = local.cloudrun_name #name the cloud run service
    location = local.region

    template {

        spec {

            container_concurrency = 1

            containers {
                
                image = local.image_uri # Replace with newly created image uri
                
                resources {
                    limits = {
                        cpu = "2.0"
                        memory = "8000Mi"
                    }
                }
            }
        }
        
    }
        
    traffic {
        percent         = 100
        latest_revision = true
    }
    depends_on = [
        google_project.project,
        google_project_service.cloud_run_service,
        null_resource.app_container, 
    ]
}

#create a null resource to build the image from the app folder and push it to the google container registry.
resource "null_resource" "app_container" {

    provisioner "local-exec" {
       
        command = "cd ../app && gcloud config set project ${local.project} && gcloud builds submit --tag ${local.image_uri}"
    
    }

    depends_on = [
        google_project.project,
        google_project_service.cloud_build_service,
        google_project_iam_member.project_owner
    ]
}


#create the pubsub notification system.
resource "google_pubsub_topic" "default" {
    
    name = local.pubsub_name

    depends_on = [
      google_project_iam_member.project_owner,
    ]
}

resource "google_service_account" "sa" {

    account_id   = "cloud-run-pubsub-invoker"
    display_name = "Cloud Run Pub/Sub Invoker"

    depends_on = [
        google_project_iam_member.project_owner,
        google_project_service.cloud_run_service,
    ]
}

resource "google_cloud_run_service_iam_binding" "binding" {

    location = google_cloud_run_service.default.location
    service  = google_cloud_run_service.default.name
    role     = "roles/run.invoker"
    members  = ["serviceAccount:${google_service_account.sa.email}"]

    depends_on = [
        google_pubsub_topic.default,
        google_project_service.cloud_run_service,
    ]
}

resource "google_project_service_identity" "pubsub_agent" {
    
    provider = google-beta
    project  = local.project_name
    service  = "pubsub.googleapis.com"

    depends_on = [
        google_project.project,
        google_project_service.cloud_run_service,
    ]
}

resource "google_project_iam_binding" "project_token_creator" {
    
    project = local.project_name
    role    = "roles/iam.serviceAccountTokenCreator"
    members = ["serviceAccount:${google_project_service_identity.pubsub_agent.email}"]

    depends_on = [
        google_pubsub_topic.default,
        google_project_service.cloud_run_service,
    ]

}

resource "google_pubsub_subscription" "subscription" {
    
    name  = "pubsub_subscription"
    topic = google_pubsub_topic.default.name

    #acknoledgement deadline to 600 seconds
    ack_deadline_seconds = 600

    #message retention duration
    message_retention_duration = "1000s"

    push_config {
        push_endpoint = google_cloud_run_service.default.status[0].url
        oidc_token {
        service_account_email = google_service_account.sa.email
        }
        attributes = {
        x-goog-version = "v1"
        }
    }
    
    depends_on = [
        google_project.project,
        google_cloud_run_service.default
        ]
}


data "google_storage_project_service_account" "gcs_account" {
  depends_on = [
    google_project.project,
  ]
}

resource "google_pubsub_topic_iam_binding" "binding" {
    topic   = google_pubsub_topic.default.name
    role    = "roles/pubsub.publisher"
    members = ["serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"]

    depends_on = [
        google_project_service.cloud_run_service,
    ]
}

resource "google_storage_notification" "notification" {
    bucket         = google_storage_bucket.storage_input_bucket.name
    payload_format = "JSON_API_V1"
    topic          = google_pubsub_topic.default.id
    depends_on     = [google_pubsub_topic_iam_binding.binding]
}