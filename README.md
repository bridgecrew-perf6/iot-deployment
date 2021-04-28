# Deployment using Azure Python SDK
The following steps of Azure service deployment are executed by the deployment script:

1. Create a **resource group** for Azure resources of the IoT project,
2. Deploy Azure **IotHub**,
3. Onboard & provision default **IoT devices**,
4. Provision a **CosmosDB** and initialize it,
5. Provision an **App Service Plan** for Azure Functions,
6. Provision a **Storage account** for Azure Functions,
7. Provision **Azure Functions** inside the ASP (app service plan),
8. Initialize the Azure **function apps**.

* **Requires executing the following commands in any terminal**:
  1. `az login` to login,
  2. `az account list -o table` to see subscriptions,
  3. `az account set --subscription="<SubscriptionId>"` to choose a subscription for deployment.
<!-- * **Requires**:
  * Setting up a service principal. Run the following sequence of commands in `powershell`:
    1. `az login` to login,
    2. `az account list -o table` to see subscriptions,
    3. `az account set --subscription="<SubscriptionId>"` to choose a subscription for deployment,
    4. `az ad sp create-for-rbac --name DeploymentPrincipal --role Contributor` to create a service principal with **Contributor** access level.
  * **TODO: Write more!** -->

* The subscription chosen in the terminal **must be the same** as the one provided as a command line argument to the deployment script.

## **Usage:**

    usage: main.py [-h] [--resource-group-name RESOURCE_GROUP_NAME]
                [--iot-hub-name IOT_HUB_NAME]
                [--device-ids-file-path DEVICE_IDS_FILE_PATH]   
                [--cosmosdb-name COSMOSDB_NAME]
                [--app-srv-plan-name APP_SRV_PLAN_NAME]
                [--storage-acc-name STORAGE_ACC_NAME]
                [--functions-name FUNCTIONS_NAME]
                [--functions-code-path FUNCTIONS_CODE_PATH]
                [--location LOCATION]
                [--logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                [--verbose]
                azure_subscription_id vendor_credentials_path

    positional arguments:
    azure_subscription_id
                            Azure subscription ID.
    vendor_credentials_path
                            Path to a JSON file containing credentials for each
                            device vendor server. The JSON object must be of the
                            following format: {"vendor1": {"endpoint_uri1":
                            {"x-api-key": API_KEY}, "endpoint_uri2": {"username":
                            USERNAME, "password": PASSWORD}}, ...}

    optional arguments:
    -h, --help            show this help message and exit
    --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the deployment.
    --iot-hub-name IOT_HUB_NAME
                            IotHub name for deployment.
    --device-ids-file-path DEVICE_IDS_FILE_PATH
                            Path of the text file containing 1 device id per line
                            to be registered in IotHub.
    --cosmosdb-name COSMOSDB_NAME
                            CosmosDB name for the deployment.
    --app-srv-plan-name APP_SRV_PLAN_NAME
                            App Service Plan name for the deployment.
    --storage-acc-name STORAGE_ACC_NAME
                            Storage account name for the deployment.
    --functions-name FUNCTIONS_NAME
                            Azure Functions name for the deployment.
    --functions-code-path FUNCTIONS_CODE_PATH
                            Path to the folder containing Azure Functions source
                            code. Be warned that '.git' folder will be erased!
    --location LOCATION   Location of the Azure datacenter to deploy.
    --logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Logging level of the program.
    --verbose, -v         The flag for whether there should be logging messages.
