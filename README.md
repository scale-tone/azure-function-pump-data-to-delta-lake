# azure-function-pump-data-to-delta-lake

An Azure Function to pump (stream) events to a [Delta Lake table in Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/delta/). Supports Azure Service Bus (queues/topics), Azure Event Hubs and Azure Storage Queues as input source. You can even combine all these three in one single Function App instance.

The function expects each message to be either a JSON or XML representation of a record to be appended.
JSON example: `{"my-field1":"my-value", "my-field2": 12345}`. 
XML example: `<my-message my-field1="my-value"><my-field2>12345</my-field2></my-message>`

Resulting field names and types must match the schema of your table. If they don't, specify a [JSONPath](https://github.com/dchester/jsonpath#jsonpath-syntax) expression to convert them on-the-fly.

Table must pre-exist.

Uses [Databricks Connect client library](https://docs.databricks.com/dev-tools/databricks-connect.html#step-1-install-the-client) to connect to your cluster, therefore is written in Python. Needs to be containerized, to maintain the correct list of dependencies.
WARNING: may not work locally on your devbox (especially on Windows).

# Config Settings

The following settings need to be configured in your Function App instance.

## Output settings (required)

* `DATABRICKS_ADDRESS`, `DATABRICKS_API_TOKEN`, `DATABRICKS_CLUSTER_ID`, `DATABRICKS_ORG_ID` - connection parameters to communicate with your Azure Databricks cluster. [See here on how and where to get them](https://docs.databricks.com/dev-tools/databricks-connect.html#step-2-configure-connection-properties).
* `OUTPUT_TABLE_NAME` - name of your Delta Lake table, e.g. `default.my-table`.

## Service Bus input settings (if you use Service Bus)

* `SERVICEBUS_CONN_STRING` - connection string to your Azure Service Bus namespace.
* `SERVICEBUS_QUEUE_NAME` - name of your input queue
  
  OR
  
* `SERVICEBUS_TOPIC_NAME`, `SERVICEBUS_SUBSCRIPTION_NAME` - names of your topic and subscription. Specify either queue name or topic/subscription names, not both.

* (optional) `SERVICEBUS_JSONPATH_QUERY` - a [JSONPath](https://github.com/dchester/jsonpath#jsonpath-syntax) expression to be applied to each message. Use it if your messages (either JSON or XML) do not match your table's schema.

## Event Hubs input settings (if you use Event Hubs)

* `EVENTHUB_CONN_STRING` - connection string to your Event Hubs namespace.
* `EVENTHUB_NAME` - name of your input event hub.
* (optional) `EVENTHUB_JSONPATH_QUERY` - a [JSONPath](https://github.com/dchester/jsonpath#jsonpath-syntax) expression to be applied to each message. Use it if your messages (either JSON or XML) do not match your table's schema.

## Storage queues input settings (if you use Storage Queues)

* `STORAGE_CONN_STRING` - connection string to your Azure Storage account.
* `STORAGE_QUEUE_NAME` - name of your input Storage queue.
* (optional) `STORAGE_JSONPATH_QUERY` - a [JSONPath](https://github.com/dchester/jsonpath#jsonpath-syntax) expression to be applied to each message. Use it if your messages (either JSON or XML) do not match your table's schema.

# How to deploy to Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fscale-tone%2Fazure-function-pump-data-to-delta-lake%2Fmain%2Farm-template.json)

The above button will deploy [this container](https://hub.docker.com/r/scaletone/azurefunctionpumpdatatodeltalake) to a newly created Azure Functions instance (Premium plan).

Alternatively you can fork this repo and deploy it [exactly as described here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python#create-and-configure-a-function-app-on-azure-with-the-image).

# Performance

Test setup: 
* Function App instance in Premium tier locked to 2 EP2 instances (2 vCPU, 7GB memory each).
* 3-node cluster (4 cores, 14 GB memory each).
* Service Bus queue with Standard pricing tier, not partitioned.
* Event Hub with 2 partitions, Standard pricing tier.
* Storage queue in a General Purpose V2 Storage account.
* 30000 messages of ~100 bytes each.

The following results were registered:

* **Via a Service Bus queue**:  **215** messages per second.
* **Via an Event Hub**:  **230** messages per second.
* **Via a Storage Queue**:  **75** messages per second.
