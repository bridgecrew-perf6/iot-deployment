# Deployment using Azure Python SDK
The following steps of Azure service provisioning are executed by the deployment script:

1. Create a **resource group** for Azure resources of the IoT project,
2. Provision Azure **IotHub**,
3. Onboard & provision default **IoT devices**,
4. Provision a **CosmosDB** and initialize it,
5. Provision an **App Service Plan** for Azure Functions,
6. Provision a **Storage account** for Azure Functions,
7. Provision **Azure Functions** inside the ASP (app service plan),
8. Deploy the Azure **function apps**.

If also the OPC UA integration is deployed, then:

9. Provision the **EventHub namespace** and **EventHub** inside it,
10. Provision the **ServiceBus namespace**,
11. Provision the **Key Vault**,
12. Provision the **SignalR**,

If also Azure IIoT cloud modules are to be deployed into an existing K8s cluster, then:

13.  **Register** the Azure IIoT modules to Azure AAD and **deploy** the cloud modules into the `kubectl` kubernetes cluster.

***

* **Requires executing the following commands in any terminal** (check [installing dependencies](#installing-dependencies)):
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

## **Installing Dependencies:**
* Install Python3.7+ either system-wide, user-wide or as a virtual environment.
* Run `pip install pip-tools` command via the `pip` command associated with the installed Python.
* Run `pip-sync` inside the project root folder.
* Install **Azure CLI** from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli .
* If you want to deploy **OPC UA integration** as well, then:
  * Run `az extension add --name azure-iot` from any terminal.
  * Run `Install-Module powershell-yaml` in PowerShell.
  * Install and set up `kubectl` and `helm`. Also make sure they are **accessible from the PowerShell**.

## **Usage:**
    usage: main.py [-h] {deploy,onboard} ...

    optional arguments:
      -h, --help        show this help message and exit

    Subcommands:
      {deploy,onboard}
        deploy          Subcommand to provision the Azure infrastructure.
        onboard         Subcommand for batch device onboarding into the Azure
                        IotHub.

### `deploy` subcommand usage:
    usage: main.py deploy [-h] --azure-subscription-id AZURE_SUBSCRIPTION_ID
                          [--resource-group-name RESOURCE_GROUP_NAME]
                          [--iot-hub-name IOT_HUB_NAME]
                          [--device-ids-file-path DEVICE_IDS_FILE_PATH]
                          [--is-edge-device] --vendor-credentials-path
                          VENDOR_CREDENTIALS_PATH [--cosmosdb-name COSMOSDB_NAME]
                          [--app-srv-plan-name APP_SRV_PLAN_NAME]
                          [--storage-acc-name STORAGE_ACC_NAME]
                          [--functions-name FUNCTIONS_NAME]
                          [--functions-code-path FUNCTIONS_CODE_PATH]
                          [--location LOCATION]
                          [--event-hub-namespace EVENT_HUB_NAMESPACE]
                          [--event-hub-name EVENT_HUB_NAME]
                          [--service-bus-namespace SERVICE_BUS_NAMESPACE]
                          [--key-vault-name KEY_VAULT_NAME]
                          [--signalr-name SIGNALR_NAME]
                          [--iiot-app-name IIOT_APP_NAME]
                          [--iiot-repo-path IIOT_REPO_PATH]
                          [--aad-reg-path AAD_REG_PATH]
                          [--helm-values-yaml-path HELM_VALUES_YAML_PATH]
                          --tenant-id TENANT_ID
                          [--logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [--verbose]
                          {iiot,vanilla} ...

    optional arguments:
      -h, --help            show this help message and exit
      --azure-subscription-id AZURE_SUBSCRIPTION_ID
                            Azure subscription ID.
      --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the deployment.
      --iot-hub-name IOT_HUB_NAME
                            IotHub name for the deployment.
      --device-ids-file-path DEVICE_IDS_FILE_PATH
                            Path of the text file containing 1 device id per line
                            to be registered in IotHub.
      --is-edge-device      The flag for registering the devices as an iot edge
                            device in Azure IotHub.
      --vendor-credentials-path VENDOR_CREDENTIALS_PATH
                            Path to a JSON file containing credentials for each
                            device vendor server. The JSON object must be of the
                            following format: {"vendor1": {"endpoint_uri1":
                            {"x-api-key": API_KEY}, "endpoint_uri2": {"username":
                            USERNAME, "password": PASSWORD}}, ...}
      --cosmosdb-name COSMOSDB_NAME
                            Cosmos DB name for the deployment.
      --app-srv-plan-name APP_SRV_PLAN_NAME
                            App Service Plan name for the deployment.
      --storage-acc-name STORAGE_ACC_NAME
                            Storage account name for the deployment.
      --functions-name FUNCTIONS_NAME
                            Azure Functions name for the deployment.
      --functions-code-path FUNCTIONS_CODE_PATH
                            Path to the folder containing Azure Functions source
                            code. Be warned that '.git' folder will be erased!
      --location LOCATION   Location of the Azure datacenter for the deployment.
      --event-hub-namespace EVENT_HUB_NAMESPACE
                            Name of the EventHub namespace for the deployment.
      --event-hub-name EVENT_HUB_NAME
                            Name of the EventHub to provision inside the EventHub
                            namespace.
      --service-bus-namespace SERVICE_BUS_NAMESPACE
                            Name of the ServiceBus for the deployment.
      --key-vault-name KEY_VAULT_NAME
                            Name of the Key Vault for the deployment.
      --signalr-name SIGNALR_NAME
                            Name of the SignalR for the deployment.
      --iiot-app-name IIOT_APP_NAME
                            Name of the Azure IIoT app to be registered in AAD, as
                            '<app_name>-client', '<app_name>-web' and
                            '<app_name>-service'.
      --iiot-repo-path IIOT_REPO_PATH
                            Path to the Git repository of Azure IIoT. You can
                            clone it from https://github.com/Azure/Industrial-IoT.
                            If not given, then Azure IIoT modules will not be
                            deployed. But the required services will be deployed.
      --aad-reg-path AAD_REG_PATH
                            Path to the '.json' file to be created during the
                            registration of Azure IIoT modules in AAD. This file
                            will also be used to deploy the modules into 'kubectl'
                            kubernetes cluster. If not given, then Azure IIoT
                            modules will not be deployed. But the required
                            services will be deployed.
      --helm-values-yaml-path HELM_VALUES_YAML_PATH
                            Path to the 'values.yaml' to be created and to be used
                            by Helm during the deployment of Azure IIoT cloud
                            modules. If not given, then Azure IIoT modules will
                            not be deployed. But the required services will be
                            deployed.
      --tenant-id TENANT_ID
                            The Azure Active Directory tenant ID that should be
                            used for authenticating requests to the key vault.
      --logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Logging level of the program.
      --verbose, -v         The flag for whether there should be logging messages.

    Subcommands:
      For this command, no subcommand is also possible.

      {iiot,vanilla}
        iiot                Subcommand to register and deploy only Azure IIoT
                            cloud modules into an existing kubernetes cluster
                            (uses 'deploy-iiot.ps1').
        vanilla             Subcommand to deploy vanilla Azure infrastructure
                            (without OPC UA integration).

#### `deploy iiot` subcommand usages:
    usage: main.py deploy iiot [-h] [--resource-group-name RESOURCE_GROUP_NAME]
                               [--iot-hub-name IOT_HUB_NAME]
                               [--cosmosdb-name COSMOSDB_NAME]
                               [--storage-acc-name STORAGE_ACC_NAME]
                               [--event-hub-namespace EVENT_HUB_NAMESPACE]
                               [--event-hub-name EVENT_HUB_NAME]
                               [--service-bus-namespace SERVICE_BUS_NAMESPACE]
                               [--key-vault-name KEY_VAULT_NAME]
                               [--signalr-name SIGNALR_NAME]
                               [--iiot-app-name IIOT_APP_NAME] --iiot-repo-path
                               IIOT_REPO_PATH --aad-reg-path AAD_REG_PATH
                               --helm-values-yaml-path HELM_VALUES_YAML_PATH
                               [--logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                               [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the deployment.
      --iot-hub-name IOT_HUB_NAME
                            IotHub name for the deployment.
      --cosmosdb-name COSMOSDB_NAME
                            Cosmos DB name for the deployment.
      --storage-acc-name STORAGE_ACC_NAME
                            Storage account name for the deployment.
      --event-hub-namespace EVENT_HUB_NAMESPACE
                            Name of the EventHub namespace for the deployment.
      --event-hub-name EVENT_HUB_NAME
                            Name of the EventHub to provision inside the EventHub
                            namespace.
      --service-bus-namespace SERVICE_BUS_NAMESPACE
                            Name of the ServiceBus for the deployment.
      --key-vault-name KEY_VAULT_NAME
                            Name of the Key Vault for the deployment.
      --signalr-name SIGNALR_NAME
                            Name of the SignalR for the deployment.
      --iiot-app-name IIOT_APP_NAME
                            Name of the Azure IIoT app to be registered in AAD, as
                            '<app_name>-client', '<app_name>-web' and
                            '<app_name>-service'.
      --iiot-repo-path IIOT_REPO_PATH
                            Path to the Git repository of Azure IIoT. You can
                            clone it from https://github.com/Azure/Industrial-IoT.
      --aad-reg-path AAD_REG_PATH
                            Path to the '.json' file to be created during the
                            registration of Azure IIoT modules in AAD. This file
                            will also be used to deploy the modules into 'kubectl'
                            kubernetes cluster.
      --helm-values-yaml-path HELM_VALUES_YAML_PATH
                            Path to the 'values.yaml' to be created and to be used
                            by Helm during the deployment of Azure IIoT cloud
                            modules.
      --logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Logging level of the program.
      --verbose, -v         The flag for whether there should be logging messages.

#### `deploy vanilla` subcommand usage:
    usage: main.py deploy vanilla [-h] --azure-subscription-id
                                  AZURE_SUBSCRIPTION_ID
                                  [--resource-group-name RESOURCE_GROUP_NAME]
                                  [--iot-hub-name IOT_HUB_NAME]
                                  --device-ids-file-path DEVICE_IDS_FILE_PATH
                                  [--is-edge-device] --vendor-credentials-path
                                  VENDOR_CREDENTIALS_PATH
                                  [--cosmosdb-name COSMOSDB_NAME]
                                  [--app-srv-plan-name APP_SRV_PLAN_NAME]
                                  [--storage-acc-name STORAGE_ACC_NAME]
                                  [--functions-name FUNCTIONS_NAME]
                                  [--functions-code-path FUNCTIONS_CODE_PATH]
                                  [--location LOCATION]
                                  [--logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                  [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --azure-subscription-id AZURE_SUBSCRIPTION_ID
                            Azure subscription ID.
      --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the deployment.
      --iot-hub-name IOT_HUB_NAME
                            IotHub name for the deployment.
      --device-ids-file-path DEVICE_IDS_FILE_PATH
                            Path of the text file containing 1 device id per line
                            to be registered in IotHub.
      --is-edge-device      The flag for registering the devices as an iot edge
                            device in Azure IotHub.
      --vendor-credentials-path VENDOR_CREDENTIALS_PATH
                            Path to a JSON file containing credentials for each
                            device vendor server. The JSON object must be of the
                            following format: {"vendor1": {"endpoint_uri1":
                            {"x-api-key": API_KEY}, "endpoint_uri2": {"username":
                            USERNAME, "password": PASSWORD}}, ...}
      --cosmosdb-name COSMOSDB_NAME
                            Cosmos DB name for the deployment.
      --app-srv-plan-name APP_SRV_PLAN_NAME
                            App Service Plan name for the deployment.
      --storage-acc-name STORAGE_ACC_NAME
                            Storage account name for the deployment.
      --functions-name FUNCTIONS_NAME
                            Azure Functions name for the deployment.
      --functions-code-path FUNCTIONS_CODE_PATH
                            Path to the folder containing Azure Functions source
                            code. Be warned that '.git' folder will be erased!
      --location LOCATION   Location of the Azure datacenter for the deployment.
      --logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Logging level of the program.
      --verbose, -v         The flag for whether there should be logging messages.

### `onboard` subcommand usage:
    usage: main.py onboard [-h] --azure-subscription-id AZURE_SUBSCRIPTION_ID
                           --resource-group-name RESOURCE_GROUP_NAME
                           --iot-hub-name IOT_HUB_NAME --device-ids-file-path
                           DEVICE_IDS_FILE_PATH [--is-edge-device]
                           [--logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --azure-subscription-id AZURE_SUBSCRIPTION_ID
                            Azure subscription ID.
      --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the device onboarding.
      --iot-hub-name IOT_HUB_NAME
                            IotHub name for the device onboarding.
      --device-ids-file-path DEVICE_IDS_FILE_PATH
                            Path of the text file containing 1 device id per line
                            to be registered in IotHub.
      --is-edge-device      The flag for registering the devices as an iot edge
                            device in Azure IotHub.
      --logging-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Logging level of the program.
      --verbose, -v         The flag for whether there should be logging messages.
