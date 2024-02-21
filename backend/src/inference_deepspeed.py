import os
import torch
import deepspeed
from transformers import pipeline, LlamaTokenizer, LlamaForCausalLM
import google.protobuf

def main():
    local_rank = int(os.getenv('LOCAL_RANK', '0'))
    world_size = int(os.getenv('WORLD_SIZE', '1'))

    # Setup for potential distributed environment improvements
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank)

    # Finma model setup
    finma_tokenizer = LlamaTokenizer.from_pretrained('ChanceFocus/finma-7b-trade')
    finma_model = LlamaForCausalLM.from_pretrained('ChanceFocus/finma-7b-trade', device_map='auto')

    # Initialize the pipeline with specific device
    # generator = pipeline('text-generation', model='ChanceFocus/finma-7b-trade',
    #                      device=local_rank)

    # Initialize DeepSpeed Inference
    ds_engine = deepspeed.init_inference(finma_model,
                                               tensor_parallel={"tp_size": world_size},
                                               dtype=torch.float)
                                            #    replace_with_kernel_inject=True
    
    model = ds_engine.module

    # Efficient CUDA memory handling
    torch.cuda.empty_cache()  # Clear any cached memory to avoid out-of-memory

    with torch.no_grad():  # Ensures no gradients are computed to save memory
        # string = generator("DeepSpeed is", do_sample=True, min_length=50)
        output = model("Deepspeed is")

    # Ensure printing only occurs in the main process in a distributed setting
    if not torch.distributed.is_initialized() or torch.distributed.get_rank() == 0:
        print(output)

if __name__ == "__main__":
    main()
