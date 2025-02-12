from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI
import torch
import traceback

class BaseTask:
    def __init__(self):
        pass
    
    def serialize_table(self, df):
        header = '|' + '|'.join(df.columns) + '|'
        separator = '|' + '|'.join('---' for _ in df.columns) + '|'
        content = '\n'.join('|' + '|'.join(str(val).strip() for val in row) + '|' for row in df.fillna('').values)
        return f"{header}\n{separator}\n{content}"

    def create_prompt(self, df, description_ids=0):
        descriptions = self.descriptions
        structure = self.structure
        
        df_str = self.serialize_table(df)

        if type(description_ids) == int:
            description_ids = [description_ids]

        prompts = []            
        for description_id in description_ids:
            if type(description_id) == str: #direct description
                description = description_id
            elif type(description_id) == int:
                if description_id >= len(descriptions):
                    raise ValueError("ID not in available templates, please provide a value between 0 and {}.".format(len(descriptions)))
                description = descriptions[description_id]
            else:
                raise ValueError("Wrong type of descriptions")
            prompt = structure.format(description, df_str)
            prompts.append(prompt)
        return prompts
        
    
    def run_prompts(self, prompts, model, endpoint=None, token=None):
        responses = []
        for nop, prompt in enumerate(prompts):
            # print('Prompt no:', nop+1)
            response = self.run_prompt(prompt, model, endpoint, token)
            responses.append(response)
        return responses
    
    def run_prompt(self, prompt, model, endpoint=None, token=None):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        try:
            if endpoint is None: # HuggingFace alternative:
                device = torch.device("cuda:0") if torch.cuda.is_available() else "cpu"
                self.model = AutoModelForCausalLM.from_pretrained(
                    model, torch_dtype=torch.float16, device_map={"": 0}
                ).to(device)
                self.tokenizer = AutoTokenizer.from_pretrained(model)
                

                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
                generated_ids = self.model.generate(**model_inputs, max_new_tokens=512)
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                
                del self.model
                del self.tokenizer
                torch.cuda.empty_cache()
                
            else: # OpenAI protocol
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
    
    def run(self, df, model, description_ids=0, endpoint=None, token=None, verbose=True):
        prompts = self.create_prompt(df, description_ids)
        responses = self.run_prompts(prompts, model, endpoint, token)
        result = self.merge(responses, model, endpoint, token)
        
        output = {'result': result}
        if not verbose:
            output['responses'] = responses
        return output
