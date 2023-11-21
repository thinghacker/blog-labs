# This script (including all errors) was assembled by Adam Booth using ideas
# from others including the pysros documentation, example code and stackoverflow
# it probably isn't production grade but it seems to work well enough to
# demonstrate that it has potential!
import sys
from pysros.management import connect, sros
from pysros import pprint

# used for remote script execution
try:
    from pysros.errors import *
except:
    pass
# ANSI Colors
bright_cyan = "\u001b[36;1m"
bright_red = "\u001b[31;1m"
bright_green = "\u001b[32;1m"
reset_color = "\u001b[0m"


def name_sysip(router):
    print(
        "NE:"
        + bright_green
        + str(router.running.get("/nokia-state:state/system/oper-name"))
        + reset_color
        + "(System Address:"
        + str(
            router.running.get(
                '/nokia-state:state/router[router-name="Base"]/interface[interface-name="system"]/ipv4/primary/oper-address'
            )
        )
        + ")"
    )


def mactable(router, vplsname):
    state_vpls = router.running.get("/nokia-state:state/service/vpls")
    for vpls in state_vpls.keys():
        # find the VPLS instances we are interested in (if any)
        if (
            "fdb" in state_vpls[vpls].keys()
            and "mac" in state_vpls[vpls]["fdb"].keys()
            and (str(vpls) == vplsname or vplsname == "all")
        ):
            print(bright_cyan + "VPLS:" + bright_red + vpls + reset_color)
            pprint.printTree(state_vpls[vpls]["fdb"]["mac"])


def usage():
    print("pyexec", sys.argv[0])
    print("Options:")
    # we only care about connectivity options when running remotely
    if not sros():
        print(" --user {or -u} USERNAME")
        print(" --pass {or -p} PASSWORD")
        print(" --router {or -r} HOSTNAME/IP (or multiple separated by :)")
    print(" --vpls {or -v} VPLSNAME (or all)")


if __name__ == "__main__":
    # default parameters
    user = "admin"
    passw = "admin"
    routers = "1.2.3.4"
    vpls = "all"

    # display usage information if no arguments are passed
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    # parse command arguments (SROS boxes do not have many built in modules)
    for opt, val in zip(sys.argv[1::2], sys.argv[2::2]):
        if opt in ["-u", "--username"]:
            user = val
        if opt in ["-p", "--password"]:
            passw = val
        if opt in ["-v", "--vpls"]:
            vpls = val
        if opt in ["-r", "--routers"]:
            routers = val
    # we don't want attempt to loop multiple times is this is running on the rotuer directly
    if sros():
        routers = "127.0.0.1"
        exceptlist = RuntimeError
    else:
        exceptlist = (RuntimeError, SrosMgmtError)
    # this can run multiple routers
    for router in routers.split(":"):
        # session is the handle to the router
        try:
            session = connect(host=router, username=user, password=passw, hostkey_verify=False)
        except exceptlist as err:
            print("router:", router, str(err))
            sys.exit(-1)
        if not sros():
            # display the hostname and system address of the NE
            name_sysip(session)
        # display the MAC FDB(s)
        mactable(session, vpls)
        print("#" * 40)
