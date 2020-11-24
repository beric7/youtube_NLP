# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 17:58:49 2020

@author: Eric Bianchi

references:
    https://github.com/ripulagrawal98/Analytic_Steps/blob
    /master/Extract%20%26%20Pre-process%20-YouTube-Comments
    /Extract%26Clean-YouTube-Comments.ipynb
"""
import csv
import os
import pickle
import google.oauth2.credentials

import pandas as pd
import demoji
import emoji
from emoji import UNICODE_EMOJI
from langdetect import detect
import re   # regular expression
from tqdm import tqdm
import itertools
import collections
import matplotlib.pyplot as plt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Authenticate service
def get_authenticated_service(save_location):
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                save_location + CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

# result query from the request video search, this brings up a list of videos. 
# we choose the video that appears first in this query list which is why it is
# important to have the name exactly as it appears. 
def query_results(query, service):
    query_results = service.search().list(part = 'snippet',q = query,
                                      order = 'relevance', 
                                      type = 'video',
                                      relevanceLanguage = 'en',
                                      safeSearch = 'moderate').execute()
    return query_results

# This function extracts the details from a given video and returns the result
# which again contains all the videos that this query returns. 
def extract_video_details(query_results):
    video_id = []
    channel = []
    video_title = []
    video_desc = []
    for item in query_results['items']:
        video_id.append(item['id']['videoId'])
        channel.append(item['snippet']['channelTitle'])
        video_title.append(item['snippet']['title'])
        video_desc.append(item['snippet']['description'])
    video_id = video_id[0]
    channel = channel[0]
    video_title = video_title[0]
    video_desc = video_desc[0]
    
    return video_id, channel, video_title, video_desc

# This is the function that extracts comments. The extraction originally put all the comments
# into an array which was later turned into a CSV file. It is better suited, 
# due to memory contraints, if they were added directly to the CSV file as it was 
# being read. This way we do not have to store the text in the CPU memory, this is what I did.
# 
# @param: video_id = unique youtube video ID
# @param: channel = unique channel video is on
# @param: video_title = video title
# @param: video_desc = video description
# @param: save_csv_location = where the csv file is being saved
# @param: the number of iterations
# @param: type_ = the type of ordering for the response, (time = more, relevance caps at 2000)
def extract_comments(video_id, channel, video_title, video_desc, save_csv_location, number, type_, service):
    nextPage_token = None
    count = 0
        
    with open(save_csv_location, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Comment', 'Initial Reply', 'Replies', 'Likes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()
        # this captures the bulk of the information, but may miss out on the most relevant comments
        while 1:
          response = service.commentThreads().list(
                            part = 'snippet, replies',
                            videoId = video_id,
                            maxResults = 100, 
                            order = type_, 
                            textFormat = 'plainText',
                            pageToken = nextPage_token
                            ).execute()
          nextPage_token = response.get('nextPageToken')
          
          for item in response['items']:
              if 'replies' in item.keys():
                  
                  reply_text = get_reply(item, service)
                  comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                  comment_text = encode_decode(demojize(comment_text))
                  
                  writer.writerow({'Comment': comment_text,
                                   'Initial Reply': reply_text,
                                   'Replies': item['snippet']['totalReplyCount'],
                                   'Likes': item['snippet']['topLevelComment']['snippet']['likeCount']})        
                  count = count + 1
                  if (count % 50) == 0:
                      print(count)
          if nextPage_token is None or count > number:
            break

# Helper function to get the first reply. Essentially youtube goes from the bottom-up. 
def get_reply(item, service):
    parent_id = item["id"]
    max_num = item['snippet']['totalReplyCount']
    array= []
    it = 0
    nextPage_token = None
    while 1:
        response = service.comments().list(
                      part = 'snippet',
                      maxResults = 100,
                      parentId = parent_id, 
                      textFormat = 'plainText',
                      pageToken = nextPage_token
                      ).execute()
        nextPage_token = response.get('nextPageToken')
        for reply in response['items']:
            array.append(reply)
            it = it + 1
        if nextPage_token is None or it >= max_num - 1:
            break
    array = response['items']
    length = len(array)
    # remove remoji
    reply_text = demojize(array[length-1]["snippet"]["textDisplay"])
    # remove nonsense characters
    reply_text = encode_decode(reply_text)
    return reply_text

# search your emoji
def is_emoji(s):
    return s in UNICODE_EMOJI

# add space near your emoji
def add_space(text):
    return ''.join(' ' + char if is_emoji(char) else char for char in text).strip()

def demojize(text):
    text_space = add_space(text)
    text = emoji.demojize(text_space)   
    return text

# This function only shows english comments. We only check the comment. 
def show_english_only(comments, save_location, english_comment_csv, query):
    comments['language'] = 0
    count = 0
    for i in tqdm(range(0,len(comments))):
    
    
      temp = comments['Comment'].iloc[i]
      count += 1
      try:
        comments['language'].iloc[i] = detect(temp)
      except:
        comments['language'].iloc[i] = "error"
    
    comments[comments['language']=='en']['language'].value_counts()
    english_comm = comments[comments['language'] == 'en']    
    
    english_comment_csv = save_location + query + '_EN.csv'
    english_comm.to_csv(english_comment_csv, index = False, encoding='utf-8-sig')
    return english_comm

# removes the stupid nonsense characters!
def encode_decode(input_text):
    encoded_string = input_text.encode("ascii", "ignore")
    return encoded_string.decode()
    
# This function creates the dataset as a CSV file.   
def create_dataset(english_comment_csv, dataset_destination):

    en_comments = pd.read_csv(english_comment_csv, error_bad_lines=False, encoding='utf-8-sig')
    dataset = en_comments[['english_comment', 'first_reply','Replies', 'Likes']].copy()
    dataset.to_csv(dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')

def to_lower_case(df, header1, new_header):
    df[new_header] = df[header1].apply(lambda x:str(x).lower())
    return df

def regularize(df, header1, new_header, regex):
    df[new_header] = df[header1].apply(lambda x:test_com(x, regex))
    regularized_list = df[new_header]
    return df, regularized_list


def most_common_histogram(df, header, count):
    # unique = set(df[header].str.lower().str.split(' ').sum())
    words = []
    for comment in df[header]:
        words.append(comment.split(' '))
    unique_word_list = list(itertools.chain(*words))
    # Create counter
    count_of_words = collections.Counter(unique_word_list)
    
    most_common_comments = count_of_words.most_common(count)
    return most_common_comments, unique_word_list

def plot_histogram(histo_list, title):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    
    histo_list = pd.DataFrame(histo_list, columns=['words', 'count'])
    
    # Plot horizontal bar graph
    histo_list.sort_values(by='count').plot.barh(x='words',
                          y='count',
                          ax=ax,
                          color="purple")
    
    ax.set_title(title)
    
    plt.show()

# Helper Function
def test_com(x, regex):
    try: 
        print(x)
        x = re.sub(regex," ",x)
        
        # remove multi-spaces
        x = ' '.join(x.split())
    except:
        x = ''
    return x 

def contraction_removal():
       
    from pycontractions import Contractions
    import gensim.downloader as api
    # model = api.load("glove-twitter-25")
    # model = api.load("glove-twitter-100")
    model = api.load("word2vec-google-news-300")

    cont = Contractions(kv_model=model)
    cont.load_models()
    # cont = Contractions('GoogleNews-vectors-negative300.bin')
    
def expand_contractions(text, cont):
    """expand shortened words, e.g. don't to do not"""
    text_list = list(cont.expand_texts([text], precise=True))
    text = text_list[0]
    return text





    