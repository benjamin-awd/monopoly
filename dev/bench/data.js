window.BENCHMARK_DATA = {
  "lastUpdate": 1788591999441,
  "repoUrl": "https://github.com/benjamin-awd/monopoly",
  "entries": {
    "monopoly CLI performance": [
      {
        "commit": {
          "author": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "committer": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "distinct": true,
          "id": "0975cb7d696de62a40603c11e671e2471ccb2655",
          "message": "ci(perf): single-runner comparison, noise-aware gate, main history\n\n- Run current vs main in one hyperfine invocation on one runner to\n  eliminate cross-machine variance and halve CI cost.\n- Fail the regression gate only when a slowdown is >20% AND exceeds 2x\n  the combined measurement noise; keep the 10s absolute ceiling.\n- Add performance-history workflow: benchmark main on push/weekly and\n  append to gh-pages via github-action-benchmark for trend tracking.",
          "timestamp": "2026-09-04T09:56:06+08:00",
          "tree_id": "e18868e864c4b3067d32f98106c8966d010f8045",
          "url": "https://github.com/benjamin-awd/monopoly/commit/0975cb7d696de62a40603c11e671e2471ccb2655"
        },
        "date": 1788487037833,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8749728383200001,
            "range": "± 0.009270307266371595",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.6368267630800002,
            "range": "± 0.02453702948528775",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "committer": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "distinct": true,
          "id": "13898d39710d94b05c95e6d914554141d6fd4ef0",
          "message": "fix(dbs): raise consolidated transaction_bound to 230\n\nLater pages of a DBS consolidated statement indent the transaction\ntable further right than the first page. In a 2026 statement the\nBalance column drifts across pages (210 -> 223 -> 234), pushing the\nwithdrawal/deposit amount column to col 223 on a later page. With the\nprevious transaction_bound=220 the \"Interest Earned\" deposit on that\npage was discarded as beyond-boundary, dropping one transaction and\nfailing the safety check by exactly 0.08.\n\nRaise the bound to 230 so real amounts (max observed col 223) are kept\nwhile balance-only summary lines (amount col 239+) are still rejected.",
          "timestamp": "2026-09-05T15:01:08+08:00",
          "tree_id": "75ded790870f7ac9ce9c0f44fb3f0407b64f5faf",
          "url": "https://github.com/benjamin-awd/monopoly/commit/13898d39710d94b05c95e6d914554141d6fd4ef0"
        },
        "date": 1788591744793,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.7111791027600001,
            "range": "± 0.011352244809188554",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.2815120903600001,
            "range": "± 0.0075525552784630095",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "committer": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "distinct": true,
          "id": "04774cad2b6d28ac2d83896cf9a4d3eb37c06efd",
          "message": "chore: add .envrc",
          "timestamp": "2026-09-05T15:05:15+08:00",
          "tree_id": "c31d076397d8cb537b75d5b6d7da57ab1aa98b6d",
          "url": "https://github.com/benjamin-awd/monopoly/commit/04774cad2b6d28ac2d83896cf9a4d3eb37c06efd"
        },
        "date": 1788591998854,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8970472593000001,
            "range": "± 0.014213060684535548",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.73427053978,
            "range": "± 0.051659340399575475",
            "unit": "s"
          }
        ]
      }
    ]
  }
}