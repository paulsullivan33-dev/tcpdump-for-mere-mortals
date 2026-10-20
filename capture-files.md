# Capture Files

A capture on a terminal scrolls away,
and the interesting packet is always
the one that scrolled. Writing captures
to a file is the habit that turns
tcpdump from a live toy into a record:
the file can be re-read, re-filtered,
summarised, attached to a bug report, or
opened in Wireshark on another machine
— and it says exactly what it said the
first time.

## Writing: -w

```
$ tcpdump -i lo -nn -Z root -w specimen.pcap "tcp port 45080 or icmp"
  (second terminal: curl -s http://127.0.0.1:45080/; ping -c 2 127.0.0.1)
tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
16 packets captured
32 packets received by filter
0 packets dropped by kernel

$ ls -l specimen.pcap
-rw-rw---- 1 root nogroup 1908 Oct 20 21:47 specimen.pcap

$ file specimen.pcap
specimen.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Ethernet, capture length 262144)
```

Sixteen packets — the whole web
conversation plus two pings — in 1,908
bytes of **pcap**, the standard capture
format: a small header, then each
packet's timestamp, true length,
captured length, and bytes. With `-w`,
tcpdump prints nothing per packet; the
chatter goes to the file and only the
footer remains on stderr. (The footer
counts all three numbers, as in chapter
2.)

The `-Z root` needs its sentence,
because it is the one flag here that is
the build machine's, not tcpdump's.
Run as root, tcpdump drops privileges
to an unprivileged user (`tcpdump`) and
makes the savefile that user's. On this
build machine the ownership change is
refused by the environment, and without
`-Z` the run fails outright — chapter 9
keeps the error and the 24-byte
header-only file it leaves behind.
`-Z root` says "drop to root instead,"
which the environment accepts. On an
ordinary machine, run tcpdump as root
(or with `sudo`) and plain `-w` works
exactly as documented; if you ever meet
the ownership error on a locked-down
box of your own, you now own its fix
too.

A copy of this very file ships as
`examples/specimen.pcap`, so the rest
of the chapter works before you've
captured anything.

## Reading: -r, and filtering twice

```
$ tcpdump -r specimen.pcap -nn
21:47:29.638439 IP 127.0.0.1.33162 > 127.0.0.1.45080: Flags [S], seq 2946274604, win 65495, ...
... (all sixteen packets, in capture order) ...
21:47:29.951156 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16842, seq 2, length 64
```

Reading is printing, from the file
instead of the wire — every display
flag works, and so do filters, applied
*again*, at read time:

```
$ tcpdump -r specimen.pcap -nn icmp
21:47:29.645408 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16842, seq 1, length 64
21:47:29.645419 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16842, seq 1, length 64
21:47:29.951141 IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 16842, seq 2, length 64
21:47:29.951156 IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 16842, seq 2, length 64
```

That pair of habits — capture wide,
filter at leisure — is the professional
pattern. The filter at capture time is
a decision you can't unmake; the filter
at read time is a question you can keep
asking. Capture-time filters still earn
their place on busy links (chapter 8's
drops are why), but when disk is cheaper
than regret, save more than you think
you need.

`-tttt` belongs to reading: it prints
each packet's full date beside the
time, turning a wall of `21:47:29`s
into a timeline a report can quote:

```
$ tcpdump -r specimen.pcap -nn -tttt | head -3
2026-10-20 21:47:29.638439 IP 127.0.0.1.33162 > 127.0.0.1.45080: Flags [S], seq 2946274604, win 65495, ...
```

## Rotation: -G and -W

A capture left running needs a leash.
`-G seconds` starts a new file every so
often (the filename is a `strftime`
pattern, so the time is *in* the name);
`-W count` caps how many files the
capture keeps:

```
$ tcpdump -i lo -nn -Z root -G 2 -W 3 -w rot-%H%M%S.pcap icmp
  (second terminal: ping -c 8 -i 0.7 127.0.0.1)
tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
Maximum file limit reached: 3
13 packets captured

$ ls -l rot-*.pcap
-rw-rw---- 1 root nogroup 252 Oct 20 21:48 rot-214813.pcap
-rw-rw---- 1 root nogroup 480 Oct 20 21:48 rot-214815.pcap
-rw-rw---- 1 root nogroup 708 Oct 20 21:48 rot-214817.pcap
```

Three files, two seconds apart, and
tcpdump stopped itself at the limit
("Maximum file limit reached" — with
`-W` and no other bound, reaching the
cap *ends* the capture rather than
wrapping forever; read the manual page
before leaving one running for a
weekend). Thirteen of the burst's
sixteen packets made it into files
before the stop — rotation is a budget,
and the footer keeps the accounts.
For a bounded watch, the shape is
`-G 3600 -W 24`: a day of hourly
captures, and then it stops — disk use
decided in advance, not discovered
later.

Check: read the shipped
`examples/specimen.pcap` with a filter
that matches nothing in it — `udp`, say
(the file holds TCP and ICMP only). The
output is empty and instant, and nobody
waited on a network for it. That
emptiness is free: it's the capture-
time emptiness of chapter 9 that costs
you the evidence.
