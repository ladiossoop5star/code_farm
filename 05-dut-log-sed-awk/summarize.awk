BEGIN { FS = OFS = "\t" }

{
    batch = $1
    if (!(batch in totals))
        batches[++n] = batch
    totals[batch]++
    counts[batch, $2]++
}

END {
    print "batch", "total", "PASS", "NO_DEVICE", "NO_EVENT", "NO_RESULT", "REVIEW"
    for (i = 1; i <= n; i++) {
        batch = batches[i]
        print batch, totals[batch], counts[batch, "PASS"] + 0,
              counts[batch, "NO_DEVICE"] + 0, counts[batch, "NO_EVENT"] + 0,
              counts[batch, "NO_RESULT"] + 0, counts[batch, "REVIEW"] + 0
    }
}
