# Containerlab based Nokia Seamless-MPLS demo including pySROS and Event Handler System to simplify BGP-VPLS (RFC4761) configuration activities when using RSVP-TE signaled LSPs

The article Supporting this is at https://www.thingnetwork.io/pysros-and-event-handler-system-makes-bgp-vpls-easier/

This exercise describes is a simple Network that used BGP Labeled-Unicast (RFC3107) to build a Multi-OSPF area Seamless-MPLS network.

> If you are in a hurry and are just interested in the pySROS script and using it with EHS?
> The main areas of interest may be:
>
> * [The pySROS Script used for BGP-VPLS SDP creation](pysros-scripts/bgp-vpls-pathmaker.py)
> * [Registering the script into SROS](bgp-vpls-automation/PythonScriptRegistration.cfg)
> * [Enabling the Event Handler System invoke the Script when the right event occurs](bgp-vpls-automation/EventHandlerSystem.cfg)

The following scenarios are used to demonstrate some concepts behind BGP-VPLS (RFC4761) based deployments that need to be dealt with with Nokia SROS. Although these types of service constructs are less common for green-fields networks since maturity and near ubiquitous access of EVPN, there are existing networks that rely on this and understanding the behavior is helpful.

Also, these scenarios and the script were driven from some observations during a proof of concept and how things might be easier when using pySROS.


Unlike L3VPN (MPLS/BGP IP-VPN) Services which can leverage dynamically created LSPs for service transport,
L2VPN using BGP-VPLS instances on Nokia platforms require the use of SDPs (and LSPs).  Configuring these especially on networks that grow can become quite tedious, and this is where scripting via pySROS and the use of the Event Handler System can assist.

There are four scenarios that are described which build upon each other to help build an understanding on what the differences are between deploying L3VPN (VPRN) and L2VPN (BGP-VPLS) services are, and how through the use of on-router automation, BGP-VPLS services become nearly as simple to deploy.


|Scenario|Description|
|----|-----------|
|[The Base Infrastructure Build and Test Sequence](01_BaseInfrastructureBuildandTest.md)|Setting up the Base Infrastructure and confirming the Seamless-MPLS network is ready for service deployment|
|[The L3VPN (RFC4364 - MPLS/BGP IP-VPN) Build and Test Sequence](02_L3ServiceBuildandTest.md)|Deploying a Simple Full-Mesh L3VPN (VPRN) as a baseline to show how simple services should be to deploy. Once deployed, verifying that clients attached to the PE Routers are able to communicate with each other via the routed VPN|
|[The L2VPN (RFC4761 - VPLS with BGP Auto discovery and Signalling) Build and Test Sequence](03_L2ServiceBuildandTest.md)|Deploying a Simple Full-Mesh L2VPN (VPLS), realising that there is a requirement to manually provision SDPs between routers (this may include the need to provision additional RSVP-TE LSPs for the SDP to bind to). Then verifying that clients attached to the PE Routers are able to communicate with each other via the bridged VPN|
|[Using pySROS and Event Handler System for easier BGP-VPLS Service Provisioning](04_PySROSandEHS.md)|Enhancing the deployment of RFC4761 VPLS Using BGP (BGP-VPLS) for Auto-Discovery and Signaling using RSVP-TE signaled LSPs using pySROS and Event Handler System by using python scripts that can be executed by the router itself to find BGP-VPLS instances that require SDPs to be built and construct them (and any relevant RSVP-TE LSPs).  Then using the Event Handler System to invoke the script when it detects that a VPLS doesn't have a manually created SDP|

Each scenario is self-contained and can be run without having to have an early scenario executed.  This should be helpful for those that are more interested in directly looking at the example where PySROS scripts are used and linked to the Event Handler System. 

More information on pySROS can be found on it's github page - <https://github.com/nokia/pysros>

The Nokia Developer Portal also provides information on pySROS <https://network.developer.nokia.com/static/sr/learn/pysros/latest/introduction.html>

Containerlab is available at <https://containerlab.dev/>

This lab and associated python scripts are by Adam Booth and are free to use if it helps!
