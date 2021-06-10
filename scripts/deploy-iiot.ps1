# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
# az login
# az extension add --name azure-iot
# Install-Module powershell-yaml
param(
    [string] $RGName = "IoT-project",
    [string] $IotHubName = "iot-hub-materialfluss",
    [string] $CosmosDBName = "cosmosdb-materialfluss",
    [string] $StorageAccName = "storage0materialfluss",
    [string] $EvHubNamespace = "event-hub-namespace-materialfluss",
    [string] $EvHubName = "event-hub-materialfluss",
    [string] $SerBusNamespace = "service-bus-namespace-materialfluss",
    [string] $KeyVaultName = "key-vault-materialfluss",
    [string] $SignalRName = "signalr-materialfluss",
    [string] $IIoTAppName = "azure-iiot-materialfluss",
    # "D:\Users\deniz\Desktop\masters\COURSES\SS2021\IDP\IoT\development\repos\Industrial-IoT"
    [Parameter(Mandatory = $true)] [string] $IIoTRepoPath,
    # "D:\Users\deniz\Desktop\masters\COURSES\SS2021\IDP\IoT\development\Azure\IIoT\aad.json"
    [Parameter(Mandatory = $true)] [string] $AadRegPath,
    # "D:\Users\deniz\Desktop\masters\COURSES\SS2021\IDP\IoT\development\Azure\IIoT\values.yaml"
    [Parameter(Mandatory = $true)] [string] $ValuesYamlPath
)

$tenant_id = az account show --query "tenantId"
Write-Output $tenant_id

$event_hub_comp_endpoint = az iot hub show --name $IotHubName --query "properties.eventHubEndpoints.events.endpoint"
Write-Output $event_hub_comp_endpoint
az iot hub consumer-group create --hub-name $IotHubName --name events
az iot hub consumer-group create --hub-name $IotHubName --name telemetry
az iot hub consumer-group create --hub-name $IotHubName --name tunnel
az iot hub consumer-group create --hub-name $IotHubName --name onboarding

$res_strlist = az iot hub connection-string show --hub-name $IotHubName --policy-name iothubowner --key-type secondary
$res_json = "$res_strlist" | ConvertFrom-Json
$iothubowner_connstr = $res_json.connectionString
Write-Output $iothubowner_connstr

$cosmosdb_connstr = az cosmosdb keys list --resource-group $RGName --name $CosmosDBName --type connection-strings --query "connectionStrings[1].connectionString"
Write-Output $cosmosdb_connstr

$storage_connstr = az storage account show-connection-string --name $StorageAccName --query "connectionString"
Write-Output $storage_connstr

$EvHubNamespace_connstr = az eventhubs namespace authorization-rule keys list --resource-group $RGName --namespace-name $EvHubNamespace --name RootManageSharedAccessKey --query "secondaryConnectionString"
Write-Output $EvHubNamespace_connstr
az eventhubs eventhub consumer-group create --resource-group $RGName --namespace-name $EvHubNamespace --eventhub-name $EvHubName --name telemetry_cdm
az eventhubs eventhub consumer-group create --resource-group $RGName --namespace-name $EvHubNamespace --eventhub-name $EvHubName --name telemetry_ux

$SerBusNamespace_connstr = az servicebus namespace authorization-rule keys list --resource-group $RGName --namespace-name $SerBusNamespace --name RootManageSharedAccessKey --query "secondaryConnectionString"
Write-Output $SerBusNamespace_connstr

$kv_uri = az keyvault show --name $KeyVaultName --query "properties.vaultUri"
Write-Output $kv_uri

$sr_connstr = az signalr key list --name $SignalRName --resource-group $RGName --query "secondaryConnectionString"
Write-Output $sr_connstr

$aad_register_script_path = Join-Path -Path $IIoTRepoPath -ChildPath "deploy" -AdditionalChildPath "scripts", "aad-register.ps1"
$params = '-Name "' + $IIoTAppName.ToString() + '" -TenantId ' + $tenant_id.ToString() + ' -Output "' + $AadRegPath.ToString() + '"'
Invoke-Expression -Command "$aad_register_script_path $params"

helm repo add azure-iiot https://azureiiot.blob.core.windows.net/helm
kubectl create namespace azure-iiot-ns
$aad_json = Get-Content -Raw -Path $AadRegPath | ConvertFrom-Json
$helm_values_dict = @{
    azure      = @{
        tenantId            = $tenant_id.Trim('"', "'");
        iotHub              = @{
            eventHub             = @{
                endpoint      = $event_hub_comp_endpoint.Trim('"', "'");
                consumerGroup = @{
                    events     = "events";
                    telemetry  = "telemetry";
                    tunnel     = "tunnel";
                    onboarding = "onboarding";
                };
            };
            sharedAccessPolicies = @{
                iothubowner = @{
                    connectionString = $iothubowner_connstr.Trim('"', "'");
                };
            };
        };
        cosmosDB            = @{
            connectionString = $cosmosdb_connstr.Trim('"', "'");
        };
        storageAccount      = @{
            connectionString = $storage_connstr.Trim('"', "'");
        };
        eventHubNamespace   = @{
            sharedAccessPolicies = @{
                rootManageSharedAccessKey = @{
                    connectionString = $EvHubNamespace_connstr.Trim('"', "'");
                };
            };
            eventHub             = @{
                name          = $EvHubName;
                consumerGroup = @{
                    telemetryCdm = "telemetry_cdm";
                    telemetryUx  = "telemetry_ux";
                };
            };
        };
        serviceBusNamespace = @{
            sharedAccessPolicies = @{
                rootManageSharedAccessKey = @{
                    connectionString = $SerBusNamespace_connstr.Trim('"', "'");
                };
            };
        };
        keyVault            = @{
            uri = $kv_uri.Trim('"', "'");
        };
        signalR             = @{
            connectionString = $sr_connstr.Trim('"', "'");
            serviceMode      = "Default";
        };
        auth                = @{
            required    = $true;
            servicesApp = @{
                appId    = $aad_json.ServiceId;
                secret   = $aad_json.ServiceSecret;
                audience = $aad_json.Audience;
            };
            clientsApp  = @{
                appId  = $aad_json.WebAppId;
                secret = $aad_json.WebAppSecret;
            };
        };
    };
    deployment = @{
        ingress = @{
            enabled     = $true;
            annotations = @{
                "kubernetes.io/ingress.class"                        = "nginx";
                "nginx.ingress.kubernetes.io/affinity"               = "cookie";
                "nginx.ingress.kubernetes.io/session-cookie-name"    = "affinity";
                "nginx.ingress.kubernetes.io/session-cookie-expires" = "14400";
                "nginx.ingress.kubernetes.io/session-cookie-max-age" = "14400";
                "nginx.ingress.kubernetes.io/proxy-read-timeout"     = "3600";
                "nginx.ingress.kubernetes.io/proxy-send-timeout"     = "3600";
            };
        };
    };
}
$helm_values = ConvertTo-Yaml $helm_values_dict
Set-Content -Path $ValuesYamlPath -Value $helm_values
helm install azure-iiot azure-iiot/azure-industrial-iot --namespace azure-iiot-ns --values $ValuesYamlPath
