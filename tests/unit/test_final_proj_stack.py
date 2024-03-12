import aws_cdk as core
import aws_cdk.assertions as assertions

from final_proj.final_proj_stack import FinalProjStack

# example tests. To run these tests, uncomment this file along with the example
# resource in final_proj/final_proj_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FinalProjStack(app, "final-proj")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
