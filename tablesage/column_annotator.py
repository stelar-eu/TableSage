from .base_task import BaseTask
import re
import json

class ColumnAnnotator(BaseTask):
    def __init__(self, file="semantic_types.json"):
        self.examined = set()
        
        self.descriptions = [
            "Please look at the input column and determine the semantic type that can describe *every single* instance the input column. Please only choose one semantic type from the candidate list, and remember that the type you choose has to accurately describe every single entity in the column. If no candidate column type can suitably describe every single instance in the column, please return 'None'. Please only choose one type from the candidate list below, and *do not* create new types.",
        ]

        with open(file) as f:
            types = json.load(f)        
        types = '\n'.join(types)
        self.structure = "#Task Description: {}\n\n# Input:\n**Column:**\n{}\n**Candidate column types:**\n"+types+"\n\nReturn the final result as JSON in the format {{\"chosen_semantic_type\": \"<an entry from the candidate list or None>\"}}.\n\n# Output:"
        
    def clean_response(self, response):
        pattern = r'\{\s*"chosen_semantic_type"\s*:\s*"([^"]*)"\s*\}'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            result = match.group(1).strip()
            return result
        return None
        
    def merge(self, responses, model, endpoint=None, token=None):
        description = 'Given the following column semantic types, provide a single table semantic type that combines and covers all of them.'
        partials = ""
        for nor, response in enumerate(responses):
            partials += f"{nor+1}. {response}\n"
        prompt = "#Task Description: {}\n\n# Input:\n**Semantic Types:**\n{}\n\nReturn the final result as JSON in the format {{\"chosen_semantic_type\": \"<table semantic type>\"}}.\n\n# Output:"
        prompt = prompt.format(description, partials)
        
        response = self.run_prompt(prompt, model, endpoint, token)
        return response
        
        