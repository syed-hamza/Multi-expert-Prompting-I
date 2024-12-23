import requests
import json

class OllamaModel:
    def __init__(self, model_name="llama3.2:3b"):
        self.base_url = "http://localhost:11434"
        self.model_name = model_name

    def generate_response(self, prompt, role, system_prompt=None):
        url = f"{self.base_url}/api/generate"
        
        # Construct the prompt based on role and system prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\nRole: {role}\nUser: {prompt}"
        else:
            full_prompt = f"Role: {role}\nUser: {prompt}"

        data = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def get_expert_response(self, prompt, expert_type):
        system_prompts = {
            "surgeon": "You are an experienced surgeon with extensive medical knowledge.",
            "physiotherapist": "You are a skilled physiotherapist specializing in rehabilitation.",
            "doctor": "You are a general practitioner with broad medical expertise."
        }

        return self.generate_response(
            prompt=prompt,
            role=expert_type,
            system_prompt=system_prompts.get(expert_type, "You are a medical expert.")
        ) 