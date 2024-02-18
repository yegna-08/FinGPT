import transformers
from fastapi import FastAPI, HTTPException, Request
import torch
from peft import PeftModel  # Assuming 'impot peft' was meant to be 'import peft'
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer, LlamaForCausalLM
import uvicorn
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
import deepspeed


ALLOWED_ORIGINS = ["*"]  # Replace with the actual origin of your client app
ALLOWED_METHODS = ["*"]
ALLOWED_HEADERS = ["*"]

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)


# Finma model setup
finma_tokenizer = LlamaTokenizer.from_pretrained('ChanceFocus/finma-7b-trade')
finma_model = LlamaForCausalLM.from_pretrained('ChanceFocus/finma-7b-trade', device_map='auto')

# FinGPT model setup

# base_model = AutoModelForCausalLM.from_pretrained(
#     'meta-llama/Llama-2-7b-chat-hf',
#     trust_remote_code=True,
#     device_map="auto",
#     # torch_dtype=torch.float16,   # optional if you have enough VRAM
# )
# fingpt_tokenizer = AutoTokenizer.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
# fingpt_model = PeftModel.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
# fingpt_model = fingpt_model.eval()

# # Initialize the tokenizer and DeepSpeed model for the FINMA model
# finma_tokenizer = AutoTokenizer.from_pretrained('ChanceFocus/finma-7b-trade')
# Assuming the model setup for DeepSpeed is similar to the example provided
# Note: DeepSpeed's init_inference requires a model object and a configuration
model_path = 'ChanceFocus/finma-7b-trade'  # Path to your model
deepspeed_config = {
    "fp16": {
        "enabled": True
    },
    "inference": {
        "auto": True,
        "transformer_layer": {
            "enabled": True
        }
    }
}
# model = LlamaForCausalLM.from_pretrained(model_path, device_map='auto')
engine = deepspeed.init_inference(finma_model, config=deepspeed_config)


async def generate_finma_response(text: str):
    inputs = finma_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: finma_model.generate(**inputs))
    return finma_tokenizer.decode(output[0], skip_special_tokens=True)

async def generate_fingpt_response(text: str):
    inputs = fingpt_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: fingpt_model.generate(**inputs))
    return fingpt_tokenizer.decode(output[0], skip_special_tokens=True)

@app.post("/finma")
async def finma_endpoint(request: Request):
    try:
        body = await request.json()
        text = body.get("text", None)
        if text:
            response = await generate_finma_response(text)
            return {"response": response}
        else:
            raise HTTPException(status_code=422, detail="Missing required fields")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def generate_finma_deepspeed_response(text: str):
    inputs = finma_tokenizer(text, return_tensors="pt")
    outputs = await run_in_threadpool(lambda: engine.module.generate(**inputs))
    return finma_tokenizer.decode(outputs[0], skip_special_tokens=True)

@app.post("/finma_deepspeed")
async def finma_deepspeed_endpoint(request: Request):
    try:
        body = await request.json()
        text = body.get("text", None)
        if text:
            response = await generate_finma_deepspeed_response(text)
            return {"response": response}
        else:
            raise HTTPException(status_code=422, detail="Missing required fields")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fingpt")
async def fingpt_endpoint(text: str):
    try:
        response = await generate_fingpt_response(text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Start Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=5000)
