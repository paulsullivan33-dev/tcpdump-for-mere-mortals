# Everyday Recipes

The recipes below are the captures the
earlier chapters built, aimed at the
questions people actually ask. Each was
run against the lab; each transfers to
a real interface by changing the
address, the port, and the interface
name — nothing else.

## "What is it asking DNS?"

DNS is the chattiest diagnostic on any
machine: before almost every
conversation, something asks for an
address. Watch port 53 on the
machine's outward interface:

```
$ tcpdump -i host0 -nn -c 4 port 53
  (second terminal: getent hosts packetlab.example.com)
listening on host0, link-type EN10MB (Ethernet), snapshot length 262144 bytes
21:46:51.872366 IP 198.19.0.2.48388 > 198.19.0.1.53: 12978+ [1au] AAAA? packetlab.example.com. (50)
21:46:51.877909 IP 198.19.0.1.53 > 198.19.0.2.48388: 12978* 0/0/0 (39)
21:46:51.878030 IP 198.19.0.2.46152 > 198.19.0.1.53: 7886+ [1au] A? packetlab.example.com. (50)
21:46:51.882004 IP 198.19.0.1.53 > 198.19.0.2.46152: 7886* 1/0/0 A 198.18.110.30 (55)
4 packets captured
```

tcpdump decodes DNS in its summary: the
query id (`12978`), the question
(`AAAA? packetlab.example.com.` — the
IPv6-address question first, then `A?`
for IPv4), and the answer's shape
(`1/0/0 A 198.18.110.30` — one answer
record, an address). The build
machine's resolver *invents* its
answers (198.18.x is its synthetic
range, a sandbox arrangement); on your
network the same recipe shows your real
resolver's real answers, and the query
names — which is usually the recipe's
whole point — are genuine either way.
"What did this machine look up, in what
order, and did anything answer" is a
question this capture settles outright.
Add `-A` and the names are readable
even where the summary decode isn't.

## "Did anything answer?"

A request with a problem has exactly
three shapes of reply, and the capture
distinguishes all of them. The lab
keeps a closed TCP port, 45999, for the
first:

```
$ tcpdump -i lo -nn -c 2 tcp port 45999
  (second terminal: curl -s http://127.0.0.1:45999/)
21:52:39.178756 IP 127.0.0.1.39882 > 127.0.0.1.45999: Flags [S], seq 1937587098, win 65495, options [mss 65495,sackOK,TS val 2341204049 ecr 0,nop,wscale 10], length 0
21:52:39.178769 IP 127.0.0.1.45999 > 127.0.0.1.39882: Flags [R.], seq 0, ack 1937587099, win 0, length 0
2 packets captured
```

**Refused.** The `[S]` goes out and a
`[R.]` — a reset — comes back within
13 microseconds: the host is there, the
port is shut, and it said so. curl
reports exit 7, connection refused, and
the capture proves the refusal was the
*host's*, not a network failure's.

UDP's refusal wears ICMP, because UDP
itself has no resets. The lab's closed
UDP specimen, 45998:

```
$ tcpdump -i lo -nn "udp port 45998 or icmp"
  (second terminal: printf "anyone there?\n" | nc -u -w 1 127.0.0.1 45998)
21:58:54.265209 IP 127.0.0.1.34353 > 127.0.0.1.45998: UDP, length 14
21:58:54.265227 IP 127.0.0.1 > 127.0.0.1: ICMP 127.0.0.1 udp port 45998 unreachable, length 50
2 packets captured
```

**Unreachable** — the stack answers for
the absent program: port unreachable,
in so many words.

The third shape is **silence**: the
`[S]` (or the datagram) goes out and
*nothing* comes back — the capture
shows the request repeated as the
client retries, each line identical
but for its timestamp. Silence means
the packets are being dropped on the
way, answered by a firewall's discard,
or addressed somewhere that can't
reply: everything a refusal rules out.
Telling "refused" from "silent" is
half of all network debugging, and it
is a two-packet capture.

## "Who keeps connecting?"

Chapter 4's flag test, worn as a
recipe: watch only connection attempts
to a service —

```
tcpdump -i lo -nn "tcp port 45080 and tcp[tcpflags] & tcp-syn != 0"
```

Every line is somebody starting
something: a client SYN or the server's
SYN-ACK. Run it against a real service
and you have a connection census with
timestamps, including the attempts
that never complete — the ones whose
third packet never comes, which are
the attempts worth asking about.

## "Who is talking the most?"

Save first (chapter 7), then count.
From the lab's own specimen file:

```
$ tcpdump -r specimen.pcap -nn | awk '{print $3}' | sort | uniq -c | sort -rn
      6 127.0.0.1.45080
      6 127.0.0.1.33162
      4 127.0.0.1
```

Field 3 of every line is the source
endpoint; the pipe tallies it. On
loopback the answer is a tie between
the conversation's two ends (6 and 6 —
the ICMP lines, 4, have no port to
print, which is why their "source" is a
bare address). On a real capture the
same pipeline names your loudest
talkers in order — the text-processing
guide in this series is the place to
take the idea further; this one-liner
is its most common first use.

## "Is it even leaving the machine?"

The cheapest sanity check in the
chapter, and the one that ends the most
arguments: capture on the *outward*
interface with a filter for the
destination — `tcpdump -i host0 -nn
host 203.0.113.10`, say — and then run
the failing client. Packets in the
capture: the failure is beyond your
machine. No packets: the failure is
*in* your machine (a name that resolved
elsewhere, a proxy setting, a route
that points somewhere you didn't
expect) — and chapter 9's first entry
is the extreme case, where the
operating system refuses the send
itself and the capture's emptiness is
the diagnosis.

Check: aim the refusal recipe at the
lab's closed *UDP* specimen with a TCP
filter (`tcp port 45998`). The capture
is empty, and correctly so — the
datagram and its unreachable are both
outside the filter's protocol. An empty
capture accuses the filter before it
accuses the network; this check is how
you learn to read it that way.
