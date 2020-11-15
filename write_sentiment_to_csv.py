# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 08:21:46 2020

@author: Eric Bianchi
"""
from csv import writer
from csv import reader
from tqdm import tqdm
import pandas as pd
import torch
print(torch.__version__)
from torch import nn
import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup

PRE_TRAINED_MODEL_NAME = 'bert-base-cased'
MAX_LEN = 160
tokenizer = transformers.BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
class_names = ['1', '2', '3']
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

save_location = 'C://Users/Eric Bianchi/Desktop/'
query = "Childish Gambino - This Is America (Official Video)"
dataset_csv = save_location + query + '_cleaned_dataset.csv'
destination_csv = save_location + query + '_sentiment.csv'
class SentimentClassifier(nn.Module):

  def __init__(self, n_classes):
    super(SentimentClassifier, self).__init__()
    self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
    self.drop = nn.Dropout(p=0.3)
    self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
  
  def forward(self, input_ids, attention_mask):
    _, pooled_output = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask
    )
    output = self.drop(pooled_output)
    return self.out(output)

def clean_up_csv(csv_file):
    dataset_dataframe = pd.read_csv(csv_file, lineterminator='\n', encoding='utf-8')
    dataset_dataframe.to_csv(csv_file, encoding='utf-8-sig', index = False)
    return dataset_dataframe

def initialize_model(): 
    class_names = ['1', '2', '3']
    model = SentimentClassifier(len(class_names))
    bin_location = 'C://Users/Eric Bianchi/Documents/Virginia Tech/PhD/Coursework_CPE'
    model_path = bin_location + '/best_bert_sentiment_model_state.bin'
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    return model

def predict_sentiment(comment_text, tokenizer, model):
    encoded_review = tokenizer.encode_plus(comment_text, max_length=MAX_LEN,
                                       add_special_tokens=True,
                                       return_token_type_ids=False,
                                       pad_to_max_length=True,
                                       return_attention_mask=True,
                                       return_tensors='pt')
  
    input_ids = encoded_review['input_ids'].to(device)
    attention_mask = encoded_review['attention_mask'].to(device)

    output = model(input_ids, attention_mask)
    _, prediction = torch.max(output, dim=1)
    
    # print(f'Review text: {review_text}')
    # print(f'Sentiment  : {class_names[prediction]}'))
    
    return class_names[prediction]       

def iterate_csv_sentiment(tokenizer, source_csv):
    dataset_dataframe = clean_up_csv(source_csv)
    model = initialize_model()
    sentiment_array = []
    for index, row in tqdm(dataset_dataframe.iterrows()):
        comment_text = row['clean_comments']
        sentiment = predict_sentiment(comment_text, tokenizer, model)
        sentiment_array.append(sentiment)
        
    sentiment_array = iterate_csv_sentiment(tokenizer, dataset_csv)
    sent_df = pd.DataFrame(sentiment_array)
    concat = pd.concat([dataset_dataframe, sent_df], axis='col')
    
    return sent_df, concat

sent_df, concat = iterate_csv_sentiment(tokenizer, dataset_csv)
dataset_dataframe = clean_up_csv(dataset_csv)
concat = pd.concat([dataset_dataframe, sent_df], axis=1)
concat.to_csv(destination_csv,encoding='utf-8-sig', index = False, line_terminator='\n')