from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
)
from constructs import Construct


class PipelineStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        github_owner: str,
        github_repo: str,
        github_branch: str,
        codestar_connection_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact(artifact_name="CdkSynthOutput")

        build_project = codebuild.PipelineProject(
            self,
            "CdkSynthProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
                privileged=False,
            ),
        )

        pipeline = codepipeline.Pipeline(
            self,
            "CdkPipeline",
            pipeline_name="CdkLambdaApiPipeline",
        )

        pipeline.add_stage(
            stage_name="Source",
            actions=[
                cp_actions.CodeStarConnectionsSourceAction(
                    action_name="GitHub_Source",
                    owner=github_owner,
                    repo=github_repo,
                    branch=github_branch,
                    connection_arn=codestar_connection_arn,
                    output=source_output,
                )
            ],
        )

        pipeline.add_stage(
            stage_name="Build",
            actions=[
                cp_actions.CodeBuildAction(
                    action_name="Cdk_Synth",
                    project=build_project,
                    input=source_output,
                    outputs=[build_output],
                )
            ],
        )
        
        # Deploy stage: CloudFormation create/update using synthesized template
        deploy_stage = pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                cp_actions.CloudFormationCreateUpdateStackAction(
                    action_name="Deploy_CicdCdkPipelineLab3Stack",
                    template_path=build_output.at_path("cdk-synth-output.yaml"),
                    stack_name="CicdCdkPipelineLab3Stack",
                    admin_permissions=True,
                )
            ],
        )

