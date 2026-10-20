# tcpdump for Mere Mortals

**Something on your network is behaving
oddly, and you're done guessing.
tcpdump is how you stop guessing: it
watches the actual packets — who sent
them, to which port, with what flags,
carrying how much — and prints them,
one line per packet, while you watch
the program in question do its thing.**
Nmap knocks and netcat converses; this
guide's tool does neither. It listens,
and listening settles the arguments the
other tools can't: whether the request
ever left, whether anything answered,
and whether the answer was a reply, a
refusal, or silence.

It starts on the loopback interface,
with a packet lab planted there (a
specimen web server and a UDP echo) so
every packet in the early chapters is
one you caused — then takes apart a
real web conversation line by line,
teaches the filter language that picks
one conversation out of thousands, and
climbs the verbosity ladder from
one-line summaries to readable payloads
to hex. The second half is the working
tool: everyday recipes (what DNS was
asked, who keeps connecting, who talks
most, refused-versus-silent), capture
files that outlive the terminal — and
one deliberately honest chapter on the
limits: TLS seals the content and
shows you the envelope, a capture can
drop and truncate, and promiscuous mode
is not the superpower it was in 1997.

One rule runs through it, stated in the
first chapter and never relaxed: only
capture on machines and networks you
own or administer. A capture hears
everything its interface hears;
everything in the lab is your own
traffic, on purpose.

Every command output in the guide is a
real capture made on the build machine
— a planted conversation, captured as
it crossed the loopback interface and
the machine's one external link, with
tcpdump 4.99.4 and libpcap 1.10.4.
Nothing is mocked up: the handshake,
the DNS answers, the refusal, the
sealed TLS conversation the payload
flags can't read, the errors in the
troubleshooting chapter — all of them
quoted from receipts. The few things a
sandboxed build machine cannot honestly
show (a true third-party promiscuous
capture on a shared segment, Wi-Fi
monitor mode) are labelled
documented-only where they come up, and
`criteria.md` keeps the ledger of what
was captured live versus described.

## The chapters

- [What tcpdump Is](what-tcpdump-is.md)
  — capture as passive listening; the
  permission rule; why it needs
  privilege; Wireshark and tshark named
  honestly; the lab.
- [Interfaces and First Capture](interfaces-and-first-capture.md)
  — `-D` and the doorways; why loopback
  is the training ground; a full
  twelve-packet conversation; `-nn`,
  `-c`, Ctrl-C; the footer's three
  numbers and loopback's double count.
- [Reading a Packet](reading-a-packet.md)
  — one line dissected: time, endpoints,
  the flags table, seq and ack, window,
  options, length; the four acts of a
  conversation; what `-v` adds and why
  its checksums say "incorrect."
- [Filters](filters.md) — the BPF
  language: host, net, port, protocol,
  src and dst, and/or/not; one burst
  read three ways; the SYN-only
  byte-test, explained whole.
- [Payload and Verbosity](payload-and-verbosity.md)
  — `-v` and `-vv`, `-A` reading plain
  HTTP and the UDP echo whole, `-X` hex,
  `-e` link layer; reading payloads
  honestly.
- [Everyday Recipes](everyday-recipes.md)
  — watch the DNS questions; refused,
  unreachable, or silent — the three
  shapes of no; a census of connection
  attempts; the talkers pipeline; is it
  even leaving the machine.
- [Capture Files](capture-files.md) —
  `-w` and `-r`; pcap as the artifact
  that outlives the terminal; filtering
  twice (at capture, at leisure);
  rotation with `-G` and `-W`; the
  `-Z root` note this build machine
  required.
- [TLS and the Limits of Capture](tls-and-the-limits.md)
  — the same page under TLS: SNI in the
  clear, the GET nowhere (grep proves
  it); snaplen truncation; drops and
  the sample humility; promiscuous mode
  as it actually is on modern networks.
- [Troubleshooting](troubleshooting.md)
  — the empty capture that is itself
  the diagnosis; permission, device,
  and filter errors as printed; the
  savefile-ownership failure; doubled
  counts and offloaded checksums that
  are not malfunctions.
- [Glossary](glossary.md)

## What it doesn't cover

- **Wireshark and tshark, as tools.**
  Named, placed, and recommended for
  the files chapter 7 makes — but
  neither is installed on the build
  machine, and this guide stays on the
  command line it can demonstrate.
- **Decrypting captures.** Opening TLS
  with a cooperative endpoint's key log
  exists and is named in chapter 8; it
  is not a passive capture power and is
  not taught here.
- **Deep BPF programming.** One
  byte-test (the SYN filter), explained
  whole. The `pcap-filter` manual page
  is the honest next step.
- **Other people's traffic.** No
  chapter needs it; the rule in
  chapter 1 stands. Monitor mode,
  span ports, and shared-segment
  capture are described only to bound
  what they can and can't do.
- **Performance engineering.** Fighting
  drops on a saturated link gets the
  mortal's moves (tighter filters,
  bigger buffers) — not a kernel-tuning
  course.

## How to use this guide

Chapters 1–5 are the foundation: what a
capture is, how to take one, how to
read one, how to aim one, how much of
it to open. Read them in order the
first time, with the lab fixture
running and a second terminal to drive
traffic — every chapter's capture is
one you can reproduce against the
fixtures in `examples/` in under a
minute. Chapters 6 and 7 are the
recipes and the filing system; 8 is
the honesty chapter; 9 is for the day
a capture comes back empty or angry.
`examples/commands.txt` is the whole
guide as a pocket card, and
`examples/specimen.pcap` is a real
capture to practise reading before you
take one of your own.
