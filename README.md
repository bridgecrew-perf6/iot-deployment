# Deployment using Azure Python SDK
The following steps of Azure service deployment are executed by the deployment script:

1. Create a resource group for Azure resources of the IoT project,
2. Deploy Azure IoTHub,
3. Onboard & provision default IoT devices,
4. **TODO: Add more steps!**

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
                [--location LOCATION] [--iot-hub-name IOT_HUB_NAME]
                azure_subscription_id

    positional arguments:
    azure_subscription_id
                            Azure subscription ID.

    optional arguments:
    -h, --help            show this help message and exit
    --resource-group-name RESOURCE_GROUP_NAME
                            Resource group name for the deployment.
    --location LOCATION   Location of the Azure datacenter to deploy.
    --iot-hub-name IOT_HUB_NAME
                            IotHub name for deployment.
