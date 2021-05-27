import random

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
COMMON_RANDOM_POSTFIX = f"{random.randint(1,100000):05}"
DEFAULT_RESOURCE_GROUP_NAME = "IoT-project"
DEFAULT_IOT_HUB_NAME = f"iot-hub-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_COSMOSDB_NAME = f"cosmosdb-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_APP_SRV_PLAN_NAME = f"ASP-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_STORAGE_ACC_NAME = f"storage0materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_FUNCTIONS_NAME = f"functions-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_EVENT_HUB_NAMESPACE = f"event-hub-namespace-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_EVENT_HUB_NAME = f"event-hub-materialfluss{COMMON_RANDOM_POSTFIX}"
DEFAULT_LOCATION = "North Europe"
