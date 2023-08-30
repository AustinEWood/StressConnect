# StressConnect

The Executable is in the Git file. You can right-click it and create a shortcut to your desktop if you would like.


Test connections Established on your Windows device to see if they are Malicious.

The GUI is now in place.

You must select the script to run from the drop-down menu. As of now "Stress Connect" is the only option to choose. This will change in the future. 

You can run the script without the API key. You will not get the VirusTotal information but you will get all other relevant information. There is input validation for the API key as well. So, if the API key is wrong an error will output to the error_log.txt file and you will not see the VT malicious score.

You now have the option to view the output in the application itself. This means you do not have to save the file.

Errors will output to the error_log.txt. I am adding user-friendly errors on the front end but they are not in yet.

You may also save the information with the "Save Ouput" button this will export formatted to a CSV file.





Script Information:


Stress Connect: 
This script will use netstate to pull all established connections to your device. It will filter out any IPv6 addresses as well as any loopback addresses. If you have supplied an API key it will test the connection's remote IP to VirusTotal to see if any are known malicious IPs.  Supplied in the information with be Protocol, Local Address and port, Remote address and port, State of the connection, PID of the process running, and the Process Name running attached to the connection. If the API key is present it will add "Malicious Verdicts" to the list of information and give it a number showing how many vendors have reported the IP. 

![StressConnectOpen](https://github.com/AustinEWood/StressConnect/assets/53714369/6e136070-a900-403f-aa26-29c6178503bb)

![StressConnectRun](https://github.com/AustinEWood/StressConnect/assets/53714369/edd9b374-ed88-4cff-991d-9771c98d8262)

![StressConnectWithAPIKey](https://github.com/AustinEWood/StressConnect/assets/53714369/bc96ddc6-d552-471c-9ba6-dbd9a09867a9)

![StressConnectSaveFile](https://github.com/AustinEWood/StressConnect/assets/53714369/53551f2b-e8ff-4ff1-a45f-fbf8aab53ad4)

![StressConnectCSVFile](https://github.com/AustinEWood/StressConnect/assets/53714369/bbaf90d6-d334-4f47-8924-09901f7b25b0)




