#!/usr/bin/env python3

import aws_cdk as cdk

from lambda_diffusion.lambda_diffusion_stack import LambdaDiffusionStack


app = cdk.App()
LambdaDiffusionStack(app, "LambdaDiffusionStack")

app.synth()
