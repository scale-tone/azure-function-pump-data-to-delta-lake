# azure-function-pump-data-to-delta-lake

An Azure Function to pump events from an Azure Service Bus queue/topic into a [Delta Lake table in Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/delta/).

Uses [Databricks Connect client library](https://docs.databricks.com/dev-tools/databricks-connect.html#step-1-install-the-client) to connect to your cluster, therefore is written in Python. Needs to be containerized, to maintain the correct list of dependencies.
WARNING: may not work locally on your devbox (especially on Windows).

The function expects each message to be a JSON representation of a record to be appended, e.g. `{"my-field1":"my-value", "my-field2": 12345}`. Field names and types must match the schema of your table. Table must pre-exist.

# Config Settings

The following settings need to be configured in your Function App instance.

* `DATABRICKS_ADDRESS`, `DATABRICKS_API_TOKEN`, `DATABRICKS_CLUSTER_ID`, `DATABRICKS_ORG_ID` - connection parameters to communicate with your Azure Databricks cluster. [See here on how and where to get them](https://docs.databricks.com/dev-tools/databricks-connect.html#step-2-configure-connection-properties).

* `SERVICEBUS_CONN_STRING` - connection string to your Azure Service Bus namespace.
* `INPUT_QUEUE_NAME` - name of your input queue
  
  OR
  
* `INPUT_TOPIC_NAME`, `INPUT_SUBSCRIPTION_NAME` - names of your topic and subscription. Specify either queue name or topic/subscription names, not both.
* `OUTPUT_TABLE_NAME` - name of your Delta Lake table, e.g. `default.my-table`.

# How to deploy to Azure

[Exactly as described here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python#create-and-configure-a-function-app-on-azure-with-the-image).
