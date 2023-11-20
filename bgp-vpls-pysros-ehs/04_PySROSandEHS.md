# Containerlab based Nokia Seamless-MPLS demo including pySROS and Event Handler System to simplify BGP-VPLS (RFC4761) configuration activities when using RSVP-TE signaled LSPs

## Enhancing the deployment of RFC4761 VPLS Using BGP (BGP-VPLS) for Auto-Discovery and Signaling using RSVP-TE signaled LSPs using pySROS and Event Handler System 

As part of the [Seamless-MPLS Demo](README.md), this scenario is the where pySROS and Event Handler System get integrated into the L2VPN solution to make deployment easier.

The previous scenario was [The L2VPN RFC4761 - VPLS with BGP Auto discovery and Signaling Build and Test Sequence](03_L2ServiceBuildandTest.md)

As this is possibly the more interesting part of this demo, it is possible that same people may not have gone through the previous tasks.  That is completely fine and the instructions below will provide guidance on how to get into it.

The following diagram highlights the Simple Full-Mesh L2VPN (BGP-VPLS) service to be provisioned on the network (assuming that the infrastructure is already in place):

![BGP-VPLS](diagrams/03_L2VPN-RFC4761-Topology.PNG)

## L2VPN-600 PE and CE Details:

|Node Name|RD|RT|PE-CE Role|PE-CE Interface|PE-CE IP Address|
|-|---|---|---|---|---|
|RED-R1| 64512:600 | 64512:600 | PE|1/1/3.600  |N/A |
|RED-R1-CLIENT| N/A |N/A | CE | eth1.600 | 172.16.200.1/24 |
|RED-R2| 64512:600 | 64512:600 | PE|1/1/3.600  |N/A |
|RED-R2-CLIENT| N/A |N/A | CE | eth1.600 | 172.16.200.2/24 |
|BLUE-R1| 64512:600 | 64512:600 | PE|1/1/3.600  |N/A |
|BLUE-R1-CLIENT| N/A |N/A | CE | eth1.600 | 172.16.200.3/24 |



## Step #-1 - If Containerlab is already running, stop it

If you were previously running the bgp-vpls.yml topology, please shutdown the containerlab instance.  The intention will be to "start afresh" without any additional LSPs or services configured that might get in the way of the understanding

```
sudo containerlab destroy --topo bgp-vpls.yml
```

## Step #0 - Obtain Containerlab (this lab was developed using containerlab version 0.42.0)
Only necessary if you do not yet have containerlab on your system

https://containerlab.dev/install/

## Step #1 - Ensure that you have a SROS docker image and valid license key

If necessary edit **bgp-vpls.yml** to align with your environment (this lab is using SROS version 23.10.R1, and the license file is specified to be found in  ~/23.x_SR_OS_VSR-SIM_License.txt)

For instructions on creating a docker image if you have a https://containerlab.dev/manual/vrnetlab/

For a valid license key, reach out to your appropriate Nokia contact.

## Step #2 - Start the Container Lab Instance

This is where the 4 routers and 3 linux containers and associated interconnections described in *bgp-vpls.yml* will be instantiated

```
sudo containerlab deploy --reconfigure --topo bgp-vpls.yml
```

The *reconfigure* flag will ignore any previous router configurations that may have been saved (in this scenario we do not want to consider any previous configurations - we just want the infrastructure to be ready, so this flag is necessary)

As we are using ["partial" configurations](base-configs/), as soon as containerlab returns to the console prompt, the environment will be ready to connect and perform actions.

## Step #3 - Making SROS aware that there is a python script that can be used

As part of the **bgp-vpls.yml** default kind configuration, through the binding configuration items, the folder [pysros-scripts/](pysros-scripts/) will be available to SROS routers via tftp on the IP 172.31.255.29 which is an internal component of container lab.

Apply the following to each of the PE Routers

>    /configure python python-script "BGP-VPLS-PATHMAKER" admin-state enable
>
>    /configure python python-script "BGP-VPLS-PATHMAKER" urls ["tftp://172.31.255.29/pysros-scripts/bgp-vpls-pathmaker.py"]
>
>    /configure python python-script "BGP-VPLS-PATHMAKER" version python3

