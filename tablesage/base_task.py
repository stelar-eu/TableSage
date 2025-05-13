from openai import OpenAI
import traceback
import re
import json

class BaseTask:
    def __init__(self):
        pass
    
    def run_prompt(self, prompt, model, endpoint=None, token=None):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        try:
            client = OpenAI(base_url = endpoint, api_key=token)
            
            response = client.chat.completions.create(
              model=model, messages=messages
            )
            response = response.choices[0].message.content
            
            response = self.clean_response(response)
            return response
        except Exception as e:
            traceback.print_exc()
            return None         
        
    def run_prompts(self, prompts, model, endpoint=None, token=None):
        responses = []
        for nop, prompt in enumerate(prompts):
            response = self.run_prompt(prompt, model, endpoint, token)
            responses.append(response)
        return responses        
        
    def clean_response(self, response):
        pattern = r'\{[\s\S]*\}'
        match = re.search(pattern, response, re.DOTALL)
        if match:   # 1-line JSON
            json_str = match.group(0)  # Get JSON content
            try:
                j = json.loads(json_str)  # Parse JSON
                return j[self.property_type]
            except json.JSONDecodeError as e:
                return None
        return None