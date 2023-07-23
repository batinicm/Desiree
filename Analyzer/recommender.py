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
    sentiment_df = pandas.DataFrame(sentiments).drop(['Timestamp'], axis=1)
    phrases_df = pandas.DataFrame(phrases).drop(['Timestamp'], axis=1)

    joined = pd.merge(sentiment_df, phrases_df, how='left', on=['PartitionKey', 'RowKey', 'Name'])
    joined['ForTokenization'] = joined['Sentiment'].str.cat(joined['Phrases'], sep=",")
    joined.drop(['Sentiment', 'Phrases'], axis=1)

    return joined


if __name__ == '__main__':
    # Get stored data
    # Tokenize
    # Store tokenized data

    stored_sentiments = storage_utils.get_from_storage(constants.SENTIMENT_TABLE_NAME)
    stored_phrases = storage_utils.get_from_storage(constants.PHRASES_TABLE_NAME)

    stored_data = process_stored_data_for_tokenization(stored_sentiments, stored_phrases)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(stored_data['ForTokenization'])


    # For recommendation: tokenize input data, find similarities matrix for other songs and put out top 10 songs
    # ranked by similarity with the input song
    # similarities = cosine_similarity(tfidf_matrix)


