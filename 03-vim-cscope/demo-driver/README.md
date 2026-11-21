# netrx-lab

This teaching fixture models a driver-like RX ring,
NAPI-style callback registration, DMA ownership, rollback, and one deliberate
timeout cleanup bug. It contains no private or vendor source code.

```sh
make index
make test       # fails before the exercise fix
```

The intended fix is to release the mapped RX buffer in the timeout path before
clearing or reusing the descriptor. `make reset` restores the deliberate bug.
