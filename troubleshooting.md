# Troubleshooting

Symptom first, cause second, fix third.
Every entry here was produced on the
build machine while making this guide;
the errors are quoted, not remembered.

## The capture is empty, and the program is failing anyway

```
$ tcpdump -i lo -nn "udp port 45053"
  (second terminal: a probe sends one datagram to the fixture from an
   unconnected socket; Python raises PermissionError - the sandbox
   refuses the send outright)
0 packets captured
0 packets received by filter
0 packets dropped by kernel
```

The probe failed *before* the network:
its send was refused by the operating
system, so no packet ever existed for
tcpdump to see. This is the extreme of
chapter 6's "is it even leaving the
machine?" — and the capture is not
broken; it is reporting, precisely,
that nothing crossed. **Fix:** when a
capture is empty, clear tcpdump first
(it hears fine — chapter 5's captures of
the same port prove it), then ask
whether the sender actually sent: run
the client where its own error is
visible. An empty capture of a
*working* conversation accuses the
filter or the interface (chapter 2's
wrong-doorway trap); an empty capture
of a *failing* one may be the diagnosis
itself.

## "You don't have permission to perform this capture"

```
$ su -s /bin/sh nobody -c "tcpdump -i lo -nn -c 1"
tcpdump: lo: You don't have permission to perform this capture on that device
(socket: Operation not permitted)
exit status: 1
```

Capture is privileged (chapter 1). The
build machine's captures ran as root.
**Fix:** run with `sudo`, or grant the
`CAP_NET_RAW` capability deliberately —
and notice the error names the device
and the operation plainly. If it stops
happening only on *one* interface, that
interface's driver or the sandbox you
are in has its own rule; the message is
still your first fact.

## "No such device exists"

```
$ tcpdump -i nosuch0 -nn -c 1
tcpdump: nosuch0: No such device exists
(SIOCGIFHWADDR: No such device)
```

**Fix:** `tcpdump -D` lists what this
machine actually has (chapter 2). The
usual cause is a name from another
machine's habit — `eth0` carried in
your fingers to a box that calls it
`host0` or `enp3s0`.

## "can't parse filter expression"

```
$ tcpdump -i lo -nn "tpc port 45080"
tcpdump: can't parse filter expression: syntax error
```

A filter typo, caught at compile time —
before a single packet is missed.
**Fix:** check the primitives against
chapter 4's table (`tcp`, not `tpc`),
balance the parentheses, and quote the
expression so the shell isn't eating
the `&`, `(`, or `)` characters before
tcpdump ever sees them. An unquoted
`tcp[tcpflags]...` is the classic case:
the shell reads the brackets first.

## "Couldn't change ownership of savefile"

```
$ tcpdump -i lo -nn -c 2 -w ownfail.pcap tcp port 45080   # as root, WITHOUT -Z root
tcpdump: Couldn't change ownership of savefile
exit: 1

$ ls -l ownfail.pcap
-rw-rw---- 1 root nogroup 24 Oct 20 21:53 ownfail.pcap
```

Twenty-four bytes is the pcap global
header and nothing else: as root,
tcpdump drops privileges to the
`tcpdump` user and tries to make the
savefile that user's; this machine's
environment refuses the ownership
change, so the run fails before packet
one. **Fix here:** `-Z root` (drop to
root instead) — the spelling every
`-w` capture in this guide uses, and
chapter 7 tells the whole story. On an
ordinary machine this error is rare;
when it appears, `-Z <your user>` or
writing the file somewhere the drop
user can own are the same fix wearing
different hats. Do not be tempted to
read the 24-byte file: there is nothing
in it to read.

## The footer says "received" is exactly double "captured"

It is loopback being loopback: every
packet passes the capture point twice —
once on its way out, once on its way
in — the kernel counts both passes, and
the printed list shows each packet
once (chapter 2). On a physical
interface the numbers track each other
instead. **Fix:** none; file it under
"this interface's signature," and check
the same doubling before you report a
packet storm that isn't one.

## Every checksum is "incorrect"

It is chapter 3's offload artefact: on
traffic your own machine is sending,
the checksum is filled in by hardware
*after* tcpdump's copy is taken, and
tcpdump honestly reports the empty
value as `cksum 0xfe30 (incorrect ->
0xd9ab)` — complete with the value it
computes the checksum *should* be.
**Fix:** none required. If you need
finished checksums, capture where the
packets have already crossed a wire —
another machine's interface, watching —
or turn off offloading on an interface
you own. Never file a bug against a
program on the strength of loopback
checksums.

## The same conversation has a different packet count this time

Run the chapter-2 fetch twice and the
response may arrive as one push instead
of two, or three: segmentation is the
sender's per-moment choice, governed by
timing, buffering, and load, not by any
contract with your capture. The
*bytes* are the invariant — sequence
ranges join end to end either way
(chapter 3's arithmetic still closes).
**Fix:** argue from bytes and flags,
never from an expected packet count.

## The names are wrong, or the capture made traffic of its own

You forgot `-nn` (chapter 2): tcpdump
resolves addresses through DNS and port
numbers through the services file,
adding lookups — sometimes visible as
extra DNS packets the capture itself
caused — and replacing true numbers
with a phone book's opinions. **Fix:**
`-n` for addresses, `-nn` for ports
too, always, unless the names are
specifically what you're studying.

## One line to remember

tcpdump's errors are unusually honest
— they name the device, the filter, the
file, the permission — and its silences
are honest too, once you learn their
three dialects: nothing matched, nothing
was sent, or nothing survived the
buffer. Chapter 8's footer questions
(drops? snaplen?) plus this chapter's
symptoms cover the silences a mortal
will actually meet.
