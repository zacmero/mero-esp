# Board probing plan

1. Preserve the original flash with two matching full reads — complete.
2. Probe existing firmware and read security configuration — complete.
3. Run Wi-Fi and Bluetooth diagnostics, using temporary firmware if needed — complete.
4. Restore original firmware and verify restoration — complete; full readback matches.
5. Evidence, scripts and user commands — complete; publication recorded in Git.

Do not overwrite flash until the two backups match. Keep raw dumps and nearby device identifiers out of Git.
