from llama_cpp import Llama
import os

# Load the model once during module import
MODEL_PATH = 'model/MiniPLM-Qwen-200M-Q8_0.gguf'
NUM_THREADS = 8

llm = Llama(model_path=MODEL_PATH, n_threads=NUM_THREADS)

def generate_response(prompt, farm_data=None):
    """
    Generate a response based on agronomist context.

    :param prompt: The user input or question related to farming/agriculture.
    :param farm_data: (Optional) A dictionary with farm-related data (e.g., crop type, soil type, irrigation methods) to enrich the prompt.
    :return: The response from the AI model.
    """

    # Default agronomist-related prompt context
    agronomist_context = (
        "You are an expert agronomist advising Indian farmers.\n"
        "You understand local agro-climatic zones, cropping seasons, and farming practices.\n"
        "You help with crop planning, irrigation, soil health, pest control, and sustainable methods.\n"
        "Your advice considers local resources, smallholder needs, government schemes, and market access.\n"
        "Keep guidance practical, region-specific, and aimed at improving yield and sustainability.\n"
    )


    # Add farm-specific context if available (optional)
    if farm_data:
        farm_details = (
            f"The farm is growing {farm_data.get('crop', 'unspecified crop')}. "
            f"The farm's soil type is {farm_data.get('soil_type', 'unspecified')}, and it is using {farm_data.get('irrigation_type', 'unspecified irrigation')} irrigation."
        )
        agronomist_context += f"\nFarm Details: {farm_details}\n"

    # Create the full prompt by combining agronomist context with the user prompt
    formatted_prompt = f"{agronomist_context}Human: {prompt}\nAssistant:"

    # Generate response from the model
    output = llm(
        formatted_prompt,
        max_tokens=512,
        stop=["Human:"],
        echo=True
    )

    # Extract the assistant's response and return it
    full_response = output['choices'][0]['text']
    response = full_response[len(formatted_prompt):].strip()
    return response
