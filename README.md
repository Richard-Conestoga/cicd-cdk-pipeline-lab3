# CDK Lambda API CI/CD Pipeline (Python)

## Overview

This project demonstrates an end‑to‑end CI/CD workflow for AWS infrastructure using:

- AWS CDK (Python)
- AWS CodePipeline
- AWS CodeBuild
- AWS Lambda
- Amazon API Gateway
- GitHub (via CodeStar Connections)

The pipeline automatically synthesizes and deploys a CDK stack that exposes a Lambda function through an API Gateway endpoint.

***

## Architecture

### Application Stack (`CicdCdkPipelineLab3Stack`)

- **Lambda Function**
    - Runtime: Python 3.x
    - Source: `lambda/hello.py`
    - Returns a JSON payload (`message`, `time`, `stage`, `version`).
- **API Gateway REST API**
    - Resource: `GET /hello`
    - Integration: Lambda proxy integration to the above function.
    - Stage: `dev`


### Pipeline Stack (`PipelineStack`)

- **Source Stage**
    - Provider: GitHub (via AWS CodeStar Connection)
    - Triggers on commits to a configured branch (e.g. `main`).
- **Build Stage (CodeBuild)**
    - Uses `buildspec.yml` to:
        - Install Python + Node dependencies
        - Run `cdk synth` for the app stack
        - Run `cdk deploy` for the app stack (`--require-approval never`)

> Note: The pipeline deploys the **application stack only**, not the pipeline stack itself.

***

## Repository Structure

Example layout:

```text
.
├── app.py                         # CDK app entrypoint
├── cdk.json                       # CDK configuration ("app": "python app.py")
├── requirements.txt               # Python dependencies (aws-cdk-lib, constructs, aws-cdk-cli, etc.)
├── buildspec.yml                  # CodeBuild build steps
├── lambda/
│   └── hello.py                   # Lambda handler code
└── cicd_cdk_pipeline_lab3/
    ├── __init__.py
    ├── cdk_cicd_lab_stack.py      # CdkCicdLabStack (Lambda + API)
    └── pipeline_stack.py          # PipelineStack (CodePipeline + CodeBuild)
```


***

## Prerequisites

- AWS account (personal, with permissions to create IAM, S3, Lambda, API Gateway, CodePipeline, CodeBuild, SSM)
- AWS CLI configured with a profile, for example: `personal`
- Node.js and npm
- Python 3.11+ and `pip`
- AWS CDK v2 (`npm install -g aws-cdk` for local use)
- GitHub repository for this project
- AWS CodeStar Connection to that GitHub repo

***

## Local Setup

1. Clone the repo:
```bash
git clone https://github.com/Richard-Conestoga/cicd-cdk-pipeline-lab3.git
cd cicd-cdk-pipeline-lab
```

2. Create and activate virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

4. Use your AWS profile:
```bash
export AWS_PROFILE=personal      # Windows: $env:AWS_PROFILE = "personal"
```

5. Bootstrap the environment (once per account/region):
```bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```

6. Synthesize and deploy the app stack locally:
```bash
cdk synth CicdCdkPipelineLab3Stack
cdk deploy CicdCdkPipelineLab3Stack
```

Copy the API Gateway URL from the output and test:

```bash
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/hello
```


***

## Pipeline Setup

### 1. CodeStar Connection to GitHub

In the AWS console (personal account and region):

1. Go to **Developer Tools → Connections**.
2. Create a new connection:
    - Provider: **GitHub**
    - Authorize and select your repo (e.g. `<your-username>/<your-repo>`).
3. Note the **connection ARN**.

### 2. Configure `PipelineStack` in CDK

In `app.py`:

```python
from cicd_cdk_pipeline_lab3.cdk_cicd_lab_stack import CdkCicdLabStack
from cicd_cdk_pipeline_lab3.pipeline_stack import PipelineStack

app = cdk.App()

CicdCdkPipelineLab3Stack(app, "CicdCdkPipelineLab3Stack")

PipelineStack(
    app,
    "PipelineStack",
    github_owner="<your-github-username>",
    github_repo="<your-repo-name>",
    github_branch="main",
    codestar_connection_arn="arn:aws:codestar-connections:REGION:ACCOUNT:connection/XXXX",
)

app.synth()
```

In `pipeline_stack.py`, `PipelineStack` defines:

- `CodeStarConnectionsSourceAction` pointing to your repo/branch.
- `CodeBuild` project using `buildspec.yml`.
- (Optionally) IAM policy to allow reading CDK bootstrap SSM parameter.

Deploy the pipeline stack:

```bash
cdk deploy PipelineStack
```


***

## CodeBuild Configuration (buildspec)

`buildspec.yml`:

```yaml
version: 0.2

phases:
  install:
    commands:
      - echo "Installing Python and Node dependencies"
      - pip install -r requirements.txt
      - npm install
  build:
    commands:
      - echo "CDK synth for app stack"
      - cdk synth CicdCdkPipelineLab3Stack > cdk-synth-output.yaml
      - echo "CDK deploy for app stack"
      - cdk deploy CicdCdkPipelineLab3Stack --require-approval never

artifacts:
  files:
    - cdk-synth-output.yaml
  discard-paths: yes
```

This lets CodeBuild both synthesize and deploy the app stack using CDK, handling Lambda asset uploads, IAM, and CloudFormation under the hood.

***

## End-to-End Flow

1. Developer changes Lambda code in `lambda/hello.py` (e.g., updates message).
2. Commit and push to the configured branch:
```bash
git add lambda/hello.py
git commit -m "Update Lambda response"
git push
```

3. CodePipeline automatically runs:
    - **Source**: pulls latest commit from GitHub.
    - **Build**: CodeBuild runs `cdk synth` + `cdk deploy` for `CicdCdkPipelineLab3Stack`.
4. After the pipeline succeeds, hitting the API Gateway URL `/dev/hello` returns the updated JSON response.

***

## Observability \& Debugging

- **CodePipeline**
    - View pipeline executions, per-stage status, and history.
- **CodeBuild**
    - View detailed build logs (including `cdk synth` / `cdk deploy` output).
- **CloudFormation**
    - Check stack events for `CicdCdkPipelineLab3Stack` and `PipelineStack` to debug resource-level issues.
- **Lambda Logs**
    - CloudWatch Logs group for the Lambda function shows invocation details and debug logs from `hello.py`.

***

## Clean-Up

To delete all lab resources:

```bash
# From project root, with AWS_PROFILE set to your personal profile
cdk destroy CicdCdkPipelineLab3Stack
cdk destroy PipelineStack
cdk destroy CDKToolkit   # optional: removes CDK bootstrap stack
```

Then verify in the console that:

- API Gateway, Lambda, CodePipeline, CodeBuild, and CloudFormation stacks are gone.