# 第 14 集｜TShark、端點日誌與核心 trace 對時

[English](README.en.md)

隔離網路命名空間中，UDP 客戶端從 47007 送往伺服端 47006。第 1 次收到請求時，伺服端依練習設定暫緩回覆。客戶端等 120 毫秒後，重送帶相同序號 42 的請求，伺服端於第 2 次收到時回覆。

## 重跑

需 Linux、`ip`、`unshare`、Python 3、TShark 和支援 `net:net_dev_queue` 的 tracefs。實測 TShark 4.2.2、Linux `6.17.0-1014-nvidia`。自此目錄操作。

```sh
lab_dir=$(mktemp -d)
sudo unshare --mount --net --propagation private python3 roundtrip.py "$lab_dir/result"
```

腳本只在新網路命名空間啟用 `lo`。暫存 tracefs instance 將傳送事件縮到該介面及受控程序，結束後刪除。TShark 用 `-i lo -f 'udp port 47006'` 擷取，再用 `-r` 和 `-Y` 查詢落盤結果。若只審原始樣本，可直接讀檔。

```sh
tshark -r sample/packets.pcapng -Y 'udp.port == 47006' -T fields \
  -e frame.number -e frame.time_epoch -e udp.srcport -e udp.dstport -e udp.payload
tshark -r sample/packets.pcapng -Y 'udp.dstport == 47006' -T fields -e frame.number
tshark -r sample/packets.pcapng -Y 'udp.srcport == 47006' -T fields -e frame.number
```

查目的埠得到 frame 1、2，查來源埠得到 frame 3。封包前導位元組 `01` 是請求，`02` 是回覆，後續 4 bytes 用 network byte order 編碼序號。這份驗證會核對端點日誌，相同序號先後形成請求、重試與回覆，另把 3 筆核心事件換算到封包時鐘後核對順序和時間。小於 20 毫秒的配對範圍是驗證門檻，實測差值可見表格。

[原始擷取](sample/packets.pcapng) · [時間對照](sample/aligned.tsv) · [端點日誌](sample/endpoint.tsv) · [核心 trace](sample/kernel.trace)

[TShark 操作手冊](https://www.wireshark.org/docs/man-pages/tshark.html) · [Wireshark 擷取與 offload](https://wiki.wireshark.org/CaptureSetup/Offloading)
