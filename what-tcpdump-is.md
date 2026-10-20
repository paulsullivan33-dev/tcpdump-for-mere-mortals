# What tcpdump Is

**tcpdump** is the command line's way of
watching network traffic go past: one
tool, free since the late 1980s, that
sits at a network interface and reports —
packet by packet, with timestamps — what
actually crossed it. Not what a program
*claims* it sent. Not what a log says
happened. The packets themselves, as they
were on the wire.

Its siblings in this series ask
questions. Nmap knocks on ports and
reports what answered; netcat holds one
conversation by hand. tcpdump does
neither. It does not knock, and it does
not speak. It *listens*, and listening
turns out to answer a different set of
questions — the ones that start when a
conversation you can already make isn't
behaving the way you expected:

- Did the request ever leave this
  machine?
- Did anything answer — and if so, what
  kind of answer: a reply, a refusal, or
  silence?
- Is the client really talking to the
  port I think it is?
- Who is this machine actually exchanging
  traffic with, and how much?

Those are debugging questions, and
tcpdump is a debugging tool. You reach
for it when guessing has stopped working
and you want to *see*.

## The one idea: capture is passive

Everything tcpdump knows, it learns by
being handed a copy of each packet as
the packet passes through an interface
it is watching. It injects nothing. A
capture can therefore prove a packet
existed, and it can only *suggest* why a
packet is absent: absence has a hundred
causes, and chapter 9 opens with one —
a packet the operating system refused to
send never existed at all, and the
capture's silence is the honest shape of
that fact.

Passive also means tcpdump is invisible
to the conversation it watches — on your
own machine. Which is the right moment
for the rule.

## The rule

tcpdump can hear everything its
interface can hear, and on a shared
network segment an interface can hear a
great deal that was never addressed to
it (chapter 8 explains the mechanics and
their modern limits). Hearing other
people's traffic is not a grey area
that cleverness makes safe:

> **Only capture traffic on machines and
> networks you own or administer — or
> have explicit permission to monitor.**

A capture file is a recording of
everything that crossed, payloads
included when they aren't encrypted, so
treat one the way you'd treat a
microphone transcript: sensitive by
default, kept on purpose, deleted on
purpose. Everything in this guide
happens on the loopback interface of one
machine, talking to a lab planted there,
so the rule costs nothing to keep —
exactly like its nmap and netcat
siblings.

## It needs privilege, on purpose

Because capture hears everything, the
operating system gates it. On Linux,
tcpdump needs root (or the
`CAP_NET_RAW` capability). Run as an
ordinary user, it refuses — plainly, and
immediately:

```
$ su -s /bin/sh nobody -c "tcpdump -i lo -nn -c 1"
tcpdump: lo: You don't have permission to perform this capture on that device
(socket: Operation not permitted)
```

That refusal was captured on the build
machine, not paraphrased. Every capture
in this guide ran as root, and the
chapters say so by the prompts they
show: where a capture matters, it was
made with privilege deliberately taken.

## The family: Wireshark and tshark

tcpdump has a famous relative.
**Wireshark** reads the same capture
files in a graphical window — follow a
conversation with a click, decode a
thousand protocols, colour everything.
**tshark** is Wireshark's engine as a
command-line program: tcpdump's shape
with Wireshark's decoders behind it.
Neither is installed on the build
machine, and this guide teaches neither;
it stays with tcpdump, because tcpdump
is the one that is *already there* — on
the router, the rescue image, the
minimal container, the twenty-year-old
server. Chapter 7's capture files are
the bridge: anything you save with
tcpdump, Wireshark can open later, on a
bigger screen, with the same packets in
it.

## The lab

Two fixtures, both in `examples/`:

```
$ python3 examples/lab_server.py --check
packet fixture: tcp/45080 http + udp/45053 echo, on 127.0.0.1
page: Packet Lab - Specimen Page (Server: PacketLab/1.0)
deliberately closed specimens: tcp/45999, udp/45998 (nothing binds them)
```

- `examples/lab_server.py` — a specimen
  web server on tcp/45080 serving one
  invented page, and a UDP echo on
  udp/45053 that answers every datagram
  with `echo: ` in front of it. Nothing
  binds tcp/45999 or udp/45998: a genuine
  refusal and a genuine silence, kept in
  stock.
- `examples/lab_tls_server.py` — the
  same specimen page under TLS on
  tcp/45443, for chapter 8, using a
  self-signed certificate you make with
  the openssl commands shown there.
- `examples/specimen.pcap` — a real
  capture made from this lab (one web
  conversation, two pings), so chapter
  7's reading lessons work even before
  you capture anything yourself.

The drivers are the tools already on
your machine: `curl` for web traffic,
`ping` for ICMP, and `nc` for the UDP
echo — the cast of the earlier guides,
now with an audience.

Check: with the fixture running
(`python3 examples/lab_server.py` in its
own terminal), `curl -s
http://127.0.0.1:45080/` returns the
specimen page. Chapter 2 starts from
exactly that conversation — watched,
this time, instead of read.

## Have you got it?

```
$ tcpdump --version
tcpdump version 4.99.4
libpcap version 1.10.4 (with TPACKET_V3)
OpenSSL 3.0.13 30 Jan 2024
```

Every capture in this guide ran on this
tcpdump and this libpcap, installed
fresh on the build machine with
`apt-get install tcpdump`. tcpdump's
printed half is forty years refined and
behaves the same everywhere; libpcap is
the half that talks to your operating
system, and its version is the one that
decides what your machine lets it hear.
