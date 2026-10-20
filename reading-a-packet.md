# Reading a Packet

One line of tcpdump output is a whole
packet, compressed into a sentence.
This chapter teaches the sentence, using
the conversation you captured in
chapter 2. Here is its first line again:

```
21:45:00.913537 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [S], seq 4125593649, win 65495, options [mss 65495,sackOK,TS val 4059721481 ecr 0,nop,wscale 10], length 0
```

Read it in pieces:

- **`21:45:00.913537`** — the time the
  packet passed the interface, to the
  microsecond. (Chapter 7 shows `-tttt`,
  which prints the date too.)
- **`IP`** — the network protocol. IPv4
  here; IPv6 packets say `IP6`.
- **`127.0.0.1.55954 > 127.0.0.1.45080`**
  — source, arrow, destination. Each
  endpoint is *address.port*: the packet
  travels from port 55954 (an
  **ephemeral** port — a temporary one
  curl's machine picked for this
  conversation) to port 45080, where the
  lab listens.
- **`Flags [S]`** — the TCP flags, the
  packet's one-letter intentions. The
  table below is the vocabulary.
- **`seq 4125593649`** — the sequence
  number: where this packet's data sits
  in the sender's stream. On the first
  packet of a direction tcpdump prints
  the real, randomly-chosen starting
  number; after that it prints numbers
  *relative* to it, which is why the
  rest of the capture counts from 1.
- **`win 65495`** — the receive window:
  how many more bytes the sender of this
  packet is currently willing to accept.
- **`options [...]`** — TCP options
  negotiated mostly at the start: `mss`
  (biggest segment I'll accept), `sackOK`
  (selective acknowledgements allowed),
  `TS` (a timestamp pair: `val` mine,
  `ecr` the echo of yours), `wscale`
  (window scaling).
- **`length 0`** — payload bytes. Zero:
  this packet carries no data, only
  intentions.

## The flags, which are the plot

| Flag | Name | Meaning in the conversation |
|------|------|-------------------------------|
| `S`  | SYN  | "Let's talk — here is my starting number." |
| `S.` | SYN+ACK | "Agreed — here is mine, and I acknowledge yours." (The dot means ACK is also set.) |
| `.`  | ACK  | "Received, up to here." A bare acknowledgement. |
| `P.` | PSH+ACK | "Here is data, and please hand it up promptly." Data-bearing packets usually wear this. |
| `F.` | FIN+ACK | "I'm done sending." The polite goodbye. |
| `R` / `R.` | RST | "No. Connection refused, or torn down now." Chapter 6 meets it. |
| `U`, `E`, `W` | URG, ECE, CWR | Rare in everyday captures; named so they don't alarm you. |

## The conversation, walked

With the vocabulary in place, chapter
2's twelve lines read as a story in
four acts:

**The opening (packets 1–3).** The
client sends `[S]` with its starting
sequence 4125593649. The server answers
`[S.]`: its own start, 846308440, and
`ack 4125593650` — "the next byte I
expect from you is one past your SYN"
(a SYN consumes one sequence number,
like a byte of data that isn't). The
client's bare `[.]` with `ack 1` —
relative now: one past the server's
start — completes the **three-way
handshake**. Three packets, and no
application byte has moved yet.

**The request (packet 4).** `[P.]`,
`seq 1:89`, `length 88`: bytes 1
through 88 of the client's stream,
relative — an 88-byte payload, which
chapter 5 will show is the HTTP request
itself. The server's answering `[.]`
(packet 5) says `ack 89`: all of it
arrived.

**The reply (packets 6–9).** The server
sends its answer in two pushes: `seq
1:142, length 141` — the response
headers — then `seq 142:351, length
209` — the page body. Sequence numbers
let the client (and you) check the
pieces join up: 142 begins exactly
where 1:142 ended. Each push is
acknowledged in turn.

**The closing (packets 10–12).** The
server sends `[F.]` — done sending. The
client answers with its own `[F.]` —
it is done too — and the server's last
`[.]` acknowledges it. Two FINs, each
acknowledged: a TCP goodbye is a small
ceremony, and a capture that shows only
one FIN is a conversation that ended
with one side still talking, or dead.

## What -v adds: the IP layer

The default line decodes TCP and
summarises IP. `-v` shows IP's own
fields, in a line of their own:

```
21:45:11.976853 IP (tos 0x0, ttl 64, id 61270, offset 0, flags [DF], proto TCP (6), length 60)
    127.0.0.1.55600 > 127.0.0.1.45080: Flags [S], cksum 0xfe30 (incorrect -> 0xd9ab), seq 3283675106, win 65495, options [mss 65495,sackOK,TS val 2492640475 ecr 0,nop,wscale 10], length 0
```

- **`ttl 64`** — time to live: hops this
  packet may still cross before a router
  discards it. Loopback never crosses
  one, so it stays 64; on real paths the
  number counts down, and *differences*
  in it can hint how far away a sender
  sits.
- **`id`, `offset`, `flags [DF]`** — the
  fragmentation fields. `DF` is "don't
  fragment," set on nearly everything
  modern; a fragmented packet shows
  offsets and gets a troubleshooting
  look, not a chapter.
- **`proto TCP (6)`** — the payload's
  protocol, by name and number.
- **`length 60`** — the whole IP packet,
  headers included (the default line's
  trailing `length` was payload only).
- **`cksum ... (incorrect -> ...)`** —
  do not be alarmed, and do not skip
  this note: on a machine's *own*
  traffic, checksums are often computed
  by the network hardware *after*
  tcpdump's copy is taken (checksum
  offloading). tcpdump faithfully
  reports the not-yet-filled value as
  incorrect and shows what it computes
  instead. On loopback you will see it
  constantly; on a capture taken from a
  *different* machine watching the wire,
  the same packets carry finished
  checksums. It is an artefact of where
  you stand, not corruption — and
  chapter 9 keeps it so you don't chase
  it at 2 a.m.

Check: in your own chapter-2 capture,
find the packet whose `seq` range and
`length` don't match — there isn't one,
and checking that (each data packet's
range spans exactly its length) is how
you know you've read the numbers right.
