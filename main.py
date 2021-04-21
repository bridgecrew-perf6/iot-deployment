import argparse
import random

# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential

from provisioning import resource_group, iot_hub


# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
DEFAULT_RESOURCE_GROUP_NAME = "IoT-project"
DEFAULT_LOCATION = "northeurope"
DEFAULT_IOT_HUB_NAME = f"iot-hub-materialfluss{random.randint(1,100000):05}"


def main(args: argparse.Namespace):
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()

    # Step 1: Provision the resource group.
    resource_group.provision(
        credential, args.azure_subscription_id, args.resource_group_name, args.location
    )

    # Step 2: Provision the IotHub.
    iot_hub.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.location,
    )

    # Step 3: Onboard & provision default IoT devices.


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "azure_subscription_id", type=str, help="Azure subscription ID."
    )
    parser.add_argument(
        "--resource-group-name",
        type=str,
        default=DEFAULT_RESOURCE_GROUP_NAME,
        help="Resource group name for the deployment.",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help="Location of the Azure datacenter to deploy.",
    )
    parser.add_argument(
        "--iot-hub-name",
        type=str,
        default=DEFAULT_IOT_HUB_NAME,
        help="IotHub name for deployment.",
    )
    main(parser.parse_args())
