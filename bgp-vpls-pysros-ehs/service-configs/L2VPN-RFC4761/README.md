In this demo, the Nokia Routers configured with BGP-VPLS Services leverage
PseudoWire Templates that expect a preprovisioned SDP to be available.
This is necessary when using RSVP-TE based service transport.

Out of the box there is no SDP configuration for these services available
resulting in a failure for end-to-end connectivity.

All is not lost however, while it is possible to manually configure the SDPs
and if nececessary an additional RSVP-TE LSP to bind the SDP to - whenever an
additional site joins the VPLS - the risk of needing to configure these are
present.

Through the use of a PYSROS script that can check if there are BGP-VPLS routes
that do not have an associate SDP and then create them (and LSP if needed),
this takes a lot of the tediousness away

Invoking the PYSROS script could be a manual affair, however by linking this
to the Event Handler System - we take advantage of system log events that are
related to the BGP-VPLS and missing SDPs invoking the script on demand
