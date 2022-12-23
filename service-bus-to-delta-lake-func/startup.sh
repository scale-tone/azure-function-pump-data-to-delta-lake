#!/bin/sh

if [ -n "${INPUT_QUEUE_NAME}" ];
then
	cp -rf /home/site/wwwroot/ServiceBusTrigger/function-for-queue.json /home/site/wwwroot/ServiceBusTrigger/function.json
else
	cp -rf /home/site/wwwroot/ServiceBusTrigger/function-for-topic.json /home/site/wwwroot/ServiceBusTrigger/function.json
fi

/azure-functions-host/Microsoft.Azure.WebJobs.Script.WebHost