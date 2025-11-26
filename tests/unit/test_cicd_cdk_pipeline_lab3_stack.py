import aws_cdk as core
import aws_cdk.assertions as assertions

from cicd_cdk_pipeline_lab3.cicd_cdk_pipeline_lab3_stack import CicdCdkPipelineLab3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cicd_cdk_pipeline_lab3/cicd_cdk_pipeline_lab3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CicdCdkPipelineLab3Stack(app, "cicd-cdk-pipeline-lab3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
