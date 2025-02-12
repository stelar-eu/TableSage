import pandas as pd
from .table_summarizer import TableSummarizer
from .column_summarizer import ColumnSummarizer
from .table_annotator import TableAnnotator
from .column_annotator import ColumnAnnotator

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
            
    def summarize_table(self, model, description_ids=0, sampling='random', sampling_number=5,
                        endpoint=None, token=None, verbose=True):
        ts = TableSummarizer()
        sampled_df = self.sample(self.df, sampling, sampling_number)
        responses = ts.run(sampled_df, model, description_ids, endpoint, token, verbose)
        return responses
        
    def summarize_column(self, column, model, description_ids=0, sampling='random', sampling_number=5,
                        endpoint=None, token=None, verbose=True):
        cs = ColumnSummarizer()
        if column not in self.df:
            raise ValueError('Column {} not in DataFrame.'.format(column))
        sampled_df = self.df[column].to_frame()
        sampled_df = self.sample(sampled_df, sampling, sampling_number)
        responses = cs.run(sampled_df, model, description_ids, endpoint, token, verbose)
        return responses        
    
    def annotate_table(self, model, description_ids=0, sampling='random', sampling_number=5,
                        endpoint=None, token=None, verbose=True):
        ta = TableAnnotator()
        sampled_df = self.sample(self.df, sampling, sampling_number)
        responses = ta.run(sampled_df, model, description_ids, endpoint, token, verbose)
        return responses
    
    def annotate_column(self, column, model, description_ids=0, sampling='random', sampling_number=5,
                        endpoint=None, token=None, verbose=True):
        ca = ColumnAnnotator()
        if column not in self.df:
            raise ValueError('Column {} not in DataFrame.'.format(column))
        sampled_df = self.df[column].to_frame()
        sampled_df = self.sample(sampled_df, sampling, sampling_number)
        responses = ca.run(sampled_df, model, description_ids, endpoint, token, verbose)
        return responses       