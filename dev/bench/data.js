window.BENCHMARK_DATA = {
  "lastUpdate": 1788605386144,
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
          "id": "565c8488d939a3bdf47224b1cb0236f15828d3c1",
          "message": "fix(standard_chartered): detect OpenPDF-generated statements\n\nSC switched its PDF generator from iText to OpenPDF, changing the\nproducer metadata from \"iText\" to \"OpenPDF 2.0.2\". The single\nidentifier group required producer=\"iText\", so newer statements failed\ndetection and fell back to the generic handler.\n\nAdd a second identifier group for the OpenPDF producer rather than\nloosening the existing one, per the repo convention.",
          "timestamp": "2026-09-05T15:19:39+08:00",
          "tree_id": "df6e9c96fd2afe3af24702825fa200bdfcde47ea",
          "url": "https://github.com/benjamin-awd/monopoly/commit/565c8488d939a3bdf47224b1cb0236f15828d3c1"
        },
        "date": 1788592845182,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.7803547047400002,
            "range": "± 0.01335364438837055",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.4870803372399999,
            "range": "± 0.028883033788090682",
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
          "id": "154055034bd3cd4245ba1e17e7c46d545d48f2ab",
          "message": "feat!: rename polarity to direction with normalized credit/debit values\n\nRename the credit/debit indicator from `polarity` to `direction` throughout\n(field, config flags, regex groups, Columns, SharedPatterns, methods) and\nnormalize the JSON value to \"credit\"/\"debit\" instead of the raw bank markers\n(CR/DR/+/-). Harden generate_hash to hash an explicit field list rather than the\ndataclass repr, so future Transaction fields never churn filenames; add a pinned\ntest (the mocked fixture could not catch this).\n\nBREAKING CHANGE: JSON field `polarity` is now `direction` with values\n\"credit\"/\"debit\"; StatementConfig.transaction_auto_polarity and\nMultilineConfig.multiline_polarity are renamed to *_direction; and the statement\nfilename hash changes once (generate_hash no longer uses the dataclass repr).",
          "timestamp": "2026-09-05T15:59:16+08:00",
          "tree_id": "ec849bf00be133415e3cd7c5c935755f77432b46",
          "url": "https://github.com/benjamin-awd/monopoly/commit/154055034bd3cd4245ba1e17e7c46d545d48f2ab"
        },
        "date": 1788595256996,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.56994998142,
            "range": "± 0.033989323091303404",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 0.98874821672,
            "range": "± 0.019186325869698758",
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
          "id": "ebeef07fb8143f7bb688e31bd30fd3daf08071b7",
          "message": "chore(dev): harden worktree uv provisioning\n\n- pre-commit pytest: uv run --locked (fail on stale lockfile, not silent)\n- .envrc: idiomatic uv+direnv (watch_file + uv sync --locked + PATH_add)\n  instead of source .venv/bin/activate\n- new-worktree.sh: drop uv sync (now .envrc's job), reuse existing\n  branches, and run 'direnv allow' after creation",
          "timestamp": "2026-09-05T16:11:01+08:00",
          "tree_id": "fddbcd37f4bfb90829e06d7c85e2b60cdd1121d6",
          "url": "https://github.com/benjamin-awd/monopoly/commit/ebeef07fb8143f7bb688e31bd30fd3daf08071b7"
        },
        "date": 1788595933026,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.85406824952,
            "range": "± 0.005562195125113322",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.69025868058,
            "range": "± 0.02931495170300121",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "41898282+github-actions[bot]@users.noreply.github.com",
            "name": "github-actions[bot]",
            "username": "github-actions[bot]"
          },
          "committer": {
            "email": "benjamindornel@gmail.com",
            "name": "Benjamin Dornel",
            "username": "benjamin-awd"
          },
          "distinct": true,
          "id": "2e62978e7d5eb447086387be69252c9af810122f",
          "message": "chore(main): release 0.22.0",
          "timestamp": "2026-09-05T16:53:29+08:00",
          "tree_id": "ceb1151130abb0950cdffdeb02fe89c0c0c5ad8e",
          "url": "https://github.com/benjamin-awd/monopoly/commit/2e62978e7d5eb447086387be69252c9af810122f"
        },
        "date": 1788598479524,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9408512544200003,
            "range": "± 0.0212379713003209",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.75356878472,
            "range": "± 0.02398528174575492",
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
          "id": "fef1edd8d2d03d76e9161e10aca99c069999524c",
          "message": "docs: drop removed /commit skill from CLAUDE.md skills table",
          "timestamp": "2026-09-05T17:14:43+08:00",
          "tree_id": "d6f4ac354b93d29f77f2a55a4e9d4cd140062cf5",
          "url": "https://github.com/benjamin-awd/monopoly/commit/fef1edd8d2d03d76e9161e10aca99c069999524c"
        },
        "date": 1788599762699,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6630888649200001,
            "range": "± 0.00343785218369185",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.25738004288,
            "range": "± 0.014104641241081382",
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
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4157b8500c7a2a7d482f79899283295ee7af989b",
          "message": "Merge pull request #309 from benjamin-awd/execute/community-scalable-bank-coverage\n\nRemove git-crypt: test banks with synthetic text fixtures",
          "timestamp": "2026-09-05T17:22:07+08:00",
          "tree_id": "05ed1cb6ceebd53061e4880a674347569cdb29ee",
          "url": "https://github.com/benjamin-awd/monopoly/commit/4157b8500c7a2a7d482f79899283295ee7af989b"
        },
        "date": 1788600219266,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.7952972383000001,
            "range": "± 0.004451326200283481",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.77038023154,
            "range": "± 0.02025475537056594",
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
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3c8677dc7e9676f26898ee0cb8583a50679ac18b",
          "message": "Merge pull request #312 from benjamin-awd/worktree-json-prev-balance\n\nfeat(serialize)!: split balance rows into top-level balances",
          "timestamp": "2026-09-05T18:47:51+08:00",
          "tree_id": "cb1323f498f793a91033da1afbaa61a5d161f608",
          "url": "https://github.com/benjamin-awd/monopoly/commit/3c8677dc7e9676f26898ee0cb8583a50679ac18b"
        },
        "date": 1788605385497,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.87359479388,
            "range": "± 0.004587719428780245",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.090559856920001,
            "range": "± 0.04099835876637752",
            "unit": "s"
          }
        ]
      }
    ]
  }
}