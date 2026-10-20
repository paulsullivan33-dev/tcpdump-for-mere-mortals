# Filters

Chapter 2's capture was quiet because a
filter kept it that way. Remove the
filter and the same loopback, driven by
the same three small programs, looks
like this:

```
$ tcpdump -i lo -nn
  (second terminal: ping -c 2 127.0.0.1; curl -s http://127.0.0.1:45080/; printf "packets please\n" | nc -u -w 1 127.0.0.1 45053)
...
21:45:39.264559 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16554, seq 1, length 64
21:45:39.264574 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16554, seq 1, length 64
21:45:39.567190 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16554, seq 2, length 64
21:45:39.567206 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16554, seq 2, length 64
21:45:39.592398 IP 127.0.0.1.41696 > 127.0.0.1.45080: Flags [S], seq 364417795, win 65495, ...
... (the twelve-packet web conversation of chapter 2) ...
21:45:39.598667 IP 127.0.0.1.60935 > 127.0.0.1.45053: UDP, length 15
21:45:39.598831 IP 127.0.0.1.45053 > 127.0.0.1.60935: UDP, length 21

18 packets captured
36 packets received by filter
0 packets dropped by kernel
```

Eighteen packets: 4 ICMP, 12 TCP, 2 UDP,
all interleaved by time and nothing
else. On a real interface the unfiltered
view is that, multiplied by everything
the machine is doing. Filters are how
you ask for the one conversation you
came for.

## The language, briefly

Everything after the options is a filter
expression in the **BPF** language
(the `pcap-filter` manual page is its
full grammar). tcpdump compiles it,
hands it to the kernel, and the kernel
applies it to every packet — which is
why the footer's "received by filter"
counter is the *kernel's* count of
matches, and why filtering costs almost
nothing even on a busy link.

The building blocks:

| Primitive | Matches |
|-----------|---------|
| `host 127.0.0.1` | Packets to or from that address |
| `src host …` / `dst host …` | Only as source / only as destination |
| `net 127.0.0.0/8` | To or from that network |
| `port 45080` | TCP or UDP, to or from that port |
| `src port …` / `dst port …` | Directional ports |
| `portrange 45000-45100` | A span of ports |
| `tcp`, `udp`, `icmp` | That protocol (ICMP has no ports — note its lines carry none) |
| `ip`, `ip6` | That address family |

Combine with `and`, `or`, `not` (or
`&&`, `||`, `!`), group with
parentheses, and quote the whole
expression so the shell doesn't eat the
interesting characters. Two grammar
notes that bite everyone once:

- `not` binds to what follows it, and
  `and` binds tighter than `or`. When in
  doubt, parentheses — they are cheap,
  and a silently-wrong grouping produces
  a silently-wrong capture.
- `tcp port 45080` is the common shape:
  a protocol primitive narrowed by a
  port primitive. `port 45080` alone
  would also match a UDP conversation on
  that port, if one existed.

A filter that doesn't compile is
refused before capture starts — a
mercy, and loud about it:

```
$ tcpdump -i lo -nn "tpc port 45080"
tcpdump: can't parse filter expression: syntax error
```

(Filter errors are the honest kind: you
find them in the terminal, not in an
empty capture three days later.)

## Same burst, three filters

The lab burst above, re-run under
filters, shrinks exactly as the language
promises. Only the pings survive
`icmp` — the web conversation and the
UDP pair were still sent; the filter
just declined to show them:

```
$ tcpdump -i lo -nn -c 4 icmp
21:45:55.587364 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16589, seq 1, length 64
21:45:55.587375 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16589, seq 1, length 64
21:45:55.895147 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16589, seq 2, length 64
21:45:55.895166 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16589, seq 2, length 64
4 packets captured
```

`or` admits the UDP conversation too —
six lines, the same four ICMP plus the
pair:

```
$ tcpdump -i lo -nn -c 6 "icmp or udp port 45053"
...
21:45:57.925281 IP 127.0.0.1.46928 > 127.0.0.1.45053: UDP, length 15
21:45:57.925404 IP 127.0.0.1.45053 > 127.0.0.1.46928: UDP, length 21
6 packets captured
```

## One honest power tool

The language can test bytes inside the
packet, not only addresses. The classic
use is "show me only connection
*attempts*": a packet with the SYN flag
set —

```
$ tcpdump -i lo -nn -c 2 "tcp[tcpflags] & tcp-syn != 0"
21:45:59.624019 IP 127.0.0.1.41564 > 127.0.0.1.45080: Flags [S], seq 1544696929, win 65495, options [mss 65495,sackOK,TS val 3609135553 ecr 0,nop,wscale 10], length 0
21:45:59.624038 IP 127.0.0.1.45080 > 127.0.0.1.41564: Flags [S.], seq 3512323252, ack 1544696930, win 65483, options [mss 65495,sackOK,TS val 1728529377 ecr 3609135553,nop,wscale 10], length 0
2 packets captured
```

`tcp[tcpflags]` names the flags byte of
the TCP header; `& tcp-syn != 0` keeps
packets where the SYN bit is lit — the
client's `[S]` and the server's `[S.]`,
and nothing else of the twelve. This is
as deep as the byte-surgery goes in
this guide: one expression, fully
explained, genuinely useful (chapter 6
builds a recipe on it). The grammar
allows far more; the `pcap-filter`
manual page is the honest place to learn
it, with a live capture open beside
you.

Check: predict, then run. Under
`"tcp port 45080 and tcp[tcpflags] &
tcp-syn != 0"`, how many lines does the
lab's curl conversation produce? (Two:
the same opening pair — the port
primitive and the flag test both have
to pass.) If you got four, your filter
has an `or` where this one has an
`and`.
