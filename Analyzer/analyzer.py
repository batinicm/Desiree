# Analyze initial corpus of song lyrics to have for app startup
# 1. Get song lyrics for current top 40, 80s, 90s, 00s and 10s classics
# 2. Analyze song lyrics and assign sentiment to them
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import vault_worker


# if __name__ == '__main__':



def analyze_text(text):
    endpoint = vault_worker.get_secret("LanguageAnalyzerEndpoint")
    key = vault_worker.get_secret("LanguageAnalyzerKey")

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
