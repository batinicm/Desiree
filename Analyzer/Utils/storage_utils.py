import collections.abc

import pandas
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient

from Model import constants
from . import vault_utils


def get_table_client(table_name):
    connection_string = vault_utils.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    return table_service_client.get_table_client(table_name=table_name)


def get_blob_client(container_name, blob_name):
    connection_string = vault_utils.get_secret("StorageAccountConnectionString")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    return blob_service_client.get_blob_client(container_name, blob_name)


def check_storage_created(table_name):
    table_client = get_table_client(table_name)
    entities = table_client.query_entities(query_filter="PartitionKey ne ''", results_per_page=1)
    return len(list(entities)) != 0


def delete_entities(table_name):
    table_client = get_table_client(table_name)
    entities = table_client.query_entities(query_filter="PartitionKey ne ''")

    for entity in entities:
        table_client.delete_entity(entity["PartitionKey"], entity["RowKey"])


def store_transaction(table_name, operation):
    print("Store started.")

    table_client = get_table_client(table_name)
    table_client.submit_transaction(operation)

    print("Store done.")


def get_from_storage(table_name):
    table_client = get_table_client(table_name)
    return table_client.query_entities(query_filter="PartitionKey ne ''")


def get_from_blob(container_name, blob_name):
    blob_client = get_blob_client(container_name, blob_name)
    return blob_client.download_blob().readall()


def get_partition_key(artists):
    artist = artists if type(artists) is str else next(iter(artists or []))
    artist = artist.replace('\\', '')
    artist = artist.replace('/', '')
    return artist


# Partition key: first artist name
# Row key: song spotify id - from the class itself (id.name? for easier search?)
def create_lyric_table_operation(track_row):
    track_info = track_row[1]
    return ('upsert', {
        u'PartitionKey': get_partition_key(track_info['Artists']),
        u'RowKey': track_info['SpotifyId'].replace('/', ''),
        u'Name': track_info['Name'],
        u'Artists': track_info['Artists'] if type(track_info['Artists']) is str else ",".join(track_info['Artists']),
        u'Lyrics': track_info['Lyrics']
    })


# Store song with lyrics in Azure Storage Account
def store_lyrics(tracks):
    operations = pandas.DataFrame()
    operations['PartitionKey'] = list(map(get_partition_key, tracks['Artists']))
    operations['RowKey'] = list(tracks['SpotifyId'].replace('/', ''),)
    operations['Operation'] = list(map(create_lyric_table_operation, tracks.iterrows()))

    grouped = operations.groupby(['PartitionKey', 'RowKey']).agg(list)

    for _, group in grouped.iterrows():
        store_transaction(constants.LYRICS_TABLE_NAME, group['Operation'])


def store_sentiment(sentiments):
    table_client = get_table_client(constants.SENTIMENT_TABLE_NAME)

    for lyrics, sentiment in sentiments:
        entity = {
            'PartitionKey': lyrics['PartitionKey'],
            'RowKey': lyrics['RowKey'],
            'Name': lyrics['Name'],
            'Sentiment': sentiment
        }
        table_client.create_entity(entity)


def store_phrases(phrases):
    table_client = get_table_client(constants.PHRASES_TABLE_NAME)

    for lyrics, phrase in phrases:
        entity = {
            'PartitionKey': lyrics['PartitionKey'],
            'RowKey': lyrics['RowKey'],
            'Name': lyrics['Name'],
            'Phrases': ",".join(phrase)
        }
        table_client.create_entity(entity)


def store_tokens(tokens_df):
    table_client = get_table_client(constants.TOKENS_TABLE_NAME)

    for _, row in tokens_df.iterrows():
        entity = {
            'PartitionKey': row['PartitionKey'],
            'RowKey': row['RowKey'],
            'Name': row['Name'],
            'Tokens': ",".join(row['Tokens'])
        }
        table_client.create_entity(entity)
