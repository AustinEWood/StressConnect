param (
    [string]$apiKey
)

# Initialize logging with dynamic path
$Logfile = Join-Path (Get-Location) 'error_log.txt'

# Function for writing to log file
function LogWrite{
   Param ([string]$logstring)
   Add-content $Logfile -value $logstring
}
 
# Filtering for established connections, removing loopbacks & IP6 addresses
$netstatOutput = netstat -ano | findstr ESTABLISHED | findstr -v 127.0.0.1 | findstr -v ::



# Initialize an array to store connection objects
$connections = @()

# Parse the netstat output to extract connection information
$netstatOutput | ForEach-Object {
    try {
        $parts = $_ -split '\s+'
        $remoteAddressParts = $parts[3] -split ':'
        $localAddressParts = $parts[2] -split ':'

        # Check if the RemoteAddress is an IPv6 address and skip if true
        if ($remoteAddressParts[0] -match '.*:.*:.*') {
            continue
        }

        # Get the process name using PID
        $processName = (Get-Process -Id $parts[5]).ProcessName

        # Construct a PSCustomObject to represent the connection
        $connection = [PSCustomObject]@{
            Protocol = $parts[1]
            LocalAddress = $localAddressParts[0]
            LocalPort = $localAddressParts[1]
            RemoteAddress = $remoteAddressParts[0]
            RemotePort = $remoteAddressParts[1]
            State = $parts[4]
            PID = $parts[5]
            ProcessName = $processName
        }

        # Add the connection object to the connections array
        $connections += $connection
    } catch {
        LogWrite "An error occurred while parsing netstat output: $_"    
    }
}


# Loop through each connection to process VirusTotal data (if API key is provided and valid)
function Use-APIKey{
    foreach ($connection in $connections) {
        try {
            if ($apiKey) {
                $virusTotalApiUrl = "https://www.virustotal.com/api/v3/ip_addresses/" + $connection.RemoteAddress

                $headers = @{
                    "x-apiKey" = $apiKey
                }

                $virusTotalResponse = Invoke-RestMethod -Uri $virusTotalApiUrl -Headers $headers -ErrorAction SilentlyContinue

                $connection | Add-Member -MemberType NoteProperty -Name MaliciousVerdicts -Value ($virusTotalResponse.data.attributes.last_analysis_stats.malicious)
            }
        }
        catch {
            LogWrite "An error occurred: $_" 
        }
    }    
}

# Testing to see APIKey has a value if so validate the key and run Use-APiKey.
function Test-APIKey {  
    
    $virusTotalApiUrlTest = "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8" # Using URL feed as a test

    $headers = @{
        "x-apiKey" = $apiKey
    }

    try {
        if ($apiKey -eq ""){
            LogWrite "No API Key supplied"
        }
        else {
        $response = Invoke-RestMethod -Uri $virusTotalApiUrlTest -Headers $headers -Method 'GET' -ErrorAction Stop
        LogWrite "It should have worked"
        LogWrite $response
        Use-APIKey
        }
    }    
    catch {
        LogWrite "An error occurred while testing the API key. It may be incorrect or there might be an issue with the endpoint."
    }
}


Test-APIKey




# Convert the processed connections to JSON and write them to the standard output
$connections | ConvertTo-Json -Compress -ErrorAction SilentlyContinue


