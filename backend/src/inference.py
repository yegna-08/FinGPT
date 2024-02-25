import os
import transformers
from fastapi import FastAPI, HTTPException, Request
import torch
from peft import PeftModel  # Assuming 'impot peft' was meant to be 'import peft'
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer, LlamaForCausalLM, pipeline
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

# Initialize the model once when the app starts
local_rank = int(os.getenv('LOCAL_RANK', '0'))
world_size = int(os.getenv('WORLD_SIZE', '1'))
if torch.cuda.is_available():
    torch.cuda.set_device(local_rank)

# # Finma model setup
# finma_tokenizer = LlamaTokenizer.from_pretrained('ChanceFocus/finma-7b-trade')
# finma_model = LlamaForCausalLM.from_pretrained('ChanceFocus/finma-7b-trade', device_map='auto')

generator_bloom = pipeline('text-generation', model='bigscience/bloom-1b1', device=local_rank)
generator_bloom.model = deepspeed.init_inference(generator_bloom.model, tensor_parallel={"tp_size": world_size}, dtype=torch.float, replace_with_kernel_inject=False)

generator_gemma = pipeline('text-generation', model='google/gemma-2b', device=local_rank)
generator_gemma.model = deepspeed.init_inference(generator_gemma.model, tensor_parallel={"tp_size": world_size}, dtype=torch.float, replace_with_kernel_inject=False)

# FinGPT model setup

# base_model = AutoModelForCausalLM.from_pretrained(
#     'meta-llama/Llama-2-7b-chat-hf',
#     trust_remote_code=True,
#     device_map="auto",
#     # torch_dtype=torch.float16,   # optional if you have enough VRAM
# )
# # fingpt_tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf')
# fingpt_model = PeftModel.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
# fingpt_model = fingpt_model.eval()

async def generate_finma_response(text: str):
    inputs = finma_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: finma_model.generate(**inputs))
    return finma_tokenizer.decode(output[0], skip_special_tokens=True)

async def generate_fingpt_response(text: str):
    inputs = finma_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: fingpt_model.generate(**inputs))
    return finma_tokenizer.decode(output[0], skip_special_tokens=True)

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

@app.post("/fingpt")
async def fingpt_endpoint(request: Request):
    try:
        body = await request.json()
        text = body.get("text", None)
        if text:
            response = await generate_fingpt_response(text)
            return {"response": response}
        else:
            raise HTTPException(status_code=422, detail="Missing required fields")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bloom_deepspeed")
async def generate_text(request: Request):
    try:
        body = await request.json()
        text = body.get("text", None)
        print(text)
        if text:
            # Clear any cached memory to avoid out-of-memory
            torch.cuda.empty_cache()
            # Generate text
            with torch.no_grad():  # Ensures no gradients are computed to save memory
                generated_text = generator_bloom(text, do_sample=True, max_new_tokens=50)
                return {"response": generated_text[0]['generated_text']}
        else: 
            raise HTTPException(status_code=422, detail="Missing required fields")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/gemma_deepspeed")
async def generate_text(request: Request):
    try:
        body = await request.json()
        text = body.get("text", None)
        print(text)
        if text:
            # Clear any cached memory to avoid out-of-memory
            torch.cuda.empty_cache()
            # Generate text
            with torch.no_grad():  # Ensures no gradients are computed to save memory
                generated_text = generator_gemma(text, do_sample=True, max_new_tokens=50)
                return {"response": generated_text[0]['generated_text']}
        else: 
            raise HTTPException(status_code=422, detail="Missing required fields")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

if __name__ == "__main__":
    # Start Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=5000)
