"""
Model loader for the Intent Classification Service.
Loads ngbaoan/intent-banking with Unsloth (GPU) or transformers+peft (CPU fallback).
"""
import torch
import logging

logger = logging.getLogger(__name__)
MODEL_NAME = "ngbaoan/intent-banking"

def get_model():
    try:
        from unsloth import FastLanguageModel
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=MODEL_NAME, max_seq_length=512, dtype=None, load_in_4bit=True,
        )
        FastLanguageModel.for_inference(model)
        logger.info("Model loaded via Unsloth (GPU)")
        return model, tokenizer
    except Exception as e:
        logger.warning(f"Unsloth failed ({e}), using transformers+peft")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        base = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2.5-7B",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(base, MODEL_NAME).eval()
        logger.info(f"Model loaded via transformers+peft ({device})")
        return model, tokenizer
