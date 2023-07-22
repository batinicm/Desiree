from azure.data.tables import TableServiceClient
import vault_utils


def get_table_client(table_name):
    connection_string = vault_worker.get_secret("StorageAccountConnectionString")
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
