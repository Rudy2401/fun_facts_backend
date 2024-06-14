#!/usr/bin/env python3
import os

import aws_cdk as cdk

from fun_facts_backend.fun_facts_backend_stack import FunFactsBackendStack
from fun_facts_backend.auth_stack import AuthStack


app = cdk.App()
FunFactsBackendStack(app, "FunFactsBackendStack")
AuthStack(app, "AuthStack")

app.synth()
