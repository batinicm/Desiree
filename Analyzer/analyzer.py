# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import vault_worker


# if __name__ == '__main__':


# TODO: Use Spotify API to get playlist contents (aka songs in playlists)
# Dedupe song names
# Use song names (and artists?) to retrieve lyrics from Genius
# Do sentiment analysis (and everything else that seems valuable - opinion mining etc, just to enhance user experience)
# on retrieved lyrics
# ? Store result in Azure storage account for that

def analyze_text(text):
    endpoint = vault_worker.get_secret("LanguageAnalyzerEndpoint")
    key = vault_worker.get_secret("LanguageAnalyzerKey")

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