#### RED-R1 Script Registration
```
A:admin@RED-R1# configure private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

[pr:/configure]
A:admin@RED-R1# /configure python python-script "BGP-VPLS-PATHMAKER" admin-state enable

*[pr:/configure]
A:admin@RED-R1# /configure python python-script "BGP-VPLS-PATHMAKER" urls ["tftp://172.31.255.29/pysros-scripts/bgp-vpls-pathmaker.py"]

*[pr:/configure]
A:admin@RED-R1# /configure python python-script "BGP-VPLS-PATHMAKER" version python3

*[pr:/configure]
A:admin@RED-R1# commit

[pr:/configure] exit all

```

#### RED-R1 Script Test

Use **pyexec** we are now able to invoke the script.  As there are no services requiring attention from the script, it will not take any action.  
```
A:admin@RED-R1# pyexec "BGP-VPLS-PATHMAKER"
Access Network: 10.0.1.0/24

```
The message shown is a debug message within the script - initially it will determine what access network it is in to determine if the destination router is in the same or a different network - this is so that it can determine if it is a BGP-Tunnel or a RSVP-TE based SDP service that needs constructing.

#### RED-R2 Script Registration
```
A:admin@RED-R2# configure private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

[pr:/configure]
A:admin@RED-R2# /configure python python-script "BGP-VPLS-PATHMAKER" admin-state enable

*[pr:/configure]
A:admin@RED-R2# /configure python python-script "BGP-VPLS-PATHMAKER" urls ["tftp://172.31.255.29/pysros-scripts/bgp-vpls-pathmaker.py"]

*[pr:/configure]
A:admin@RED-R2# /configure python python-script "BGP-VPLS-PATHMAKER" version python3

*[pr:/configure]
A:admin@RED-R2# commit

[pr:/configure] exit all

```

#### RED-R1 Script Test

Use **pyexec** we are now able to invoke the script.  As there are no services requiring attention from the script, it will not take any action.  
```
A:admin@RED-R1# pyexec "BGP-VPLS-PATHMAKER"
Access Network: 10.0.1.0/24

```

#### BLUE-R1 Script Registration
```
A:admin@BLUE-R1# configure private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

[pr:/configure]
A:admin@BLUE-R1# /configure python python-script "BGP-VPLS-PATHMAKER" admin-state enable

*[pr:/configure]
A:admin@BLUE-R1# /configure python python-script "BGP-VPLS-PATHMAKER" urls ["tftp://172.31.255.29/pysros-scripts/bgp-vpls-pathmaker.py"]

*[pr:/configure]
A:admin@BLUE-R1# /configure python python-script "BGP-VPLS-PATHMAKER" version python3

*[pr:/configure]
A:admin@BLUE-R1# commit

[pr:/configure]
A:admin@BLUE-R1# exit all
INFO: CLI #2074: Exiting private configuration mode

```

#### BLUE-R1 Script Test

Use **pyexec** we are now able to invoke the script.  As there are no services requiring attention from the script, it will not take any action.  
```
A:admin@RED-R1# pyexec "BGP-VPLS-PATHMAKER"
Access Network: 10.0.2.0/24

```

## Step #4 - Common Service Configuration (RED-R1, RED-R2 and BLUE-R1)

The common configuration that needs to be applied just once is to create the Psuedowire Template (pw-template) that will be used by the VPLS services to link SDPs into the BGP-VPLS 

One RED-R1, RED-R2 and BLUE-R1 apply the following configuration lines from [service-configs/L2VPN-RFC4761/COMMON-PWTEMPLATE.cfg](service-configs/L2VPN-RFC4761/COMMON-PWTEMPLATE.cfg)

```
    /configure service pw-template "BGP-VPLS" pw-template-id 1
    /configure service pw-template "BGP-VPLS" provisioned-sdp use
    /configure service pw-template "BGP-VPLS" control-word true
    /configure service pw-template "BGP-VPLS" split-horizon-group name "MESH"

```

## Step #5 - Apply the L2VPN Configuration to RED-R1 and BLUE-R1 only

RED-R2 will be introduced to this service in due course.

### Apply the L2VPN Configuration to RED-R1
Apply the L2VPN Configuration onto RED-R1 from from [service-configs/L2VPN-RFC4761/RED-R1-BGP-VPLS.cfg](service-configs/L2VPN-RFC4761/RED-R1-BGP-VPLS.cfg):

