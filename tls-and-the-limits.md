# TLS and the Limits of Capture

Chapter 5 read a web conversation like
a postcard. This chapter runs the same
trick against the same page wearing
TLS, and watches it fail — on purpose,
because knowing exactly where a
capture's vision ends is worth more
than another recipe. It ends with the
limits that have nothing to do with
encryption: truncated packets, dropped
packets, and the traffic that was never
yours to hear.

## The encrypted conversation

The lab's second fixture serves the
specimen page over HTTPS on tcp/45443,
with a self-signed certificate made
for the occasion (the OpenSSL guide in
this series is the place for the
ceremony's details; the receipts are):

```
$ openssl req -x509 -newkey rsa:2048 -nodes -keyout lab-key.pem -out lab-cert.pem -days 30 -subj "/CN=lab.test" -addext "subjectAltName=DNS:lab.test"
$ openssl x509 -in lab-cert.pem -noout -subject -ext subjectAltName
subject=CN = lab.test
X509v3 Subject Alternative Name:
    DNS:lab.test
```

Fetch it with `curl -k` (accept the
self-signed cert) and a name to match
it — `--resolve lab.test:45443:127.0.0.1`
points the invented name at the lab —
under the same `-A` capture that read
plain HTTP like a book:

```
$ tcpdump -i lo -nn -A tcp port 45443
  (second terminal: curl -k --noproxy "*" --resolve lab.test:45443:127.0.0.1 https://lab.test:45443/)
...
21:51:45.695329 IP 127.0.0.1.51454 > 127.0.0.1.45443: Flags [P.], seq 1:518, ack 1, win 64, options [nop,nop,TS val 3344905795 ecr 2250498051], length 517
...
...9.	...3.....=.<.5./.....u.........lab.test.........
...............................h2.http/1.1.........1...
...
15 packets captured
```

(The `--noproxy` is the build machine's
own arrangement — its shell sends
foreign names to a proxy, and the flag
keeps this request at home. Your
machine won't need it unless it, too,
proxies.)

The conversation's *shape* is all
there: handshake, a 517-byte first
flight from the client, the server's
1,356-byte answer, then sealed packets
of 80, 99, 255, 645 bytes — the request
and the page, in armoured envelopes
whose sizes and timings are perfectly
visible. And inside the client's first
flight, two things are legible in the
ASCII dump, because the TLS handshake
begins in the clear: **`lab.test`** —
the **SNI**, the name the client asked
for, sent openly so servers can choose
a certificate — and the offered protocol
list, `h2.http/1.1`.

Everything after the handshake is
envelope. The proof is a grep, run on
the capture itself:

```
$ grep -c "GET /" tls-raw.txt
0

$ grep -a "lab.test" tls-raw.txt | head -1
...9.	...3.....=.<.5./.....u.........lab.test.........
```

Chapter 5's capture of the same page
contains `GET /index.html` in plain
sight; this one contains it zero times.
That is the honest summary of passive
TLS analysis: **the metadata is yours —
endpoints, ports, timing, sizes, the
SNI name, the fact a conversation
happened at all — and the content is
not.** Anyone who tells you their
capture "shows the HTTPS traffic" is
showing you envelopes.

Two footnotes, labelled as what they
are. First, decryption *is* possible
when you hold one end's secrets: a
browser or server can be told to log
session keys (`SSLKEYLOGFILE`), and
Wireshark — chapter 1's relative — can
use that log to open a capture after
the fact. That is a *cooperative*
endpoint arrangement, not a passive
power, it is not installed or run on
the build machine, and this guide
doesn't teach it; it exists, and now
you know its name. Second, SNI's
openness is being closed by degrees
(ECH, encrypted ClientHello) in the
wider world; the lab's handshake
predates nobody — it simply shows what
this handshake, on this day, exposed.

## Snaplen: when the copy is shorter than the packet

tcpdump copies up to the **snapshot
length** (`-s`, "snaplen") of each
packet. The default on this build is a
generous 262144, printed in every
capture's header. Shrink it and the
headers — which tcpdump decodes from
the first bytes — still report the
packet's *true* lengths, while the
bytes you kept end early:

```
$ tcpdump -i lo -nn -A -s 100 -c 6 tcp port 45080
tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 100 bytes
...
21:48:47.716417 IP 127.0.0.1.34196 > 127.0.0.1.45080: Flags [P.], seq 1:89, ack 1, win 64, options [nop,nop,TS val 924303769 ecr 734135804], length 88
7...+...GET /index.html HTTP/1.1
21:48:47.717604 IP 127.0.0.1.45080 > 127.0.0.1.34196: Flags [P.], seq 1:142, ack 89, win 64, options [nop,nop,TS val 924303769 ecr 734135804], length 141
```

The request packet still confesses its
first line (it fits), and the response
packet still *claims* `length 141` —
but search this capture for the page's
text and it is simply not there: a
string the full capture contains twice
appears in this one zero times. Small
snaplens are a deliberate economy on
very busy links (headers kept, payloads
shed), and a quiet trap the rest of the
time. Rule of thumb: unless you are
fighting volume, leave `-s` alone — the
default already keeps everything a
mortal's disk will hold.

## Drops: the capture is a sample, and it says so

Every footer in this guide reports
`0 packets dropped by kernel`. That
zero is a fact about a quiet loopback,
not a promise. On a busy interface the
kernel's capture buffer can fill faster
than tcpdump empties it, and the
overflow is *counted, not hidden*: the
footer's dropped number is exactly the
count of packets the filter matched
that never reached you. A capture with
drops is a sample — representative,
probably, but a sample — and any
argument of the form "the packet never
arrived, see, it's not in the capture"
is void where drops are nonzero.
tcpdump's `-B` flag enlarges the buffer
when you must fight for completeness;
the mortal's first move is cheaper: a
tighter capture filter (chapter 4),
because every packet the kernel never
has to hand you is one it can't drop.

## Promiscuous mode: the honest version

By default libpcap asks the interface
to also deliver packets addressed to
*other* hardware addresses on the
segment — **promiscuous mode** (`-p`
turns it off). On the networks of
tcpdump's youth — shared cables, hubs —
that meant hearing the whole room. On a
modern switched network, the switch
delivers to your port only your own
traffic plus broadcasts, and promiscuous
mode cannot conjure what the switch
never sends you. The build machine
makes the point at its extreme: its one
external link is point-to-point, and
its chapter-6 DNS capture — promiscuous
by default, like every capture here —
contains exactly its own queries and
their answers, because nothing else
travels that wire. Promiscuous mode is
real, the permission rule of chapter 1
is written for it, and on contemporary
networks its practical reach is mostly
your own machine's traffic and whatever
your switch sends you anyway. Anyone
selling it as invisibility-cloak
espionage is describing 1997.

Check: in the shipped
`examples/specimen.pcap`, no packet is
encrypted, no packet is truncated, and
the footer (chapter 7) reports no
drops — three limits, all absent, which
is why the lab is a kind place to
learn. Before trusting a *field*
capture, ask its footer the drop
question and its header the snaplen
question; the answers are printed
there, by a tool that does not shade
them.
