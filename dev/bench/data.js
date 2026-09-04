window.BENCHMARK_DATA = {
  "lastUpdate": 1788487038354,
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
      }
    ]
  }
}