```
    /configure service vpls "L2VPN-600" admin-state enable
    /configure service vpls "L2VPN-600" service-id 600
    /configure service vpls "L2VPN-600" customer "1"
    /configure service vpls "L2VPN-600" stp admin-state disable
    /configure service vpls "L2VPN-600" bgp 1 route-distinguisher "64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target export "target:64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target import "target:64512:600"
    /configure service { vpls "L2VPN-600" bgp 1 pw-template-binding "BGP-VPLS" }
    /configure service vpls "L2VPN-600" bgp-vpls admin-state enable
    /configure service vpls "L2VPN-600" bgp-vpls maximum-ve-id 10
    /configure service vpls "L2VPN-600" bgp-vpls ve name "RED-R1-CLIENT"
    /configure service vpls "L2VPN-600" bgp-vpls ve id 1
    /configure service vpls "L2VPN-600" sap 1/1/3:600 admin-state enable
```


### Apply the L2VPN Configuration to BLUE-R1
Apply the L2VPN Configuration onto BLUE-R1 from from [service-configs/L2VPN-RFC4761/BLUE-R1-BGP-VPLS.cfg](service-configs/L2VPN-RFC4761/BLUE-R1-BGP-VPLS.cfg):

```
    /configure service vpls "L2VPN-600" admin-state enable
    /configure service vpls "L2VPN-600" service-id 600
    /configure service vpls "L2VPN-600" customer "1"
    /configure service vpls "L2VPN-600" stp admin-state disable
    /configure service vpls "L2VPN-600" bgp 1 route-distinguisher "64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target export "target:64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target import "target:64512:600"
    /configure service { vpls "L2VPN-600" bgp 1 pw-template-binding "BGP-VPLS" }
    /configure service vpls "L2VPN-600" bgp-vpls admin-state enable
    /configure service vpls "L2VPN-600" bgp-vpls maximum-ve-id 10
    /configure service vpls "L2VPN-600" bgp-vpls ve name "BLUE-R1-CLIENT"
    /configure service vpls "L2VPN-600" bgp-vpls ve id 3
    /configure service vpls "L2VPN-600" sap 1/1/3:600 admin-state enable
```
## Step #6 - Check log-id 99 on RED-R1 and BLUE-R1 for failure to bind to a SDP


### Check RED-R1 log
```
A:admin@RED-R1# show log log-id 99

===============================================================================
Event Log 99 log-name 99
===============================================================================
Description : Default System Log
Memory Log contents  [size=500   next event=85  (not wrapped)]

84 2023/11/20 11:35:10.540 UTC MAJOR: SVCMGR #2322 Base
"The system failed to create a dynamic bgpSignalL2vpn SDP Bind  in service 600 with SDP pw-template policy 1 for the following reason: suitable manual SDP not found."
```

### Check BLUE-R1 log
```
A:admin@BLUE-R1# show log log-id 99

===============================================================================
Event Log 99 log-name 99
===============================================================================
Description : Default System Log
Memory Log contents  [size=500   next event=75  (not wrapped)]

74 2023/11/20 11:35:08.592 UTC MAJOR: SVCMGR #2322 Base
"The system failed to create a dynamic bgpSignalL2vpn SDP Bind  in service 600 with SDP pw-template policy 1 for the following reason: suitable manual SDP not found."
```

## Step #6 - Verify SAP and SDP States on RED-R1 and BLUE-R1 

### Check RED-R1 L2VPN Service Base info
```
A:admin@RED-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
* 
```
### Check BLUE-R1 L2VPN Service Base info
```
A:admin@BLUE-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated. 
```

## Step #7 - Manually Invoke "BGP-VPLS-PATHMAKER" on RED-R1 and BLUE-R1
This is the script that makes the provisioning less burdensome

### Run "BGP-VPLS-PATHMAKER" on RED-R1
```
A:admin@RED-R1# pyexec "BGP-VPLS-PATHMAKER"
Access Network: 10.0.1.0/24
Checking VPLS L2VPN-600:
Need SDP to 10.0.2.1
SDP 15513 to 10.0.2.1 to be created
 BGP Tunnel SDP required
Creating SDP 15513 with BGP-Tunnel to 10.0.2.1
```

