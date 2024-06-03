import aws_cdk as core
import aws_cdk.assertions as assertions

from fun_facts_backend.fun_facts_backend_stack import FunFactsBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in fun_facts_backend/fun_facts_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FunFactsBackendStack(app, "fun-facts-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
