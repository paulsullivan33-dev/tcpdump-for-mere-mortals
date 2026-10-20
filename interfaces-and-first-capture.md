# Interfaces and First Capture

A capture watches one **interface** —
one doorway in or out of the machine. So
the first skill is choosing the right
doorway, and tcpdump starts by listing
what it can see:

```
$ tcpdump -D
1.host0 [Up, Running, Connected]
2.any (Pseudo-device that captures on all interfaces) [Up, Running]
3.lo [Up, Running, Loopback]
4.bluetooth-monitor (Bluetooth Linux Monitor) [Wireless]
5.nflog (Linux netfilter log (NFLOG) interface) [none]
6.nfqueue (Linux netfilter queue (NFQUEUE) interface) [none]
7.dbus-system (D-Bus system bus) [none]
8.dbus-session (D-Bus session bus) [none]

$ ip -brief address show
lo               UNKNOWN        127.0.0.1/8 ::1/128
host0@if3        UP             198.19.0.2/30 fd8b:4f84:7d32:99::2/64 fe80::70dc:7cff:fe34:2ffd/64
```

The build machine has two real doorways:
`host0`, its one link to the world, and
`lo`, the **loopback** interface —
traffic a machine sends to itself, at
127.0.0.1. (Your machine's external
interface will have a different name —
`eth0`, `enp3s0`, `wlan0`. The loopback
is `lo` everywhere.)

Loopback is this guide's training
ground, for three honest reasons.
Everything on it is yours. It is busy
exactly when you make it busy, so every
packet in a capture is one you caused.
And the conversations are complete:
both ends live on the same machine, so
you see requests *and* replies, which a
capture at a real network edge often
can't promise.

## The first capture

Start the lab, then, in a second
terminal:

```
$ tcpdump -i lo -nn -c 12 tcp port 45080
  (second terminal: curl -s http://127.0.0.1:45080/index.html)
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
21:45:00.913537 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [S], seq 4125593649, win 65495, options [mss 65495,sackOK,TS val 4059721481 ecr 0,nop,wscale 10], length 0
21:45:00.913607 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [S.], seq 846308440, ack 4125593650, win 65483, options [mss 65495,sackOK,TS val 3504221163 ecr 4059721481,nop,wscale 10], length 0
21:45:00.913624 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [.], ack 1, win 64, options [nop,nop,TS val 4059721481 ecr 3504221163], length 0
21:45:00.913690 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [P.], seq 1:89, ack 1, win 64, options [nop,nop,TS val 4059721481 ecr 3504221163], length 88
21:45:00.913696 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [.], ack 89, win 64, options [nop,nop,TS val 3504221163 ecr 4059721481], length 0
21:45:00.914602 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [P.], seq 1:142, ack 89, win 64, options [nop,nop,TS val 3504221164 ecr 4059721481], length 141
21:45:00.914613 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [.], ack 142, win 64, options [nop,nop,TS val 4059721482 ecr 3504221164], length 0
21:45:00.914627 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [P.], seq 142:351, ack 89, win 64, options [nop,nop,TS val 3504221164 ecr 4059721482], length 209
21:45:00.914631 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [.], ack 351, win 64, options [nop,nop,TS val 4059721482 ecr 3504221164], length 0
21:45:00.914657 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [F.], seq 351, ack 89, win 64, options [nop,nop,TS val 3504221164 ecr 4059721482], length 0
21:45:00.914843 IP 127.0.0.1.55954 > 127.0.0.1.45080: Flags [F.], seq 89, ack 352, win 64, options [nop,nop,TS val 4059721482 ecr 3504221164], length 0
21:45:00.914860 IP 127.0.0.1.45080 > 127.0.0.1.55954: Flags [.], ack 90, win 64, options [nop,nop,TS val 3504221164 ecr 4059721482], length 0

12 packets captured
24 packets received by filter
0 packets dropped by kernel
```

(The packet lines above are quoted from
the lab's receipts; your timestamps,
ports, and sequence numbers will differ,
and the response may arrive in one piece
instead of two — segmentation is the
sender's choice, and chapter 3 reads
what's there either way.)

Twelve lines for one web request. That
is the whole conversation — connection
opened, request sent, page returned,
connection closed — and chapter 3 takes
it apart line by line. First, the parts
of the *command* and the *footer*,
because both are already teaching:

**`-i lo`** — the interface. Leave it
off and tcpdump picks one for you
(usually the first non-loopback it
finds), which is how beginners end up
watching the wrong doorway and reporting
that "nothing happened."

**`-nn`** — no name lookups, twice over:
don't resolve addresses to hostnames, and
don't translate port numbers to service
names. Without it, tcpdump pauses to ask
DNS about the very traffic you're trying
to watch — muddying the timings, and
sometimes generating traffic of its own.
And a port *name* is a phone-book lookup,
not evidence, as the nmap guide showed.
Numbers are the truth; `-nn` keeps them.

**`-c 12`** — stop after 12 packets.
Without a count, tcpdump runs until you
interrupt it with Ctrl-C. Either ending
prints the footer.

**`tcp port 45080`** — a *filter*: only
show TCP packets to or from port 45080.
The filter is a language of its own and
gets chapter 4. Here it simply kept the
rest of the machine's loopback chatter
out of the picture.

## The footer is evidence too

```
12 packets captured
24 packets received by filter
0 packets dropped by kernel
```

Three numbers, three different claims:

- **captured** — packets tcpdump printed
  (or saved): 12.
- **received by filter** — packets the
  kernel's filter actually matched and
  handed over: 24. On loopback, every
  packet passes the capture point twice —
  once leaving, once arriving — and this
  counter counts both passes while the
  printed list shows each packet once.
  Elsewhere the two numbers track closely
  instead; a gap this tidy is a loopback
  signature, and chapter 9 lists it so
  you don't chase it as a malfunction.
- **dropped by kernel** — packets the
  filter matched but the kernel had no
  room to hold: 0. This is the number
  that tells you whether your capture is
  the whole story or a sample of it, and
  chapter 8 returns to it.

Check: repeat the capture and fetch the
page again. However the response happens
to segment, you should be able to count
the same conversation shape — three
packets to open, the request, the reply,
acknowledgements, and the closing
exchange of chapter 3. If your capture
is empty instead, chapter 9's first
entries are written for exactly that.
