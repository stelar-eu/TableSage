import pandas as pd
from .table_summarizer import TableSummarizer
from .column_summarizer import ColumnSummarizer
from .table_annotator import TableAnnotator
from .column_annotator import ColumnAnnotator
from .properties_merger import PropertiesMerger
from .temporal_extractor import TemporalExtractor
from .spatial_extractor import SpatialExtractor
from .properties_comparer import PropertiesComparer
from .insights_extractor import InsightsExtractor
from .properties_fuser import PropertiesFuser
from collections import Counter

class TableSage:
    
    def __init__(self):
        pass
    
    def load_dataset(self, file, separator=',', encoding='utf-8', engine='python'):
        try:
            self.df = pd.read_csv(file, sep=separator, encoding=encoding, engine='python')
        except Exception as e:
            self.df = None
            raise e
            
    def sample(self, df, sampling='random', sampling_number=5):
        if sampling == 'random':
            sample = df.head(sampling_number)
        return sample
    
    def create_profile(self):
        profiles = {}
        for col in self.df:
            profile = self.df[col].describe().to_dict()
            if self.df[col].dtype in ["float64", "int64"]:
                profiles[col] = profile
            elif self.df[col].dtype in ["object", "category"]:
                profile = {k:v for k,v in profile.items() if k in ['count', 'unique']}
                c = Counter(self.df[col].values)
                no = 5
                profile[f'top-{no}'] = [{'term': k, 'frequency': v} for k,v in c.most_common(no)]
                profiles[col] = profile
        return profiles
            
    ############### Table-Related Features ####################################
    
    def summarize_table(self, model, description_ids=0, sampling='random',
                        sampling_number=5, endpoint=None, token=None, verbose=True):
        ts = TableSummarizer()
        sampled_df = self.sample(self.df, sampling, sampling_number)
        responses = ts.run(sampled_df, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'table_summary', endpoint, token) #TODO: Merger should be different
        if not verbose:
            result['responses'] = responses
        return result
        
    def summarize_column(self, column, model, description_ids=0, sampling='random',
                         sampling_number=5, endpoint=None, token=None, verbose=True):
        cs = ColumnSummarizer()
        if column not in self.df:
            raise ValueError('Column {} not in DataFrame.'.format(column))
        sampled_df = self.df[column].to_frame()
        sampled_df = self.sample(sampled_df, sampling, sampling_number)
        responses = cs.run(sampled_df, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'column_summary', endpoint, token) #TODO: Merger should be different
        if not verbose:
            result['responses'] = responses
        return result
    
    def annotate_table(self, model, description_ids=0, sampling='random', sampling_number=5,
                        endpoint=None, token=None, verbose=True):
        ta = TableAnnotator()
        sampled_df = self.sample(self.df, sampling, sampling_number)
        responses = ta.run(sampled_df, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'table_type', endpoint, token) #TODO: Merger should be different
        if not verbose:
            result['responses'] = responses
        return result
    
    def annotate_column(self, column, model, description_ids=0, sampling='random', 
                       sampling_number=5, endpoint=None, token=None, verbose=True):
        ca = ColumnAnnotator()
        if column not in self.df:
            raise ValueError('Column {} not in DataFrame.'.format(column))
        sampled_df = self.df[column].to_frame()
        sampled_df = self.sample(sampled_df, sampling, sampling_number)
        responses = ca.run(sampled_df, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'column_type', endpoint, token) #TODO: Merger should be different
        if not verbose:
            result['responses'] = responses
        return result
    
    ############### Extraction-Related Features ###############################
    def extract_temporal(self, summary, model, description_ids=0, 
                         endpoint=None, token=None, verbose=True):
        if summary is None:
            raise ValueError('Summary cannot be None!')
        te = TemporalExtractor()
        responses = te.run(summary, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'temporal_span', endpoint, token)
        if not verbose:
            result['responses'] = responses
        return result
    
    def extract_spatial(self, summary, model, description_ids=0, 
                        endpoint=None, token=None, verbose=True):
        if summary is None:
            raise ValueError('Summary cannot be None!')
        se = SpatialExtractor()
        responses = se.run(summary, model, description_ids, endpoint, token)
        result = self.merge_properties(responses, model, 'spatial_coverage', endpoint, token)
        if not verbose:
            result['responses'] = responses
        return result    
    
    def extract_insights(self, properties, model, endpoint=None, token=None):
        profiles = self.create_profile()
        for col in properties:
            for k,v in properties[col].items():
                profiles[col][k] = v
        ie = InsightsExtractor()
        prompt = ie.create_prompt(profiles)
        response = ie.run_prompt(prompt, model, endpoint, token)
        return {'result': response}

    
    ############### Comparison-Related Features ###############################
    def compare_properties(self, properties, model, property_type='properties', endpoint=None, 
                         token=None):
        pc = PropertiesComparer()
        prompt = pc.create_prompt(properties, property_type)
        response = pc.run_prompt(prompt, model, endpoint, token)
        return {'result': response}
    
    ############### Fusion-Related Features ###################################
    
    def merge_properties(self, properties, model, property_type='properties', endpoint=None, 
                         token=None):
        pm = PropertiesMerger()
        prompt = pm.create_prompt(properties, property_type)
        response = pm.run_prompt(prompt, model, endpoint, token)
        return {'result': response}
 
    def fuse_properties(self, table_description, column_descriptions, insights, model, property_type='properties', endpoint=None, 
                         token=None):
        pf = PropertiesFuser()
        prompt = pf.create_prompt(table_description, column_descriptions, insights)
        response = pf.run_prompt(prompt, model, endpoint, token)
        return {'result': response}    
    