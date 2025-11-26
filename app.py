#!/usr/bin/env python3
import aws_cdk as cdk

from cicd_cdk_pipeline_lab3.cicd_cdk_pipeline_lab3_stack import CicdCdkPipelineLab3Stack
from cicd_cdk_pipeline_lab3.pipeline_stack import PipelineStack

app = cdk.App()

app_stack = CicdCdkPipelineLab3Stack(app, "CicdCdkPipelineLab3Stack")

PipelineStack(
    app,
    "PipelineStack",
    github_owner="Richard-Conestoga",
    github_repo="cicd-cdk-pipeline-lab3",
    github_branch="main",  # or whatever branch you use
    codestar_connection_arn="arn:aws:codeconnections:us-east-1:349070093011:connection/fe767164-5b41-43b1-98c5-6d9fee3d6cda",
)

app.synth()
