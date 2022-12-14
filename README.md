# Biomarker Classification Cloud Migration Code

This repository contains code that helps you to create a medical image classification workflow in the Google Cloud Platform (GCP). The code will create the following infrastructure in GCP. 

<img src = "https://user-images.githubusercontent.com/85404022/204656873-ffe04afc-e102-4e91-aa3e-698f6d777f92.png" width = 750, height = 500></img>

The code uses the winning <a href = "https://www.kaggle.com/c/rsna-intracranial-hemorrhage-detection/discussion/117210#latest-680918"> model </a> from the <a href = "https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/rsna-intracranial-hemorrhage-detection-challenge-2019"> 2019 Kaggle RSNA ICH Detection Challenge </a> to create a GCP infrastructure to classify ICH location given a batch of DICOM images. The GCP infrastructure expects a zipped folder with DICOM files and outputs a csv containing the ICH location of each patient image.

*Please note that the aim of this repository is to share the GCP infrastructure. In order to minimize the resources used by GCP, we have recreated only a part of the <a href = "https://www.kaggle.com/c/rsna-intracranial-hemorrhage-detection/discussion/117210#latest-680918"> model.</a> So the localization results created by the model are suboptimal.*


## Billable Resources ##

The following billable resources from GCP will be used in this example.

1. <a href = "https://cloud.google.com/run">Google Cloud Run</a>
2. <a href = "https://cloud.google.com/storage">Google Cloud Storage</a>
3. <a href = "https://cloud.google.com/pubsub">Pub/Sub</a>
4. <a href = "https://cloud.google.com/container-registry">Google Cloud Container Registry</a>

## Setup & Requirements ##

In order to run the code you will need a billing enabled GCP Account. Click <a href = "https://cloud.google.com/billing/docs/how-to/manage-billing-account"> here </a> to learn how to setup a GCP billing account.

The following tools are required to be installed in your local machine in order to run the code.

1. <a href = "https://cloud.google.com/sdk/docs/install">Google Cloud CLI </a>

2. <a href = "https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli"> Terraform </a>

3. <a href = "https://docs.docker.com/get-docker/"> Docker </a>

## Add credentials ##

Before running the code first you need to edit the var.tf file. Locate this file in terraform directory and edit the billing account name and the user email address. 

```
variable "billing_account_name" {
    default = "your billing account name"
}

variable "user" {
    default = "your GCP email address"
}
```

## Run Code ##

```
github clone https://github.com/trialsdev/Biomarker-Classification-Tutorial.git 
cd terraform
terraform init
terraform plan
terraform apply
```

## Test Code ##

In order to test the code, you can move the data in the "data_bucket" to the "input_bucket" to invoke the cloud run app. The resulting files will be saved in the "output_bucket". Run the following command in the google cloud shell to move the file to the "input_bucket". 

```
gsutil cp gs://bc_data_bucket/sample_files.zip gs://bc_input_bucket/sample_files.zip
```
Using GCP CLI

```
gcloud storage cp gs://bc_data_bucket/sample_files.zip gs://bc_input_bucket/sample_files.zip
```
*Note that you can manually upload an object to the "input_bucket" as well*

## Destroy the infrastructure ##

```
terraform destroy
```

## Additional Information ##

- While destroying the infrastructure, if you recieve an error that says a certain "API is disabled", please go to GCP platform by clicking the corresponding link. Then enable the API and run ```terraform destroy``` again in your local machine.

## References & Useful Links ##

- <a href = "https://cloud.google.com/pubsub/docs/tutorials"> Google Cloud Pub/Sub tutorials </a>.
- <a href = "https://codelabs.developers.google.com/codelabs/cloud-run-hello-python3#6"> Google Cloud run tutorials </a>
- <a href = "https://cloud.google.com/docs/terraform/get-started-with-terraform"> Google Cloud - Terraform documentation </a>
- <a href = "https://registry.terraform.io/providers/hashicorp/google/latest/docs"> Terraform - Google Cloud documentation </a>
