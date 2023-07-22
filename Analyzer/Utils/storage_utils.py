import pandas
from azure.data.tables import TableServiceClient
import vault_utils
from analyzer import LYRICS_TABLE_NAME


def get_table_client(table_name):
    connection_string = vault_utils.get_secret("StorageAccountConnectionString")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    return table_service_client.get_table_client(table_name=table_name)


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


def get_partition_key(artists):
    artist = next(iter(artists or []))
    artist = artist.replace('\\', '')
    artist = artist.replace('/', '')
    return artist


# Partition key: first artist name
# Row key: song spotify id - from the class itself (id.name? for easier search?)
def create_lyric_table_operation(track_row):
    track_info = track_row[1]
    return ('upsert', {
        u'PartitionKey': get_partition_key(track_info['Artists']),
        u'RowKey': track_info['SpotifyId'],
        u'Name': track_info['Name'],
        u'Artists': ",".join(track_info['Artists']),
        u'Lyrics': track_info['Lyrics']
    })


# Store song with lyrics in Azure Storage Account
def store_lyrics(tracks):
    operations = pandas.DataFrame()
    operations['PartitionKey'] = list(map(get_partition_key, tracks['Artists']))
    operations['Operation'] = list(map(create_lyric_table_operation, tracks.iterrows()))

    grouped = operations.groupby('PartitionKey').agg(list)

    for _, group in grouped.iterrows():
        store_transaction(LYRICS_TABLE_NAME, group['Operation'])