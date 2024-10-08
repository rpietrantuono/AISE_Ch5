
# Example of deployment on Container App Azure

This example demonstrates deploying an application using the Azure Container App service. Specifically, we'll be able to show you how to push a Docker image to the Azure Container Registry, deploy the application, and access it using Postman.





## Installation Azure CLI

On Windows (using PowerShell as administrator)

```
  $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; Remove-Item .\AzureCLI.msi
```

On macOS

```
  brew update && brew install azure-cli
```

On Ubuntu\Debian
```
  sudo sh ./install_az_cli.sh
```

Azure CLI Login 
```
  az login
  #follow the instructions on the browser
```

## Create a Private Container Registry

Azure manages and deploys resources within logical containers called Resource Groups. This allows us to group related resources for easier management. 

```
  #--name: is the name of the resource group
  #--location: specifies the geographical region for the resources

  az group create --name AISErg --location italynorth
```

Let's proceed with creating the Container Registry


```
  #--name: is the name of the Registry
  #--sku: is the type of registry. Basic is the cheapest solution, ideally for learning

  az acr create --resource-group AISErg --name aisecr --sku Basic
```

Log in to the registry before pushing or pulling container images

```
  az acr login --name aisecr
```


## Build Docker Image

Before deploying a container app, we need an application to deploy. The 'flakeexample' directory provides a skeleton application that returns a list of random numbers when requested for a forecast.


Docker containers are instantiated from Docker images. A Docker image, defined by a Dockerfile, is a portable executable file that contains everything needed to run a container. It can be shared and distributed like a software binary. 
The flakeexample directory contains the Dockerfile for building the Docker image. 

```
  cd flakeexample
  docker build -t flakeexample:local .
```

## Run Application Locally

```
  docker run --rm -it -p 2557:5000 flakeexample:local
```

## Example of request

```
  curl -X POST http://127.0.0.1:2557/forecast -H "Content-Type: application/json" -d '{"store_number": 10, "forecast_start_date": "2023-07-01T00:00:00"}' 
```
## Push Image to the Azure Container Registry

Before pushing, we have to tag the docker image with the fully qualified name of our Registry

```
  #docker tag <DOCKER IMAGE> <Container Registry name>.<Resource Group Name>.io/<Image Name on the registry>

  docker tag flakeexample:local aisecr.azurecr.io/flakeexample:v1
```

Push the Image
```
  docker push <Container Registry name>.<Resource Group Name>.io/<Image Name on the registry>
  docker push aisecr.azurecr.io/flakeexample:v1
```

Show all the images pushed on the registry

```
  az acr repository list --name aisecr --output table
``` 

## Deploy Container App

First, we have to install the container app extension for the CLI


```
  az extension add --name containerapp --upgrade
  az provider register --namespace Microsoft.App
  az provider register --namespace Microsoft.OperationalInsights
```
To deploy container apps, first create a Container environment. A Container environment is a secure boundary that groups container apps in Azure Container Apps. Deploying apps to the same environment shares resources like virtual networks and Log Analytics workspaces

```
  az containerapp env create --name AISEcaenv --resource-group AISErg --location italynorth
```

For pulling the image from the Azure Container Registry, we need to create an access key for authentication. 

First, we enable admin mode on the registry

```
  az acr update -n aisecr --admin-enabled true
```

Finally, we get the credentials

```
  az acr credential show --name aisecr
```

This command displays the username and two passwords required to pull the image and deploy it to the container app.

Let's deploy

```
  #-n: the name of the Containerapp
  #-g: the resource group
  #-image: container Image
  #--evironment: name or resource ID of the container app's environment
  #--cpu: required CPU in cores
  #--memory: required memory
  #--min-replicas: the minimum number of replicas
  #--max-replicas: the maximum number of replicas
  #--ingress: ingress type (internal or external)
  #--target-port: the application port used for ingress traffic.

  #Note: To make the application accessible from a public IP, we need to configure an external ingress.
  #      The target port on the ingress should be the same as the port exposed by the application,
  #      which is specified in the Dockerfile.

  az containerapp create -n flakeexampleapp -g AISErg --image aisecr.azurecr.io/flakeexample:v1 --environment AISEcaenv --cpu 0.5 --memory 1.0Gi --min-replicas 1 --max-replicas 2 --ingress external --target-port 5000 --registry-server aisecr.azurecr.io --registry-username <USERNAME> --registry-password <PASSWORD>
```


## Getting the FQDN (Fully Qualified Domain Name)

To access the application (for example from PostMan) we need the url. 

```
  az containerapp show --resource-group AISErg --name flakeexampleapp --query properties.configuration.ingress.fqdn
```


## Sending a request using Postman

![alt text](https://github.com/CristianMascia/AISE_Ch5/blob/main/postman.png?raw=true)