### Run "BGP-VPLS-PATHMAKER" on BLUE-R1
```
A:admin@BLUE-R1# pyexec "BGP-VPLS-PATHMAKER"
Access Network: 10.0.2.0/24
Checking VPLS L2VPN-600:
Need SDP to 10.0.1.1
SDP 15257 to 10.0.1.1 to be created
 BGP Tunnel SDP required
Creating SDP 15257 with BGP-Tunnel to 10.0.1.1
```

## Step #7 - Verify SAP and SDP States on RED-R1 and BLUE-R1
After the script has run, confirm that there are spoke SDPs attached to the service

### Check RED-R1 L2VPN Service Base info
```
A:admin@RED-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
sdp:15513:4294967295 S(10.0.2.1)         BgpVpls      0       9166    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
### Check BLUE-R1 L2VPN Service Base info
```
A:admin@BLUE-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
sdp:15257:4294967295 S(10.0.1.1)         BgpVpls      0       9166    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
## Step #8 - Connectivity between RED-R1-CLIENT and BLUE-R1-CLIENT

### RED-R1-CLIENT (172.16.200.1) to ping BLUE-R1-CLIENT (172.16.200.3) via L2VPN-600

```
$ docker exec -it clab-vpls-RED-R1-CLIENT ping 172.16.200.3 -I 172.16.200.1 -c 3
PING 172.16.200.3 (172.16.200.3) from 172.16.200.1: 56 data bytes
64 bytes from 172.16.200.3: seq=0 ttl=64 time=5.835 ms
64 bytes from 172.16.200.3: seq=1 ttl=64 time=14.437 ms
64 bytes from 172.16.200.3: seq=2 ttl=64 time=15.296 ms

--- 172.16.200.3 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 5.835/11.856/15.296 ms

```


### Check MAC Address Table on RED-R1 L2VPN-600

```
A:admin@RED-R1# show service id "600" fdb detail

===============================================================================
Forwarding Database, Service 600
===============================================================================
ServId     MAC               Source-Identifier       Type     Last Change
            Transport:Tnl-Id                         Age
-------------------------------------------------------------------------------
600        aa:c1:ab:22:12:61 sap:1/1/3:600           L/0      11/20/23 11:36:41
600        aa:c1:ab:d7:48:5e sdp:15513:4294967295    L/0      11/20/23 11:48:02
-------------------------------------------------------------------------------
No. of MAC Entries: 2
-------------------------------------------------------------------------------
Legend:L=Learned O=Oam P=Protected-MAC C=Conditional S=Static Lf=Leaf T=Trusted
===============================================================================
```


### Check MAC Address Table on BLUE-R1 L2VPN-600

```
A:admin@BLUE-R1# show service id "600" fdb detail

===============================================================================
Forwarding Database, Service 600
===============================================================================
ServId     MAC               Source-Identifier       Type     Last Change
            Transport:Tnl-Id                         Age
-------------------------------------------------------------------------------
600        aa:c1:ab:22:12:61 sdp:15257:4294967295    L/0      11/20/23 11:47:56
600        aa:c1:ab:d7:48:5e sap:1/1/3:600           L/0      11/20/23 11:48:02
-------------------------------------------------------------------------------
No. of MAC Entries: 2
-------------------------------------------------------------------------------
Legend:L=Learned O=Oam P=Protected-MAC C=Conditional S=Static Lf=Leaf T=Trusted
===============================================================================
```


## Step #9 - Event Handler System Configuration

There are 4 items to be configured so that an event can result in a script being executed.

* The Log Filter - used by the Event Trigger and ensures only relevant events with a specific message are used
* The Script Control Policy - this links the pySROS script we want to run and is called by the Handler
* The Handler - used by the Event Trigger to call the Script Control Policy
* The Event Trigger - called when a specific application and event occurs in accordance to the Log Filter and when triggered called the Handler

On RED-R1, RED-R2 and BLUE-R1 apply the following configuration so that in the event a log event related to a dynamicSDPBindCreation Fails due to a manual SDP not being found, it will trigger our pySROS script:

