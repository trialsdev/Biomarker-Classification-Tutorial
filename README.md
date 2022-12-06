# Biomarker Classification Cloud Migration Code

This repository contains code that helps you to create a medical image classification workflow in the Google Cloud Platform (GCP). The code will create the following infrastructure in GCP. 

<img src = "https://user-images.githubusercontent.com/85404022/204656873-ffe04afc-e102-4e91-aa3e-698f6d777f92.png" width = 750, height = 500></img>

## Billable Resources ##

The following billable resources from GCP will be used in this example.

1. <a href = "https://cloud.google.com/run">Google Cloud Run</a>
2. <a href = "https://cloud.google.com/storage">Google Cloud Storage</a>
3. <a href = "https://cloud.google.com/pubsub">Pub/Sub</a>
4. <a href = "https://cloud.google.com/container-registry">Google Cloud Container Registry</a>

## Setup & Requirements ##

In order to run the code you will need a Google Cloud Platform Account with a billing account.

The following tools are required to be installed in your local machine in order to run the code.

1. <a href = "https://cloud.google.com/sdk/docs/install">Google Cloud CLI </a>

2. <a href = "https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli"> Terraform </a>

## Run Code ##

```
github clone https://github.com/trialsdev/Biomarker-Segmentation-Tutorial.git 
cd terraform
terraform init
terraform plan
terraform apply
```

## Test Code ##

In order to test the code, you can move the data in the "data_bucket" to the "input_bucket" to invoke the cloud run app. The resulting files will be saved in the "output_bucket". Run the following command in the google cloud shell to move the file to the "input_bucket". (Note that you can manually upload an object to the "input_bucket" as well)

```

```
Using GCP CLI

```

```

## Destroy the infrastructure ##

```
terraform destroy
```

## Additional Information ##


## References & Useful Links ##
