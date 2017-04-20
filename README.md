# adverum-serverless-demoapp

This demo app was created in response to the following request;

Using AWS Cloud Transformation create a template that can be used to inflate a stack of your own choice that provides the following
1. A failsafe web server that can scale on demand, back ended by a database of your own choice, having the database reside  in a separate VPC.
2. The web page (only needs to be one) should provide the any wording as long as it is fetched from the backed data source.
3. A suitable monitoring solution should be in play that is triggered if the CPU utilization of the web server goes over 70% utilization. This should then trigger an alert that sends an email to a predefined address.

### Methodology and Approach
##### Criteria
The following criteria was derived from the requests
- Web server is to be scalable, resiliant and highly available.
- Database is to be secure and isolated from front-end.
- Notification event if web server utilization exceeds threshold of 70%.

##### Design
The application is based on S3 for static website hosting and a serverless backend composed of API Gateway, Lambda and DynamoDB.
- S3 was chosen to host the website as there is no server overhead and for practical purposes provides massive scalability. The service provides 11 9's of durability and 4 9's(99.99) of availability and can be replicated cross-region to provide further redundancy. The S3 website hosting can be further enhanced using CloudFront and WAF/Shield for improved performance and security.
- DynamoDB is a high performance, scalable service provided by AWS. Though the service is not VPC based, AWS has announced support for private VPC endpoints, thus allowing access from private resources (VPC or on-premise) without the need to traverse a public network. DynamoDB can be secured on multiple planes such as the control plane and/or the data/application plane(e.g. only an authenticated user may access or decrypt their data.)
- Access to the database is provided through the use of API Gateway and Lambda functions. This demo implements minimal security but this cand be enhanced to provide strong security, encryption and isolation.
- As S3 is a managed service provided by AWS, there are no servers to monitor and in this context, utilization will never exceed a threshold. Website monitoring and statistics are available for all website and cdn services.

##### Implementation
This repo contains the full code and templates needed to create a Serverless Demo App.

There are three separate parts to this application: the api, the pipeline which detects, builds, and deploys changes, and the website.

### Step 1

### Website
In the [website directory](website/) there are two files:

1. **[index.html](website/index.html):** This is the index file that our S3 bucket will be displaying.
2. **[website.yaml](website/website.yaml):** The CloudFormation template used to create the Amazon S3 bucket for the website.

Create the website stack using the console or cli.

Once the stack is complete, upload website artifacts with the following command.

```bash
sh upload_website.sh <profile-name> <s3-bucket-name>
```

And visit the url saved before.


### Step 2
### API
The Serverless API. The [api directory](api/) contains three files.

1. **[buildspec.yml](api/buildspec.yml):** This is used by CodeBuild in the build step of the pipeline.
2. **[index.js](api/index.js):** The Lambda function code.
2. **[app.yaml](api/app.yaml):** This is the SAM template file that will be used to create the API gateway resource, Lambda function and DynamoDB table, and hook them up together

Note: A new CodeCommit repo will be created in the following step. The files from the [api directory](api/) will be placed there. This repo will be used for the automated CI/CD pipeline built below.

### Step 3

### Pipeline
The pipeline is a full CI/CD serverless pipeline for building and deploying the api, lambda functions and DynamoDB table. This example uses CloudFormation to create the pipeline, all resources, and any permissions needed.

The following resources are created:

- An S3 bucket to store deployment artifacts.
- An AWS CodeBuild stage to build any changes checked into the repo.
- The AWS CodePipeline that will watch for changes on your repo, and push these changes through to build and deployment steps.
- All IAM roles and policies required.

The CloudFormation templates being used to create these resources can be found in [pipeline directory](pipeline/).

To create the pipeline stack, click the launch the stack using the console or cli.

Commit and push the files found in the [api directory](api/).

Go back to the pipeline we generated in Step 3, you will see AWS CodePipeline automatically pick up the changes, and start the build and deploy process.