>    /configure log filter "FILTER-BGP-VPLS-PATHMAKER" default-action forward
>
>    /configure log filter "FILTER-BGP-VPLS-PATHMAKER" named-entry "no_manual_sdp" action forward
>
>    /configure log filter "FILTER-BGP-VPLS-PATHMAKER" named-entry "no_manual_sdp" match message eq "suitable manual SDP not found"
>
>    /configure log filter "FILTER-BGP-VPLS-PATHMAKER" named-entry "no_manual_sdp" match message regexp true
>
>    /configure system script-control script-policy "SCRIPTPOLICY-BGP-VPLS-PATHMAKER" owner "admin" admin-state enable
>
>    /configure system script-control script-policy "SCRIPTPOLICY-BGP-VPLS-PATHMAKER" owner "admin" results "/null"
>
>    /configure system script-control script-policy "SCRIPTPOLICY-BGP-VPLS-PATHMAKER" owner "admin" python-script name "BGP-VPLS-PATHMAKER"
>
>    /configure log event-handling handler "HANDLER-BGP-VPLS-PATHMAKER" admin-state enable
>
>    /configure log event-handling handler "HANDLER-BGP-VPLS-PATHMAKER" entry 10 script-policy name "SCRIPTPOLICY-BGP-VPLS-PATHMAKER"
>
>    /configure log event-handling handler "HANDLER-BGP-VPLS-PATHMAKER" entry 10 script-policy owner "admin"
>
>    /configure log event-trigger svcmgr event dynamicSdpBindCreationFailed admin-state enable
>
>    /configure log event-trigger svcmgr event dynamicSdpBindCreationFailed entry 10 admin-state enable

>    /configure log event-trigger svcmgr event dynamicSdpBindCreationFailed entry 10 filter "FILTER-BGP-VPLS-PATHMAKER"
>
>    /configure log event-trigger svcmgr event dynamicSdpBindCreationFailed entry 10 handler "HANDLER-BGP-VPLS-PATHMAKER"

## Step #10 - Apply the L2VPN Configuration to RED-R2

Finally RED-R2 will be added to the VPLS and the associated SDPs (and RSVP-TE LSPs if needed) will be created by the script when the event handler detects an event

### Apply the L2VPN Configuration to RED-R2
Apply the L2VPN Configuration onto RED-R2 from from [service-configs/L2VPN-RFC4761/RED-R1-BGP-VPLS.cfg](service-configs/L2VPN-RFC4761/RED-R2-BGP-VPLS.cfg):

```
    /configure service vpls "L2VPN-600" admin-state enable
    /configure service vpls "L2VPN-600" service-id 600
    /configure service vpls "L2VPN-600" customer "1"
    /configure service vpls "L2VPN-600" stp admin-state disable
    /configure service vpls "L2VPN-600" bgp 1 route-distinguisher "64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target export "target:64512:600"
    /configure service vpls "L2VPN-600" bgp 1 route-target import "target:64512:600"
    /configure service { vpls "L2VPN-600" bgp 1 pw-template-binding "BGP-VPLS" }
    /configure service vpls "L2VPN-600" bgp-vpls admin-state enable
    /configure service vpls "L2VPN-600" bgp-vpls maximum-ve-id 10
    /configure service vpls "L2VPN-600" bgp-vpls ve name "RED-R2-CLIENT"
    /configure service vpls "L2VPN-600" bgp-vpls ve id 2
    /configure service vpls "L2VPN-600" sap 1/1/3:600 admin-state enable
```

## Step #11 - Verify SAP and SDP States on RED-R1, RED-R2 and BLUE-R1
Now that the event handler knows when it should trigger the script, we should see that RED-R1 and BLUE-R1 have SDPs to RED-R2 (10.0.1.2) and that RED-R2 has SDPs to RED-R1 (10.0.1.1) and BLUE-R1 (10.0.2.1)

### Check RED-R1 L2VPN Service Base info
```
A:admin@RED-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
sdp:15258:4294967294 S(10.0.1.2)         BgpVpls      0       9170    Up   Up
sdp:15513:4294967295 S(10.0.2.1)         BgpVpls      0       9166    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
### Check RED-R2 L2VPN Service Base info
```
A:admin@RED-R2# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
sdp:15257:4294967294 S(10.0.1.1)         BgpVpls      0       9170    Up   Up
sdp:15513:4294967295 S(10.0.2.1)         BgpVpls      0       9166    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
``` 


### Check BLUE-R1 L2VPN Service Base info
```
A:admin@BLUE-R1# show service id "L2VPN-600" base | match "Service Access" post-lines 10
Service Access & Destination Points
-------------------------------------------------------------------------------
Identifier                               Type         AdmMTU  OprMTU  Adm  Opr
-------------------------------------------------------------------------------
sap:1/1/3:600                            q-tag        9192    9192    Up   Up
sdp:15257:4294967295 S(10.0.1.1)         BgpVpls      0       9166    Up   Up
sdp:15258:4294967294 S(10.0.1.2)         BgpVpls      0       9166    Up   Up
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
### Check the SDP Configuration on RED-R1

