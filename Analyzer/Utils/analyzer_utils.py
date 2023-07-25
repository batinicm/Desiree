import re

import pandas
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from . import vault_utils
from Model.track_class import Track


# Preprocess lyrics to eliminate part of song annotations (verse, chorus, singer...)
# and additional details at the beginning of the song
def process_lyrics_for_analysis(lyrics):
    cleaned_lyrics = re.sub("\[.*\]", "", lyrics)
    cleaned_lyrics = cleaned_lyrics.split("\n")
    return ".".join(cleaned_lyrics[1:- 1])


# Remove duplicate songs (recognized by the same spotify guid)
# Remove rows which have empty 'Lyrics' column
# Prepare lyrics for analysis
def prepare_scraped_lyrics_for_analysis(tracks):
    dataframe = pandas.DataFrame(map(Track.to_dict, tracks))
    dataframe.drop_duplicates(subset=['SpotifyId'], inplace=True)
    dataframe['Lyrics'].str.strip()
    dataframe.drop(dataframe[dataframe['Lyrics'] == ""].index, inplace=True)
    dataframe['Lyrics'] = list(map(process_lyrics_for_analysis, dataframe['Lyrics']))

    return dataframe


def prepare_kaggle_lyrics_for_analysis(lyrics):
    lyrics['Lyrics'].str.strip()
    lyrics.drop(lyrics[lyrics['Lyrics'] == ""].index, inplace=True)
    lyrics['Lyrics'] = list(map(process_lyrics_for_analysis, lyrics['Lyrics']))

    return lyrics


def get_max_score_sentiment(l):
    if (l.confidence_scores.positive >= l.confidence_scores.negative) and (
            l.confidence_scores.positive >= l.confidence_scores.neutral):
        return "positive"
    elif (l.confidence_scores.negative >= l.confidence_scores.positive) and (
            l.confidence_scores.negative >= l.confidence_scores.neutral):
        return "negative"
    else:
        return "neutral"


def analyze_text(lyrics):
    endpoint = vault_utils.get_secret("LanguageAnalyzerEndpoint")
    key = vault_utils.get_secret("LanguageAnalyzerKey")
    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))

    sentiments = list()
    for entity in lyrics:
        result = text_analytics_client.analyze_sentiment([entity["Lyrics"]], show_opinion_mining=True)
        lyric_result = [l for l in result if not l.is_error]

        if len(lyric_result) == 0:
            sentiments.append("neutral")
        else:
            sentiments.append(get_max_score_sentiment(lyric_result[0]))

    return zip(lyrics, sentiments)


def extract_key_phrases(lyrics):
    endpoint = vault_utils.get_secret("LanguageAnalyzerEndpoint")
    key = vault_utils.get_secret("LanguageAnalyzerKey")
    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))

    phrases = list()
    for entity in lyrics:
        result = text_analytics_client.extract_key_phrases([entity["Lyrics"]])

        if len(result) == 0:
            phrases.append([])
        else:
            phr = result[0]
            if not phr.is_error:
                phrases.append(result[0].key_phrases)
            else:
                phrases.append([])

    return zip(lyrics, phrases)

