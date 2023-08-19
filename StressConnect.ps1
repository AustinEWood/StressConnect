# Filtering for established connections removing loopbacks & IP6 addresses
$netstatOutput = netstat -ano | findstr ESTABLISHED | findstr -v 127. | findstr -v [

# Parse the netstat output to extract connection information
$connections = $netstatOutput | ForEach-Object {
    $parts = $_ -split '\s+'
    $addressParts = $parts[2, 3] -split ':'
    $remoteAddress = $addressParts[2]
    $remotePort = $addressParts[3]

    $addressParts = $parts[2] -split ':'
    $localAddress = $addressParts[0]
    $localPort = $addressParts[1]
    
    [PSCustomObject]@{
        Protocol = $parts[1]
        LocalAddress = $localAddress
        LocalPort = $localPort
        RemoteAddress = $remoteAddress
        RemotePort = $remotePort
        State = $parts[4]
        PID = $parts[5]
    }
}

# Initialize an array to store processed connection information
$connectionsWithProcesses = @()

# Loop through each connection to process VirusTotal data
foreach ($connection in $connections) {
    $process = Get-Process -Id $connection.PID -ErrorAction SilentlyContinue

    # Construct the VirusTotal API URL for the current connection's remote address
    $virusTotalApiUrl = "https://www.virustotal.com/api/v3/ip_addresses/$($connection.remoteAddress)"
    
    # Set up headers with your API key
    $headers = @{
        "x-apikey" = "Your API Key Here"
    }

    # Send the VirusTotal API request
    $virusTotalResponse = Invoke-RestMethod -Uri $virusTotalApiUrl -Headers $headers

    $connection | Add-Member -MemberType NoteProperty -Name ProcessName -Value ($process.Name -join ', ')
    $connection | Add-Member -MemberType NoteProperty -Name MaliciousVerdicts -Value ($virusTotalResponse.data.attributes.last_analysis_stats.malicious)
    
    # Add the processed connection information to the array
    $connectionsWithProcesses += $connection
}

# Export the data to a CSV file
$currentTD = Get-Date -Format "yyyyMMdd_HHmmss"
$desktopFilePath = [Environment]::GetFolderPath('Desktop')
$csvFolderExists = Test-Path -Path "$desktopFilePath\nsConnections"
if (-not $csvFolderExists) {
    New-Item -Path "$desktopFilePath" -Name "nsConnections" -ItemType 'directory'
}
$csvFilePath = "$desktopFilePath\nsConnections"
$csvFileName = "$csvFilePath\$currentTD.csv"
#$csvFilePath = "Your\File\Path\Here.csv"
$connectionsWithProcesses | Export-Csv -Path $csvFileName -NoTypeInformation

Write-Host "Data exported to $csvFileName"
 