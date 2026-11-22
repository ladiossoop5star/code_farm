# Episode 14 · Align TShark captures, endpoint logs, and kernel events

[繁體中文](README.md)

In an isolated network namespace, a UDP client sends from port 47007 to port 47006. The server holds its first reply. After 120 ms the client retries with the same sequence number, 42, and the server replies to the second request.

## Rerun the exercise

You need Linux, `ip`, `unshare`, Python 3, TShark, and tracefs with the `net:net_dev_queue` event. The exercise was tested with TShark 4.2.2 and Linux 6.17.0-1014-nvidia. Run from this directory.

```sh
lab_dir=$(mktemp -d)
sudo unshare --mount --net --propagation private python3 roundtrip.py "$lab_dir/result"
```

The script brings up only `lo` in the new network namespace. It limits a temporary tracefs instance to the interface and exercise processes, then removes the instance. TShark captures with `-i lo -f 'udp port 47006'` and queries the saved file with `-r` and `-Y`. To inspect the included capture, run the following commands directly.

```sh
tshark -r sample/packets.pcapng -Y 'udp.port == 47006' -T fields \
  -e frame.number -e frame.time_epoch -e udp.srcport -e udp.dstport -e udp.payload
tshark -r sample/packets.pcapng -Y 'udp.dstport == 47006' -T fields -e frame.number
tshark -r sample/packets.pcapng -Y 'udp.srcport == 47006' -T fields -e frame.number
```

The destination-port filter gives frames 1 and 2, and the source-port filter gives frame 3. The first payload byte is `01` for a request and `02` for a reply. The next 4 bytes hold the sequence number in network byte order. The verifier uses the endpoint log to match the request, retry, and reply, then converts the three kernel events to the capture's time base. The exercise uses a 20 ms matching tolerance. The actual differences are in the alignment table.

[Packet capture](sample/packets.pcapng) · [Alignment table](sample/aligned.tsv) · [Endpoint log](sample/endpoint.tsv) · [Kernel trace](sample/kernel.trace)

[TShark manual](https://www.wireshark.org/docs/man-pages/tshark.html) · [Wireshark capture and offload](https://wiki.wireshark.org/CaptureSetup/Offloading)
