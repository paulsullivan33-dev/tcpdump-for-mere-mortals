# Glossary

- **BPF (Berkeley Packet Filter)** —
  The filter language tcpdump compiles
  and the kernel applies to every
  packet: `tcp port 45080`, `host …`,
  `icmp or udp port 45053`. Chapter 4.
- **Capture** — The act (and the
  result) of recording packets as they
  pass an interface. Passive: a capture
  adds no packets of its own.
- **Checksum offloading** — The network
  hardware filling in checksums after
  tcpdump's copy is taken, which is why
  your own machine's traffic shows
  `cksum ... (incorrect -> ...)`.
  Chapter 3.
- **Dropped by kernel** — The footer's
  count of filter-matched packets the
  kernel had no buffer room to hold.
  Above zero, your capture is a sample.
  Chapter 8.
- **Ephemeral port** — The temporary,
  high-numbered port a client end of a
  conversation picks for itself
  (55954, 33162 in the lab's captures).
- **Filter** — A BPF expression deciding
  which packets tcpdump prints or
  saves. Applied in the kernel at
  capture time, and again by you at
  read time. Chapter 4.
- **Flags** — TCP's one-letter
  intentions on each packet: `S` SYN,
  `.` ACK, `P.` PSH, `F.` FIN, `R` RST.
  Chapter 3's table is the vocabulary.
- **Footer** — The three closing counts
  of every capture: packets captured,
  received by filter, dropped by
  kernel. Evidence, not decoration.
- **Interface** — One doorway in or out
  of the machine (`lo`, `host0`, your
  `eth0`/`wlan0`). A capture watches
  exactly one, or the `any` pseudo-
  device. Listed by `tcpdump -D`.
- **libpcap** — The library under
  tcpdump that talks to the operating
  system and does the capturing; its
  version decides what your machine
  lets it hear. Wireshark's family uses
  the same roots.
- **Loopback (`lo`)** — The interface a
  machine uses to talk to itself at
  127.0.0.1. Complete conversations,
  all yours: this guide's training
  ground. Its capture signature is a
  "received by filter" count exactly
  double the printed packets.
- **pcap** — The standard binary format
  of a saved capture (`-w` writes it,
  `-r` reads it, Wireshark opens it).
  Chapter 7.
- **Promiscuous mode** — The interface
  delivering packets addressed to other
  hardware on the segment, too. Real,
  permission-gated by the rule in
  chapter 1 — and on modern switched
  networks, mostly limited to what the
  switch sends your port anyway.
  Chapter 8.
- **Received by filter** — The kernel's
  count of packets that matched your
  filter and were handed over. See
  loopback, for its doubling.
- **RST (reset)** — TCP's refusal: the
  `[R.]` that answers a SYN to a closed
  port. Its presence means the host
  answered; its absence means silence
  did. Chapter 6.
- **Sequence number (seq)** — A data
  packet's position in its sender's
  stream, printed absolute on a
  direction's first packet and relative
  after. `ack` is the mirror: the next
  byte the sender expects. Chapter 3.
- **Snaplen (snapshot length, `-s`)** —
  How many bytes of each packet tcpdump
  keeps. Shrink it and payloads truncate
  while headers still report true
  lengths. Chapter 8.
- **SNI (Server Name Indication)** —
  The hostname a TLS client asks for,
  sent in the clear in the opening
  handshake — which is why chapter 8's
  sealed capture still shows `lab.test`.
- **Three-way handshake** — SYN,
  SYN-ACK, ACK: the three packets that
  open every TCP conversation, and the
  first thing to look for in any
  capture. Chapter 3.
- **tshark** — Wireshark's command-line
  engine: tcpdump's shape with
  Wireshark's decoders. Named, not
  installed or taught here. Chapter 1.
- **Wireshark** — The graphical reader
  of pcap files: the same packets, on a
  bigger screen. Chapter 7's files are
  its native food.
