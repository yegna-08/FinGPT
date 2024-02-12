import transformers
from fastapi import FastAPI, HTTPException
import torch
from peft import PeftModel  # Assuming 'impot peft' was meant to be 'import peft'
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer, LlamaForCausalLM
import uvicorn
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware


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
# fingpt_tokenizer = AutoTokenizer.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
# fingpt_model = PeftModel.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
# fingpt_model = fingpt_model.eval()

base_model = AutoModelForCausalLM.from_pretrained(
    'meta-llama/Llama-2-7b-chat-hf',
    trust_remote_code=True,
    device_map="auto",
    # torch_dtype=torch.float16,   # optional if you have enough VRAM
)
fingpt_tokenizer = AutoTokenizer.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
fingpt_model = PeftModel.from_pretrained('FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
fingpt_model = fingpt_model.eval()


app = FastAPI()

async def generate_finma_response(text: str):
    inputs = finma_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: finma_model.generate(**inputs))
    return finma_tokenizer.decode(output[0], skip_special_tokens=True)

async def generate_fingpt_response(text: str):
    inputs = fingpt_tokenizer(text, return_tensors="pt")
    output = await run_in_threadpool(lambda: fingpt_model.generate(**inputs))
    return fingpt_tokenizer.decode(output[0], skip_special_tokens=True)

@app.post("/finma")
async def finma_endpoint(text: str):
    try:
        response = await generate_finma_response(text)
        return {"response": response}
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
