# youtube NLP
Youtube Comment Generator

Final Project for Deep Learning ECE 6554 (Virginia Tech)

**Objectives:**
1. Using Kaggle Youtube dataset, train a sentiment analyzer.
2. Use trained analyzer on youtube comments/replies gathered from video.
2. Generate fake comments based on existing comments from videos, using a sample word. (Train ~100-200 comments)
2. Generate fake replies to comments based on existing replies from videos, using a sample comment input. (sample ~100-200 replies)
3. Use sentiment from comments to augment the reply. Uses a sample word and a sample sentiment. (Train on ~100-200 comments


**Final operations run on CSV file, fina and replace bad unicode text**
* â€œ = " (beginning quote)
* â€™ = ' (apostrophe)
* â€ = " (end quote)
* œ = (replace with nothing.)

**Get the first n words from cell in excel spread sheet**
=TRIM(LEFT(A2, FIND("~",SUBSTITUTE(A2, " ", "~",3)&"~")))

**Run the program**
- Use the run-file to run all the functions in Youtube_5


![alt text](https://github.com/beric7/youtube_NLP/blob/main/Figure%201.png)
![alt text](https://github.com/beric7/youtube_NLP/blob/main/Figure%202.png)
