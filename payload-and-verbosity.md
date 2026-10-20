# Payload and Verbosity

So far tcpdump has reported packets
without opening them: header fields,
flags, lengths. But the packets are
right there, and for unencrypted
protocols their contents are printable.
This chapter climbs the verbosity
ladder — how much of each packet
tcpdump shows you — using the same lab
conversation at every rung.

## -v and -vv: more decoding

You met `-v` in chapter 3: it adds the
IP header's own fields (ttl, id, proto)
on a line above the TCP summary. `-vv`
adds more again — among it, checksum
*values* for the TCP header itself:

```
$ tcpdump -i lo -nn -vv -c 2 tcp port 45080
21:46:38.341252 IP (tos 0x0, ttl 64, id 10184, offset 0, flags [DF], proto TCP (6), length 60)
    127.0.0.1.59034 > 127.0.0.1.45080: Flags [S], cksum 0xfe30 (incorrect -> 0x7b6d), seq 4289131094, win 65495, options [mss 65495,sackOK,TS val 141706094 ecr 0,nop,wscale 10], length 0
```

(Chapters 3's warning applies doubly
here: the `(incorrect -> ...)` pair is
checksum offloading, seen because the
capture point sits before the hardware
finishes the sum — an artefact of where
you stand, not damage.)

Each rung costs readability. Default
output is a conversation you can follow
with your eyes; `-vv` is a protocol
dissection. Climb when the question is
about the layer the rung exposes, and
not before.

## -A: the payload as text

`-A` prints each packet's payload as
ASCII. For the lab's web conversation,
that turns the summary into the thing
itself:

```
$ tcpdump -i lo -nn -A -c 12 tcp port 45080
...
21:46:24.089752 IP 127.0.0.1.48680 > 127.0.0.1.45080: Flags [P.], seq 1:89, ack 1, win 64, options [nop,nop,TS val 2523687350 ecr 1669719864], length 88
E.....@.@.4..........(..P.v..*.....@.......
.li.c..8GET /index.html HTTP/1.1
Host: 127.0.0.1:45080
User-Agent: curl/8.5.0
Accept: */*
...
21:46:24.090567 IP 127.0.0.1.45080 > 127.0.0.1.48680: Flags [P.], seq 1:142, ack 89, win 64, options [nop,nop,TS val 1669719864 ecr 2523687350], length 141
...
c..9.li.HTTP/1.0 200 OK
Server: PacketLab/1.0
Date: Tue, 20 Oct 2026 21:46:24 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 209
...
21:46:24.090625 IP 127.0.0.1.45080 > 127.0.0.1.48680: Flags [P.], seq 142:351, ack 89, win 64, options [nop,nop,TS val 1669719864 ecr 2523687350], length 209
...
c..9.li.<!doctype html>
<title>Packet Lab - Specimen Page</title>
<h1>Packet Lab</h1>
<p>This page exists so tcpdump has something
honest to look at. Every byte of it crossed the
loopback interface to get to you.</p>
```

The request line, the headers (curl's
`User-Agent` naming itself), the
server's `Server: PacketLab/1.0` banner,
and the page body — all read straight
off the wire, because plain HTTP is
text and nothing about it is sealed.
Packets without payload print their
headers as a line or two of
punctuation-flavoured noise (`E.....@.@.
4...` is an IP header wearing ASCII it
was never meant to wear); the payload
packets are the ones worth reading.

The UDP echo is the same story, told
smaller — this is the entire exchange
from chapter 4, payloads open:

```
$ tcpdump -i lo -nn -A -c 2 udp port 45053
21:46:42.899205 IP 127.0.0.1.34204 > 127.0.0.1.45053: UDP, length 15
E..+.,@.@.>................*packets please

21:46:42.899386 IP 127.0.0.1.45053 > 127.0.0.1.34204: UDP, length 21
E..14.@.@.."...............0echo: packets please
```

Fifteen bytes out, twenty-one back,
both readable: the datagram *is* its
payload.

## -X: hex and ASCII together

`-X` prints each packet in hex with the
ASCII alongside — headers included,
which is what makes it the rung for
"show me exactly what was on the wire":

```
$ tcpdump -i lo -nn -X -c 5 tcp port 45080
21:46:34.311224 IP 127.0.0.1.47482 > 127.0.0.1.45080: Flags [S], seq 401168207, win 65495, options [mss 65495,sackOK,TS val 165597862 ecr 0,nop,wscale 10], length 0
	0x0000:  4500 003c dc6b 4000 4006 604e 7f00 0001  E..<.k@.@.`N....
	0x0010:  7f00 0001 b97a b018 17e9 574f 0000 0000  .....z....WO....
	0x0020:  a002 ffd7 fe30 0000 0204 ffd7 0402 080a  .....0..........
	0x0030:  09de d2a6 0000 0000 0103 030a            ............
```

Read the first bytes with chapter 3's
anatomy in hand: `45` is IPv4 with a
20-byte header, `003c` is the IP total
length (60), `4006` carries the DF flag
and protocol 6 (TCP), and `7f00 0001`
is 127.0.0.1 wearing hex. You will
rarely need this rung; when you do —
comparing two packets the summaries
claim are identical, checking padding,
reading a protocol nobody wrote a
decoder for — nothing else substitutes.

## -e: the link layer

`-e` prepends the frame's own header —
addresses and all:

```
$ tcpdump -i lo -nn -e -c 3 tcp port 45080
21:46:36.325722 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 74: 127.0.0.1.47484 > 127.0.0.1.45080: Flags [S], ...
```

Loopback has no hardware addresses, so
its "Ethernet" header is a costume of
zeros the kernel puts on so the traffic
has a familiar shape (`ethertype IPv4`
is the one honest field). On a real
Ethernet or Wi-Fi interface the same
rung shows real MAC addresses — the
layer you need when the question is
*which physical device* sent a frame,
or whether frames are arriving at all.

## Reading payloads honestly

Three cautions, all of which chapter 8
develops:

- **Text protocols only.** HTTP, the
  lab's echo, classic DNS — readable.
  Compressed, binary, or encoded
  payloads print as the same
  punctuation-flavoured noise as the
  headers above, and guessing at them
  proves nothing.
- **Encryption seals it.** The same
  `-A` against a TLS conversation
  (chapter 8) shows handshakes and
  silence where the request should be.
- **What you can read, so could anyone
  else at this vantage point.** The
  permission rule from chapter 1 is not
  decoration: an `-A` capture of someone
  else's plain-HTTP session is their
  mail, read.

Check: run the `-A` capture against the
UDP echo and the web fetch, and find
one packet whose `-A` tail is *only*
noise. (Any header-only packet — the
`[S]`, say: 60 bytes of headers, no
payload, pure costume ASCII.) And if
your capture has no handshake in it at
all, the lesson is ordering: start the
capture *before* running the driver,
not after. tcpdump cannot show you a
packet that crossed before it was
listening.
