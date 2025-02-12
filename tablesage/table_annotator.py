from .base_task import BaseTask
import re
import json

class TableAnnotator(BaseTask):
    def __init__(self, file="semantic_types.json"):
        self.examined = set()
        
        self.descriptions = [
            "Please look at the input table and determine the semantic type that best describes the table as a whole. The semantic type should reflect the main concept represented by all the columns together. Please only choose one semantic type from the candidate list, and remember that the type you choose has to accurately describe the entire table. If no candidate type can suitably describe the table, please return 'None'. Please only choose one type from the candidate list below, and *do not* create new types.",
        ]

        with open(file) as f:
            types = json.load(f)        
        types = '\n'.join(types)
        self.structure = "#Task Description: {}\n\n# Input:\n**Table:**\n{}\n**Candidate table types:**\n"+types+"\n\nReturn the final result as JSON in the format {{\"chosen_semantic_type\": \"<an entry from the candidate list or None>\"}}.\n\n# Output:"
        
    def clean_response(self, response):
        pattern = r'\{\s*"chosen_semantic_type"\s*:\s*"([^"]*)"\s*\}'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            result = match.group(1).strip()
            return result
        return None
        
    def merge(self, responses, model, endpoint=None, token=None):
        description = 'Given the following table semantic types, provide a single table semantic type that combines and covers all of them.'
        partials = ""
        for nor, response in enumerate(responses):
            partials += f"{nor+1}. {response}\n"
        prompt = "#Task Description: {}\n\n# Input:\n**Semantic Types:**\n{}\n\nReturn the final result as JSON in the format {{\"chosen_semantic_type\": \"<table semantic type>\"}}.\n\n# Output:"
        prompt = prompt.format(description, partials)
        
        response = self.run_prompt(prompt, model, endpoint, token)
        return response
        
        