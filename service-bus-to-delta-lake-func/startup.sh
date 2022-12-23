#!/bin/sh

if [[ $INPUT_QUEUE_NAME ]];
then
	cp -rf /home/site/wwwroot/ServiceBusTest/function-for-queue.json /home/site/wwwroot/ServiceBusTest/function.json
else
	cp -rf /home/site/wwwroot/ServiceBusTest/function-for-topic.json /home/site/wwwroot/ServiceBusTest/function.json
fi

/azure-functions-host/Microsoft.Azure.WebJobs.Script.WebHost