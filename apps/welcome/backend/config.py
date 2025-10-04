import os
from pydantic_settings import BaseSettings
import google.generativeai as genai

class Settings(BaseSettings):
    APP_NAME: str = "AF PM Planner"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")  # ✅ Load Gemini key

    # AI Model Configuration - Centralized for easy updates
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.4
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TOP_P: float = 0.95
    GEMINI_TOP_K: int = 40

settings = Settings()

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_gemini_model(
    model_name: str = None,
    temperature: float = None,
    max_output_tokens: int = None,
    response_mime_type: str = None,
    system_instruction: str = None,
    top_p: float = None,
    top_k: int = None
):
    """
    Get a configured Gemini model instance with centralized settings.

    Args:
        model_name: Override default model name (optional)
        temperature: Override default temperature (optional)
        max_output_tokens: Override default max tokens (optional)
        response_mime_type: Set response format, e.g., "application/json" (optional)
        system_instruction: System instruction for the model (optional)
        top_p: Override default top_p (optional)
        top_k: Override default top_k (optional)

    Returns:
        Configured GenerativeModel instance
    """
    config = {
        "temperature": temperature if temperature is not None else settings.GEMINI_TEMPERATURE,
        "max_output_tokens": max_output_tokens if max_output_tokens is not None else settings.GEMINI_MAX_OUTPUT_TOKENS,
        "top_p": top_p if top_p is not None else settings.GEMINI_TOP_P,
        "top_k": top_k if top_k is not None else settings.GEMINI_TOP_K,
    }

    if response_mime_type:
        config["response_mime_type"] = response_mime_type

    model_params = {
        "model_name": model_name if model_name is not None else settings.GEMINI_MODEL,
        "generation_config": genai.types.GenerationConfig(**config)
    }

    if system_instruction:
        model_params["system_instruction"] = system_instruction

    return genai.GenerativeModel(**model_params)