```
[pr:/configure service]
A:admin@RED-R1# info
    pw-template "BGP-VPLS" {
        pw-template-id 1
        provisioned-sdp use
        control-word true
        split-horizon-group {
            name "MESH"
        }
    }
    sdp 15258 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.1.2 RSVP"
        delivery-type mpls
        signaling bgp
        far-end {
            ip-address 10.0.1.2
        }
        lsp "BGPVPLS-10.0.1.2" { }
    }
    sdp 15513 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.2.1 BGP-LU"
        delivery-type mpls
        signaling bgp
        bgp-tunnel true
        far-end {
            ip-address 10.0.2.1
        }
    }
``` 

### On RED-R1 Check the Configuration of the LSP that is bound to to the SDP 
```
[pr:/configure router "Base" mpls lsp "BGPVPLS-10.0.1.2"]
A:admin@RED-R1# info
    admin-state enable
    type p2p-rsvp
    to 10.0.1.2
    rsvp-resv-style ff
    adspec true
    path-computation-method local-cspf
    fast-reroute {
        frr-method one-to-one
    }
    primary "LOOSE" {
    }
```

### Check the SDP Configuration on RED-R2

```
[pr:/configure service]
A:admin@RED-R2# info
    pw-template "BGP-VPLS" {
        pw-template-id 1
        provisioned-sdp use
        control-word true
        split-horizon-group {
            name "MESH"
        }
    }
    sdp 15257 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.1.1 RSVP"
        delivery-type mpls
        signaling bgp
        far-end {
            ip-address 10.0.1.1
        }
        lsp "BGPVPLS-10.0.1.1" { }
    }
    sdp 15513 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.2.1 BGP-LU"
        delivery-type mpls
        signaling bgp
        bgp-tunnel true
        far-end {
            ip-address 10.0.2.1
        }
    }
``` 

### On RED-R2 Check the Configuration of the LSP that is bound to to the SDP 
```
[pr:/configure router "Base" mpls lsp "BGPVPLS-10.0.1.1"]
A:admin@RED-R2# info
    admin-state enable
    type p2p-rsvp
    to 10.0.1.1
    rsvp-resv-style ff
    adspec true
    path-computation-method local-cspf
    fast-reroute {
        frr-method one-to-one
    }
    primary "LOOSE" {
    }
```

### Check the SDP Configuration on BLUE-R1

```
[pr:/configure service]
A:admin@BLUE-R1# info
    pw-template "BGP-VPLS" {
        pw-template-id 1
        provisioned-sdp use
        control-word true
        split-horizon-group {
            name "MESH"
        }
    }
    sdp 15257 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.1.1 BGP-LU"
        delivery-type mpls
        signaling bgp
        bgp-tunnel true
        far-end {
            ip-address 10.0.1.1
        }
    }
    sdp 15258 {
        admin-state enable
        description "bgp-vpls-pathmaker.py - 10.0.1.2 BGP-LU"
        delivery-type mpls
        signaling bgp
        bgp-tunnel true
        far-end {
            ip-address 10.0.1.2
        }
    }
``` 

## Step #12 - Connectivity between RED-R1-CLIENT, RED-R2-CLIENT and BLUE-R1-CLIENT

### RED-R1-CLIENT (172.16.200.1) to ping RED-R2-CLIENT (172.16.200.2) via L2VPN-600

```
$ docker exec -it clab-vpls-RED-R1-CLIENT ping 172.16.200.2 -I 172.16.200.1 -c 3
PING 172.16.200.2 (172.16.200.2) from 172.16.200.1: 56 data bytes
64 bytes from 172.16.200.2: seq=0 ttl=64 time=5.109 ms
64 bytes from 172.16.200.2: seq=1 ttl=64 time=9.615 ms
64 bytes from 172.16.200.2: seq=2 ttl=64 time=9.470 ms

--- 172.16.200.2 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 5.109/8.064/9.615 ms
```

