# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.9

### Need to install Java (as it is not installed by default in this Python container)
RUN apt install default-jre -y

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot

# Otherwise DataBricks Connect expects an exact match between client and cluster versions
ENV DEBUG_IGNORE_VERSION_MISMATCH=1

# Need to override the startup script, to copy the correct function.json based on whether a queue or a topic is chosen as input
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh
CMD [ "/startup.sh" ]