Tool for making iOS 17+ RSD tunnels

It has been written to be as minimal as possible to enable the following:
1. Creating QUIC RSD tunnels for iOS 17+ devices
1. Creating TCP RSD tunnels for iOS 17.4+ devices
1. "Lockdown pairing" iOS devices
1. "Remote pairing" iOS 17+ devices
1. Doing all of the above without running any Python code as root.
1. Support iPhone XR, XS, and beyond ( iOS 17 devices )

In order to minimize the dependencies of the project a few choices have been made:
1. cryptography module is avoided outside of use of bits of it
within the qh3 library being depended on. This is to avoid the large size of the library, as
well as the non-standard way it works that would make it hard to port this project to C.
For ECC, PyNaCL module is used.
1. oscrypto module is used. It is small and great for creating certificates, which is needed
for pairing. It hasn't been done yet, but oscrypto can handle socket SSL wrapping also, which
will enable the project to avoid depending on the Python SSL module, which is problematically
dependent on OpenSSL, which is bad for use of this embedded in an app.
1. MDNS service discovery requests are created manually and the response parsed manually to
avoid the use of the dnslib module. The dnslib module is small ( 500kb ) so this is an
over-optimization. https://github.com/dryark/py_cf_mdns is used.
1. hkdf has been written in as it's tiny and pointless to use a library for it.

The utun interactivity has been rewritten to use "external utuns".
An example of one way to do this is in external_utun.py

The code has been changed to suspend / resume remoted using an external c program via shell-out.

The project runs on both macOS and Linux. Windows is not an intended target.

## Linux Support

On Linux, the `tunnel` command (USB/lockdown path) is fully supported. The
`remote-tunnel`, `remote-list`, and `remote-pair` commands require the
[py_cf_iface](https://github.com/dryark/py_cf_iface) library to be ported
to Linux as well (in progress).

### Linux Requirements

- `usbmuxd` running (for USB device communication)
- `pytun-pmd3` Python package (installed automatically via requirements.txt)
- `CAP_NET_ADMIN` capability or root privileges (for TUN interface creation)

### Running on Linux

```bash
pip3 install -r requirements.txt

# The tunnel command requires root or CAP_NET_ADMIN for TUN creation
sudo python3 -m ios_rsd_tunnel tunnel -u <UDID>

# Or grant capability to Python directly (avoids running as root):
# sudo setcap cap_net_admin+ep $(readlink -f $(which python3))
# python3 -m ios_rsd_tunnel tunnel -u <UDID>
```
