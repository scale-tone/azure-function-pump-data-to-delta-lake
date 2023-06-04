#!/bin/sh

if [ -n "${EVENTHUB_CONN_STRING}" ];
then
	cp -rf /home/site/wwwroot/EventHubTrigger/function-for-eventhub.json /home/site/wwwroot/EventHubTrigger/function.json
fi

if [ -n "${SERVICEBUS_CONN_STRING}" ];
then

	if [ -n "${INPUT_QUEUE_NAME}" ];
	then
		cp -rf /home/site/wwwroot/ServiceBusTrigger/function-for-queue.json /home/site/wwwroot/ServiceBusTrigger/function.json
	else
		cp -rf /home/site/wwwroot/ServiceBusTrigger/function-for-topic.json /home/site/wwwroot/ServiceBusTrigger/function.json
	fi

fi

/azure-functions-host/Microsoft.Azure.WebJobs.Script.WebHost