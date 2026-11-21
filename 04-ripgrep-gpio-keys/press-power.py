"""Send the simulated power-button event to a local QEMU guest over QMP."""
import argparse
import json
import socket


def request(stream, command):
    payload = json.dumps({"execute": command}).encode("ascii") + b"\r\n"
    stream.write(payload)
    stream.flush()
    for line in stream:
        message = json.loads(line)
        if "error" in message:
            raise RuntimeError(f"{command}: {message['error']['desc']}")
        if "return" in message:
            return message["return"]
    raise RuntimeError(f"QMP closed before answering {command}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qmp_socket")
    args = parser.parse_args()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(3)
        connection.connect(args.qmp_socket)
        with connection.makefile("rwb") as stream:
            if "QMP" not in json.loads(stream.readline()):
                raise RuntimeError("Missing QMP greeting")
            request(stream, "qmp_capabilities")
            request(stream, "system_powerdown")


if __name__ == "__main__":
    main()
