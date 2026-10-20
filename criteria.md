# Writing Criteria

Every guide in this repo is written to the same
standard. If you're adding or editing a guide —
human or AI — hold it to these.

1. **Plain words, real ideas.** Simple language,
   never dumbed-down concepts. Explain jargon on
   first use; collect terms in the glossary.
2. **No hype.** No marketing adjectives, no
   "revolutionary," no promises about what
   something will do for the reader.
3. **Honest about limits.** Say what the thing
   *can't* do. State uncertainty instead of
   smoothing it over. Validation notes include
   what remains unverified.
4. **No invented numbers.** Benchmarks, defaults,
   and specs are either measured or qualified with
   "depends on your setup." If it wasn't tested,
   say so.
5. **Checkable.** Commands are meant to be run,
   with "Check:" blocks showing what success looks
   like. Sources are linked, not asserted.
6. **Respect the reader's setup.** Call out
   Windows/Mac/Linux differences. Don't assume a
   GPU, a budget, or prior experience.
7. **Safety isn't skipped.** Real risks get
   stated plainly, not buried.
8. **Scoped.** Each guide says what it covers and
   points elsewhere for the rest. No guide
   pretends to be the whole subject.
9. **Structure over prose.** Tables, before/after
   examples, symptom → fix. Scannable beats essay.

## Verification notes for this guide

Standard 3 and 4 applied to this guide,
specifically. The build machine ran Ubuntu
24.04 as root, with **tcpdump 4.99.4 and
libpcap 1.10.4 (with TPACKET_V3)** installed
fresh for the build (`apt-get install
tcpdump`; OpenSSL 3.0.13 underlies both).
Every quoted output in the chapters is a
capture from that tcpdump, watching the
shipped lab. Working transcripts are kept
with the build (`tcpdump-lab/transcripts/`,
twenty files).

