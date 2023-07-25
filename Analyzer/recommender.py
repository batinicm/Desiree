# Create a recommender which will take a song id (spotify id or name and artist) and its lyrics
# And recommend a song which has the same sentiment and most similar content

# Steps:
#   1. Prepare existing data for processing (TODO: check what needs to be done)
#   2. Take labeled data (from azure storage)
#   3. Do tokenization - TODO: stored data could already be pre-processed so storage contains vectors?
#    That way we don't waste compute time every time we need to do recommendation
#   4. Calculate similarity between input data and existing data
#   5. Return top 10 songs with greatest similarity
import pandas
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from Utils import storage_utils
from Model import constants


def process_stored_data_for_tokenization(sentiments, phrases):
    # Join lyrics and phrases and create frame like:
    #   PartitionKey(artist name)
    #   RowKey(spotify id)
    #   Name
    #   ForTokenization (sentiment + key phrases)
    sentiment_df = pandas.DataFrame(sentiments)
    phrases_df = pandas.DataFrame(phrases)

    joined = pd.merge(sentiment_df, phrases_df, how='left', on=['PartitionKey', 'RowKey', 'Name'])
    joined['ForTokenization'] = joined['Sentiment'].str.cat(joined['Phrases'], sep=",")
    joined.drop(['Sentiment', 'Phrases'], axis=1, inplace=True)

    return joined


# def recommend():
# For recommendation: tokenize all data, find similarities matrix for other songs and put out top 10 songs
# ranked by similarity with the input song
# similarities = cosine_similarity(tfidf_matrix)


# General flow of action:
# search for song name and artist - through spotify api get id
# check if song already present in data TODO: see if you can store recommendation results - like spotify ids or similar
# scrape for lyrics
# get sentiment and key phrases
# store sentiment and phrases for future use
# use sentiment and key phrases to do tokenization for recommendation
# churn out top 10 recommended songs spotify id
# put into queue/playlist/play next and display on webpage
if __name__ == '__main__':
    stored_sentiments = storage_utils.get_from_storage(constants.SENTIMENT_TABLE_NAME)
    stored_phrases = storage_utils.get_from_storage(constants.PHRASES_TABLE_NAME)

    stored_data = process_stored_data_for_tokenization(stored_sentiments, stored_phrases)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(stored_data['ForTokenization'])

    similarities = cosine_similarity(tfidf_matrix)
    similarities_indexed = pd.DataFrame(similarities, columns=stored_data['RowKey'],
                                        index=stored_data['RowKey']).reset_index()

    #TODO: find top 10 similarities for all songs in the database and store them in the storage
    test_song = "4RvWPyQ5RL0ao9LPZeSouE"
    recommendations = pd.DataFrame(similarities_indexed.nlargest(11, test_song)['RowKey'])
    recommendations = recommendations[recommendations['RowKey'] != test_song]

