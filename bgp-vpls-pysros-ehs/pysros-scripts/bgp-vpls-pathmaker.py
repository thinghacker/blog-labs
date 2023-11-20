import sys
from pysros.management import connect
from pysros.management import sros

# Set to DEBUG = False when running normally
DEBUG = True


def find_missing_sdps(router):
    """Search the routes in each BGP-VPLS for missing SDPs

    Return a list of next-hop IPs that will need a manual SDP created
    """

    state_vpls = router.running.get("/nokia-state:state/service/vpls")

    sdpnhlist = []
    for vpls, vplsdata in state_vpls.items():
        if DEBUG:
            print("Checking VPLS " + vpls + ":")
        vplsbgproutes = {}
        if "bgp-vpls" in vplsdata.keys() and "routes" in vplsdata["bgp-vpls"]:
            vplsbgproutes = vplsdata["bgp-vpls"]["routes"]
        for vplsroute, vplsroutedata in vplsbgproutes.items():
            tsdpbindid = None
            tnexthop = None
            terror = None
            for k, v in vplsroutedata.items():
                if str(k) == "next-hop-address":
                    tnexthop = str(v)
                if str(k) == "error-message":
                    terror = str(v)
            if terror == "suitable manual SDP not found":
                sdpnhlist.append(tnexthop)
                if DEBUG:
                    print("Need SDP to " + tnexthop)
    sdpnhlist = set(sdpnhlist)
    return sdpnhlist


def getpl_network(router, plname):
    """Return the Network Portion from a named Prefix-List"""

    conf_access_pl = router.running.get(
        "/nokia-conf:configure/policy-options/prefix-list"
    )

    network = None
    for k, v in conf_access_pl[plname]["prefix"].items():
        if "ip-prefix" in v:
            network = str(v["ip-prefix"])
    return network


# This function was described on Stackoverflow by Danilo
# https://stackoverflow.com/questions/2733788
def ip2bin(ip):
    """Converts an IP Address to a binary string

    the number of bits returned is dependant on prefix-length if provided"""

    octets = map(int, ip.split("/")[0].split("."))  # '1.2.3.4'=>[1, 2, 3, 4]
    binary = "{0:08b}{1:08b}{2:08b}{3:08b}".format(*octets)
    range = int(ip.split("/")[1]) if "/" in ip else None
    return binary[:range] if range else binary


def create_sdp_bgptunnel(router, sdpid, sdpdest):
    """Create an SDP that supports bgp-tunneling

    Assumes that there is already an LSP to the BGP-LU ABR"""

    template = {
        "sdp-id": sdpid,
        "admin-state": "enable",
        "description": "bgp-vpls-pathmaker.py - " + sdpdest + " BGP-LU",
        "delivery-type": "mpls",
        "signaling": "bgp",
        "bgp-tunnel": True,
        "far-end": {"ip-address": sdpdest},
    }
    if DEBUG:
        print("Creating SDP " + str(sdpid) + " with BGP-Tunnel to " + sdpdest)

    router.candidate.set("/nokia-conf:configure/service/sdp", template, commit=True)


def find_manual_rsvp_lsp(router, dest):
    """Find existing manually defined LSPs to the destination"""

    state_tt = router.running.get(
        '/nokia-state:state/router[router-name="Base"]/tunnel-table/ipv4/tunnel'
    )

    # Make a dict using the tunnelid as key and destination as value
    # This is used in the lsp section to determine what the IP destination of LSP is
    tunneltable = {}
    for tunnel, tunneldata in state_tt.items():
        tempttunelldata = tunneldata
        tid = None
        tdest = None
        for k, v in tempttunelldata.items():
            if str(k) == "id":
                tid = str(v)
            if str(k) == "ipv4-prefix":
                tdest = v.split("/")[0]
        tunneltable[tid] = {"dest": tdest}

    state_mpls = router.running.get(
        '/nokia-state:state/router[router-name="Base"]/mpls'
    )

    # Find an LSP that has the right destination that is manually
    # created (not using an origin-template)
    candidatelsp = None
    for lsp, lspdata in state_mpls["lsp"].items():
        if (
            len(lspdata["origin-template"]) == 0
            and str(lspdata["ttm-tunnel-id"]) in tunneltable.keys()
            and tunneltable[str(lspdata["ttm-tunnel-id"])]["dest"] == dest
        ):
            candidatelsp = str(lspdata["lsp-name"])
    return candidatelsp


