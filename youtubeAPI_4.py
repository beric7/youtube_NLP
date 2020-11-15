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
from langdetect import detect
import re   # regular expression
from tqdm import tqdm

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
def query_results(query):
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

# This is the function that extracts comments. The extraction puts all the comments
# into an array which can be later turned into a CSV file. This would be better suited, 
# due to memory contraints if they were added directly to the CSV file as it was 
# being read, this way we do not have to store the text in the CPU memory. 
def extract_comments(video_id, channel, video_title, video_desc, save_csv_location):
    comments_pop = []
    reply_count_pop = []
    like_count_pop = []
    
    comments_temp = []
    reply_count_temp = []
    like_count_temp = []
    nextPage_token = None
    count = 0
    
    
    with open(save_csv_location, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Comment', 'Replies', 'Likes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()


        while 1:
          response = service.commentThreads().list(
                            part = 'snippet',
                            videoId = video_id,
                            maxResults = 100, 
                            order = 'time', 
                            textFormat = 'plainText',
                            pageToken = nextPage_token
                            ).execute()
          nextPage_token = response.get('nextPageToken')
          
          for item in response['items']:
              writer.writerow({'Comment': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                               'Replies': item['snippet']['totalReplyCount'],
                               'Likes': item['snippet']['topLevelComment']['snippet']['likeCount']})        
              count = count + 1
          print(count)
          if nextPage_token is None or count > 100:
            break
    

# This function removes emojis 
def remove_emojis(csv_file):
    comments = pd.read_csv(csv_file, encoding='utf-8-sig')
    demoji.download_codes()
    comments['clean_comments'] = comments['Comment'].apply(lambda x: demoji.replace(x,""))
    return comments

# This function only shows english comments. 
def show_english_only(comments, save_location, english_comment_csv, query):
    comments['language'] = 0
    count = 0
    for i in tqdm(range(0,len(comments))):
    
    
      temp = comments['clean_comments'].iloc[i]
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

# This function removes special characters, BUT is not included in the data
# pruning process since special characters are important to use. 
def remove_special_characters(english_comment_csv):
    en_comments = pd.read_csv(english_comment_csv, error_bad_lines=False, encoding='utf-8-sig')
    en_comments.shape
    
    # regex = r"[^0-9A-Za-z'\t]"
    
    copy = en_comments.copy()
    
    copy['reg'] = copy['clean_comments'].apply(lambda x:re.findall(regex,x))
    copy['regular_comments'] = copy['clean_comments'].apply(lambda x:re.sub(regex,"  ",x))
    
    return copy

# This function creates the dataset as a CSV file.   
def create_dataset(english_comment_csv, dataset_destination):
    """
    'Channel': channel_pop,
    'Video Title': video_title_pop,
    'Video Description': video_desc_pop,
    'Video ID': video_id_pop,
    'Comment': comments_pop,
    'Comment ID': comment_id_pop,
    'Replies': reply_count_pop,
    'Likes': like_count_pop,
    """
    en_comments = pd.read_csv(english_comment_csv, error_bad_lines=False, encoding='utf-8-sig')
    dataset = en_comments[['clean_comments', 'Replies', 'Likes']].copy()
    dataset.to_csv(dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    
    # WHERE WE ARE SAVING THE OUTPUT FILE.
    save_location = 'C://Users/Eric Bianchi/Desktop/'
    #
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service(save_location)

    query = "Childish Gambino - This Is America (Official Video)"
    save_csv_location = save_location + query + '.csv'
    english_comment_csv = save_location + query + '_EN.csv'
    dataset_destination = save_location + query + '_cleaned_dataset.csv'
    
    query_results = query_results(query)
    video_id, channel, video_title, video_desc = extract_video_details(query_results)
    extract_comments(video_id, channel, video_title, video_desc, save_csv_location)
    comments = remove_emojis(save_csv_location)
    english_comm = show_english_only(comments, save_location, english_comment_csv, query)

    create_dataset(english_comment_csv, dataset_destination)
    