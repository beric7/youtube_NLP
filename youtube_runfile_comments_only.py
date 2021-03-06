# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 11:13:15 2020

@author: Eric Bianchi
"""
import os
import csv
import pandas as pd
from youtubeAPI_5 import*
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.

CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# When running locally, disable OAuthlib's HTTPs verification. When
# running in production *do not* leave this option enabled.

# WHERE WE ARE SAVING THE OUTPUT FILE.
save_location = 'C://Users/Eric Bianchi/Desktop/csv_files/validation/'
'''
# Oauth
###############
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
service = get_authenticated_service(save_location)
###############
'''
# Save locations and parameters
# save_location = 'C://Users/Eric Bianchi/Desktop/csv_files/'
###############
query = "Childish Gambino - This Is America (Official Video)"
save_csv_t_location = save_location + query + '_time'+'.csv'
save_csv_r_location = save_location + query + '_rel' + '.csv'
save_csv_location = save_location + query + '.csv'
english_comment_csv = save_location + query + '_EN.csv'
dataset_destination = save_location + query + '_cleaned_dataset.csv'
number = 500
regex = r"^[^0-9A-Za-z'\t\n]"
char_list = ['(', ')', '{', '}', '"', '*', '.', ',', '!', '?', '\r', '\n']
# char_list_keyword = ['(', ')', '{', '}', '"', '*', '.', ',', '!', '?', ':']
###############

# query_results = query_results(query, service)
# video_id, channel, video_title, video_desc = extract_video_details(query_results)

# EXTRACT TIME AND RELEVANCE RESPONSES
'''
extract_comments_with_no_replies(video_id, channel, video_title, video_desc, save_csv_t_location, number, 'time', service)
extract_comments_with_no_replies(video_id, channel, video_title, video_desc, save_csv_r_location, number, 'relevance', service)
csv_time = pd.read_csv(save_csv_t_location, error_bad_lines=False, encoding='utf-8-sig')
csv_rel = pd.read_csv(save_csv_r_location, error_bad_lines=False, encoding='utf-8-sig')
concat_df = pd.concat([csv_rel,csv_time])
concat_df.to_csv(save_csv_location, index = False, line_terminator='\n', encoding='utf-8-sig')

# ONLY ENGLISH COMMENTS
print('only keeping english comments...')
english_comm = show_english_only(concat_df, save_location, english_comment_csv, query)
english_comm.to_csv(english_comment_csv, index = False, line_terminator='\n', encoding='utf-8-sig')

# DROP DUPLICATES
print('dropping duplicates...')
english_comm = pd.read_csv(english_comment_csv, error_bad_lines=False, encoding='utf-8-sig')
unique_df = english_comm.drop_duplicates(subset=['Comment'])
unique_df.to_csv(dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')
###############
'''
'''
df = pd.read_csv(dataset_destination, error_bad_lines=False, encoding='utf-8-sig')

print('lower case comments...')
df = to_lower_case(df, 'Comment', 'lowercase_comment')
df, regularized_comment_list = regularize(df, 'lowercase_comment', 'new_regularized_comment', regex)

print('spacing...')
df, spaced_comment_list = add_space(df, 'new_regularized_comment', 'spaced_comment', char_list)

print('reomve multi-spacing...')
df, no_multi_spaced_comment_list = remove_multi_space(df, 'spaced_comment', 'no_space_comment')

print('histograms...')
most_common_comments, unique_comment_word_list = most_common_histogram(df, 'no_space_comment', 50, char_list)
plot_histogram(most_common_comments, 'Common words found in comments with no replies for Childish Gambino')

df.to_csv(dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')
'''
dataset_destination = 'C://Users/Eric Bianchi/Desktop/csv_files/Childish Gambino - \
This Is America (Official Video)_refined.csv'

new_dataset_destination = 'C://Users/Eric Bianchi/Desktop/csv_files/Childish Gambino - \
This Is America (Official Video)__refined.csv'

old_dataset = pd.read_csv(dataset_destination, error_bad_lines=False, encoding='utf-8-sig')
dataset = old_dataset.copy()

character_to_remove = ':'
dataset, remove_character_column = remove_character(dataset, 'no_space_comment', character_to_remove)
dataset, remove_character_column = remove_character(dataset, 'no_space_reply', character_to_remove)

dataset = find_first_n_keywords(dataset, 'no_space_comment', 2, char_list)
dataset = find_first_n_words(dataset, 'no_space_comment', 2)

dataset.to_csv(new_dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')



