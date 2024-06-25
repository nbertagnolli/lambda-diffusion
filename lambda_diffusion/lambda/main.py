import base64
import os
import json
from io import BytesIO
from diffusers import DiffusionPipeline

# Global variable to cache the model
pipe = None


def handler(event, context):
    global pipe
    event_dict = json.loads(event["body"])
    prompt = event_dict["prompt"]
    num_inference_steps = event_dict.get("num_inference_steps", 4)

    # Initialize the model if it hasn't been loaded yet
    if pipe is None:
        model_path = os.path.join(
            os.environ["LAMBDA_TASK_ROOT"],
            "segmind/tiny-sd/models--segmind--tiny-sd/snapshots/cad0bd7495fa6c4bcca01b19a723dc91627fe84f",
        )
        print(f"Initializing model at {model_path}")
        pipe = DiffusionPipeline.from_pretrained(model_path)

    # Generate the image
    print(f"Generating image for prompt: {prompt}")
    image = pipe(
        prompt=prompt,
        num_inference_steps=num_inference_steps,
        output_type="pil",
        low_memory=True,
    ).images[0]

    # Encode the image to base64
    print("Encoding image")
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {
        "headers": {"Content-Type": "image/png"},
        "statusCode": 200,
        "body": img_str,
        "isBase64Encoded": True,
    }
