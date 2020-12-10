# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 21:05:55 2020

@author: Eric Bianchi
"""

"""
First tokenize the unique words in the comments without replies. 

Second tokenize the unique words in the comments with replies.

"""
import os
import csv
import pandas as pd
from youtubeAPI_5 import*

char_list = ['(', ')', '{', '}', '"', '*', '.', ',', '!', '?', ':', '\r', '\n']
comment_no_replies_dest = 'C://Users/Eric Bianchi/Desktop/csv_files/validation/Childish Gambino - \
This Is America (Official Video)_refined_validation.csv'

comment_with_replies_dest = 'C://Users/Eric Bianchi/Desktop/csv_files/Childish Gambino - \
This Is America (Official Video)_refined.csv'

comments_no_replies = pd.read_csv(comment_no_replies_dest, error_bad_lines=False, encoding='utf-8-sig')
val_comments = comments_no_replies['no_space_comment']

comments_with_replies = pd.read_csv(comment_with_replies_dest, error_bad_lines=False, encoding='utf-8-sig')
train_comments = comments_with_replies['no_space_comment']
                                       
len_list_comment = get_sentence_length_histo(comments_with_replies, 'no_space_comment', 'deepskyblue')
                                      
len_list_reply = get_sentence_length_histo(comments_with_replies, 'no_space_reply', 'gold')

labels = ['Comment',"Reply"]
plt.legend(labels)
plt.xlabel("Length of comment or reply")
plt.ylabel("Proportion")
plt.title("Comparing the distribution of the number of words in 'Comments' and 'Replies'")
'''
most_com_val, val_comment_vocabulary = top_n_words(comments_no_replies, 'no_space_comment', 25, char_list)
most_com_train, train_comment_vocabulary = top_n_words(comments_with_replies, 'no_space_comment', 25, char_list)   

plot_histogram(most_com_val, 'validation - comment top 25 words (stop words included)')
plot_histogram(most_com_train, 'training - comment top 25 words (stop words included)') 

most_com_train, train_comment_vocabulary = top_n_words(comments_with_replies, 'no_space_reply', 25, char_list) 

plot_histogram(most_com_train, 'training - reply top 25 words (stop words included)')

vocabulary_union = []
vocabulary_difference = []

for word in val_comment_vocabulary:
    if word in train_comment_vocabulary:
        vocabulary_union.append(word)
    else:
        vocabulary_difference.append(word)

val_comment_vocab_check = []

save_csv_location = 'C://Users/Eric Bianchi/Desktop/csv_files/validation/Childish Gambino - \
This Is America (Official Video)_validation_comments_top_n.csv'

with open(save_csv_location, 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Validation Comment', 'Validation Reply']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for sentence in val_comments:
        individual_words = sentence.split()
        if any(item in vocabulary_difference for item in individual_words):
            continue
        else:
            val_comment_vocab_check.append(sentence)
            writer.writerow({'Validation Comment': sentence, 'Validation Reply':'no reply'})
        
    
print('here')
#dataset.to_csv(new_dataset_destination, index = False, line_terminator='\n', encoding='utf-8-sig')

'''