### RED-R1-CLIENT (172.16.200.1) to ping BLUE-R1-CLIENT (172.16.200.3) via L2VPN-600

```
$ docker exec -it clab-vpls-RED-R1-CLIENT ping 172.16.200.3 -I 172.16.200.1 -c 3
PING 172.16.200.3 (172.16.200.3) from 172.16.200.1: 56 data bytes
64 bytes from 172.16.200.3: seq=0 ttl=64 time=2.899 ms
64 bytes from 172.16.200.3: seq=1 ttl=64 time=13.949 ms
64 bytes from 172.16.200.3: seq=2 ttl=64 time=14.864 ms

--- 172.16.200.3 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 2.899/10.570/14.864 ms
```

### RED-R2-CLIENT (172.16.200.2) to ping BLUE-R1-CLIENT (172.16.200.3) via L2VPN-600

```
$ docker exec -it clab-vpls-RED-R2-CLIENT ping 172.16.200.3 -I 172.16.200.2 -c 3
PING 172.16.200.3 (172.16.200.3) from 172.16.200.2: 56 data bytes
64 bytes from 172.16.200.3: seq=0 ttl=64 time=5.432 ms
64 bytes from 172.16.200.3: seq=1 ttl=64 time=14.109 ms
64 bytes from 172.16.200.3: seq=2 ttl=64 time=14.514 ms

--- 172.16.200.3 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 5.432/11.351/14.514 ms
```


### Check MAC Address Table on RED-R1 L2VPN-600

```
A:admin@RED-R1# show service id "600" fdb detail

===============================================================================
Forwarding Database, Service 600
===============================================================================
ServId     MAC               Source-Identifier       Type     Last Change
            Transport:Tnl-Id                         Age
-------------------------------------------------------------------------------
600        aa:c1:ab:22:12:61 sap:1/1/3:600           L/0      11/20/23 11:36:41
600        aa:c1:ab:af:99:a9 sdp:15258:4294967294    L/0      11/20/23 12:27:27
600        aa:c1:ab:d7:48:5e sdp:15513:4294967295    L/0      11/20/23 11:48:02
-------------------------------------------------------------------------------
No. of MAC Entries: 3
-------------------------------------------------------------------------------
Legend:L=Learned O=Oam P=Protected-MAC C=Conditional S=Static Lf=Leaf T=Trusted
===============================================================================
```


### Check MAC Address Table on RED-R2 L2VPN-600

```
A:admin@RED-R2# show service id "600" fdb detail

===============================================================================
Forwarding Database, Service 600
===============================================================================
ServId     MAC               Source-Identifier       Type     Last Change
            Transport:Tnl-Id                         Age
-------------------------------------------------------------------------------
600        aa:c1:ab:22:12:61 sdp:15257:4294967294    L/0      11/20/23 12:27:26
600        aa:c1:ab:af:99:a9 sap:1/1/3:600           L/0      11/20/23 12:27:26
600        aa:c1:ab:d7:48:5e sdp:15513:4294967295    L/0      11/20/23 12:21:11
-------------------------------------------------------------------------------
No. of MAC Entries: 3
-------------------------------------------------------------------------------
Legend:L=Learned O=Oam P=Protected-MAC C=Conditional S=Static Lf=Leaf T=Trusted
===============================================================================
```


### Check MAC Address Table on BLUE-R1 L2VPN-600

```
A:admin@BLUE-R1# show service id "600" fdb detail

===============================================================================
Forwarding Database, Service 600
===============================================================================
ServId     MAC               Source-Identifier       Type     Last Change
            Transport:Tnl-Id                         Age
-------------------------------------------------------------------------------
600        aa:c1:ab:22:12:61 sdp:15257:4294967295    L/0      11/20/23 11:47:56
600        aa:c1:ab:af:99:a9 sdp:15258:4294967294    L/0      11/20/23 12:27:27
600        aa:c1:ab:d7:48:5e sap:1/1/3:600           L/0      11/20/23 11:48:02
-------------------------------------------------------------------------------
No. of MAC Entries: 3
-------------------------------------------------------------------------------
Legend:L=Learned O=Oam P=Protected-MAC C=Conditional S=Static Lf=Leaf T=Trusted
===============================================================================
```



