def create_manual_rsvp_lsp(router, dest):
    """Create a manual RSVP-TE lsp"""

    lspname = "BGPVPLS-" + dest
    template = {
        "lsp-name": lspname,
        "to": dest,
        "type": "p2p-rsvp",
        "primary": {"path-name": "LOOSE"},
        "rsvp-resv-style": "ff",
        "adspec": True,
        "path-computation-method": "local-cspf",
        "fast-reroute": {"frr-method": "one-to-one"},
        "admin-state": "enable",
    }
    if DEBUG:
        print("Creating RSVP-TE LSP " + lspname + " to " + dest)

    router.candidate.set(
        '/nokia-conf:configure/router[router-name="Base"]/mpls/lsp',
        template,
        commit=True,
    )
    return lspname


def create_sdp_rsvptunnel(router, sdpid, sdpdest):
    """Create an SDP and bind it to an LSP (create it if necessary)"""

    # Find an existing LSP that can be used, otherwise create one
    lspname = find_manual_rsvp_lsp(router, sdpdest)
    if lspname == None:
        if DEBUG:
            print("No manually created LSP to " + sdpdest + " found")

            lspname = create_manual_rsvp_lsp(router, sdpdest)

    template = {
        "sdp-id": sdpid,
        "admin-state": "enable",
        "description": "bgp-vpls-pathmaker.py - " + sdpdest + " RSVP",
        "delivery-type": "mpls",
        "signaling": "bgp",
        "far-end": {"ip-address": sdpdest},
        "lsp": {"lsp-name": lspname},
    }
    if DEBUG:
        print(
            "Creating SDP "
            + str(sdpid)
            + " with RSVP-Tunnel to "
            + sdpdest
            + " with LSP "
            + lspname
        )

    router.candidate.set("/nokia-conf:configure/service/sdp", template, commit=True)


def connect_router():
    """Creates the session into the router for communications

    Uses default values if not run on the commandline and not
    otherwise set"""

    if sros():
        # Am running directly on the router
        session = connect()
    else:
        # Am running external to the router

        # these are the default parameters that will be used unless
        # overriden on the commandline when invoking the script
        router = "clab-interop-RED-R2"
        username = "admin"
        password = "admin"
        if len(sys.argv) > 1:
            router = sys.argv[1]
            if len(sys.argv) == 4:
                username = sys.argv[2]
                password = sys.argv[3]
        try:
            session = connect(
                host=router, username=username, password=password, hostkey_verify=False
            )
        except RuntimeError as error1:
            print("Failed to connect.  Error: ", error1)
            sys.exit(-1)
        except ModelProcessingError as error2:
            print("Failed to create model-driven schema.  Error: ", error2)
            sys.exit(-2)
    return session


def main():
    """Find BGP-VPLS instances that need SDPs created and make them"""

    session = connect_router()
    accessnetwork = getpl_network(session, "ROUTER-ACCESS-NET")
    if DEBUG:
        print("Access Network: " + accessnetwork)
    sdps = find_missing_sdps(session)
    for sdpdest in sdps:
        # The generated sdpid will have an ID of 15000 plus the last 15
        # bits of the Destination IP Address
        sdpid = 15000 + int(ip2bin(sdpdest)[17:], 2)
        if DEBUG:
            print("SDP " + str(sdpid) + " to " + sdpdest + " to be created")
        if ip2bin(sdpdest).startswith(ip2bin(accessnetwork)) == True:
            if DEBUG:
                print(" Local RSVP SDP required")
            create_sdp_rsvptunnel(session, sdpid, sdpdest)
        else:
            if DEBUG:
                print(" BGP Tunnel SDP required")
            create_sdp_bgptunnel(session, sdpid, sdpdest)


if __name__ == "__main__":
    main()