**The lab.** `examples/lab_server.py` binds
127.0.0.1 only and stands up a specimen web
server on tcp/45080 (`Server:
PacketLab/1.0`, one invented page) and a UDP
echo on udp/45053 that answers every datagram
prefixed with `echo: `. Two specimens are
deliberate absences: nothing binds tcp/45999
or udp/45998. `examples/lab_tls_server.py`
serves the same page over TLS on tcp/45443
with a self-signed certificate made during
the build (`CN=lab.test`, SAN `DNS:lab.test`;
the openssl receipts are chapter 8's).
Drivers are curl, ping, netcat, and getent.
`examples/specimen.pcap` is the capture of
chapter 7, shipped so the reading lessons
work before the reader captures anything.

**Capture hygiene, declared.** Captures were
bounded by `-c` or by a harness timeout
standing in for Ctrl-C; driver commands ran
in a second "terminal" (a backgrounded shell)
and are noted in each transcript as such.
Two cosmetic interventions, neither touching
a byte of capture output: in
`08b-read-pcap.txt` the echoed pipeline's
shell-escaped quotes were un-escaped for
readability, and the chapter quotes trim
driver parentheticals in two places. One
capture was retaken for consistency: the
first TLS capture attempt returned zero
packets because the driver's request had
silently gone to the build shell's egress
proxy (the name `lab.test` is not in its
no-proxy list); the retaken capture drives
curl with `--noproxy "*"`, and chapter 8
says so in place. One fixture defect was
found and fixed during the build: the UDP
echo's first reply path died on this
sandbox's refusal of unconnected UDP sends
(see the invisible-send entry below); the
shipped fixture answers each datagram from
a connected socket, which the same sandbox
permits, and the fixture in `examples/` is
the fixed one.

**Live-captured (every command run for real on the build box):**

- The identity and doorway listings:
  `tcpdump --version`, `tcpdump -D`
  (eight devices), `ip -brief address
  show` (loopback plus the one external
  interface, `host0`).
- The full planted web conversation on
  loopback, repeatedly: three-way
  handshake, request, two-push response,
  acknowledgements, two-FIN close — at
  default verbosity, `-v`, `-vv`, `-A`,
  `-X`, and `-e`, and end to end in the
  shipped specimen.pcap. Packet counts
  for identical fetches varied between
  runs (12 and 13) exactly as chapter 9
  describes; the chapters quote one run
  whole and say so.
- The filter language against one mixed
  burst (ping + curl + UDP echo):
  unfiltered (18 packets), then `icmp`
  (4), `icmp or udp port 45053` (6), and
  the SYN test `tcp[tcpflags] &
  tcp-syn != 0` (2: the SYN and SYN-ACK
  alone). The malformed filter
  (`tpc port 45080`) and its exact error.
  Primitives exercised live: tcp, udp,
  icmp, port, or, the flag byte-test.
- Payload captures: the HTTP request
  line, headers, and page body under
  `-A`; the UDP echo's datagrams in both
  directions; hex under `-X`; the
  link-layer line under `-e` (loopback's
  all-zero hardware addresses, as
  printed).
- A DNS conversation on the external
  interface: AAAA and A queries to the
  machine's resolver and their answers,
  decoded by tcpdump itself. The answers
  are the sandbox resolver's synthetic
  ones (198.18.x), disclosed in chapter
  6; the query names, order, and timing
  are genuine.
- Capture files: `-w` writing
  specimen.pcap (16 packets, 1,908
  bytes, identified by `file` as pcap
  2.4), `-r` reading it back whole,
  read-time filtering (`icmp` → 4
  lines), `-tttt` dates, and the
  awk/sort/uniq talkers pipeline. The
  `-w` runs use `-Z root`: without it
  this sandbox refuses tcpdump's
  savefile ownership change and the run
  fails — that failure is itself
  captured (error verbatim, exit 1,
  24-byte header-only file) and taught
  in chapters 7 and 9.
- Rotation: `-G 2 -W 3` writing three
  time-named files and stopping at the
  cap ("Maximum file limit reached: 3",
  13 of 16 packets filed).
- Snaplen: `-s 100` truncating the
  payload view while headers report
  true lengths — the page text present
  twice in the full capture is absent
  (grep count 0) in the truncated one.
- Refusals, both shapes: a TCP SYN to
  the closed specimen answered by
  `[R.]` (curl's exit 7 recorded), and
  a UDP datagram to the closed specimen
  answered by an ICMP port-unreachable.
- The errors chapter, verbatim:
  capture attempted as user `nobody`
  (permission refused), `-i nosuch0`
  (no such device), the filter syntax
  error above.
- The invisible send: a probe whose
  unconnected UDP `sendto` this sandbox
  refuses with EPERM was run under a
  matching capture, which reported
  **0 packets captured / 0 received /
  0 dropped** — the absence is the
  evidence, quoted as captured.
- TLS: the self-signed certificate's
  creation and inspection; the full
  HTTPS fetch captured under `-A` — the
  SNI name `lab.test` and ALPN list
  legible in the ClientHello dump, and
  `grep -c "GET /"` on the capture
  returning 0. TLS 1.3 was negotiated,
  as the driver's own verbose output
  confirmed.

**Documented-only (not run), and why:**

- *Wireshark and tshark.* Neither is
  installed on the build machine
  (`tshark` verified absent). They are
  named and placed — Wireshark as the
  GUI reader of the pcap files chapter 7
  makes, tshark in one honest paragraph
  in chapter 1 — and nothing about
  their behaviour is demonstrated.
- *TLS decryption via a key log*
  (SSLKEYLOGFILE plus Wireshark):
  named in chapter 8 as a cooperative-
  endpoint arrangement that exists; not
  installed, not run, not taught.
- *Third-party / promiscuous capture of
  other hosts' traffic.* The build
  machine's only external link is
  point-to-point, so every capture in
  this guide contains this machine's
  own traffic and nothing else's to
  show. Chapter 8 describes what
  promiscuous mode can and cannot reach
  on modern switched networks as
  description, and no capture pretends
  otherwise. Wi-Fi monitor mode is
  likewise described only: no usable
  wireless capture device exists here.
- *Filter primitives taught from the
  table but not separately captured:*
  `host`, `net`, `portrange`, `src`/
  `dst`, `not`. Their grammar is the
  `pcap-filter` manual page's; the
  exercised primitives are listed in
  the live ledger above.
- *Fragmentation, ECH, and saturated-
  link drop behaviour:* named where a
  reader will meet them (fragment
  fields in chapter 3, ECH closing SNI
  in chapter 8, drops argued from the
  footer counters) — described, not
  staged. Every footer in the lab
  honestly reports zero drops; the
  guide does not manufacture a busier
  network than it has.

Specimen discipline, for the record:
every capture targets the build machine's
own interfaces; every fixture binds
127.0.0.1; the only external traffic
captured is the machine's own DNS, driven
by the author. No output was completed,
corrected, or invented: where a capture
surprised the draft — the footer's
loopback doubling, the 24-byte savefile,
the proxy that swallowed the first TLS
run — the chapters were written to the
capture.
