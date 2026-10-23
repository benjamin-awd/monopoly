window.BENCHMARK_DATA = {
  "lastUpdate": 1792752542478,
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
          "id": "91a33e42ef0463bf7013693ed1bc29b31703186e",
          "message": "Merge pull request #313 from benjamin-awd/refactor/kind-enum-and-parser-source\n\nrefactor: model transaction kind as an enum; bundle parser fixture inputs",
          "timestamp": "2026-09-05T20:40:19+08:00",
          "tree_id": "8b92039ff4143f692a32e3c3fc33e211350aa3cc",
          "url": "https://github.com/benjamin-awd/monopoly/commit/91a33e42ef0463bf7013693ed1bc29b31703186e"
        },
        "date": 1788612134406,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6724974750200001,
            "range": "± 0.009242320957874174",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.0740030906999998,
            "range": "± 0.038903696347718966",
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
          "id": "dfff2fa2a835dcb49ff0f39016a5c04304f68fcc",
          "message": "Merge pull request #314 from benjamin-awd/execute/direction-enum-column-layout\n\nfix(statements): centralise direction markers and column geometry",
          "timestamp": "2026-09-05T21:26:37+08:00",
          "tree_id": "82496cedee393791737d4144d490e8a45abf3702",
          "url": "https://github.com/benjamin-awd/monopoly/commit/dfff2fa2a835dcb49ff0f39016a5c04304f68fcc"
        },
        "date": 1788614901368,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.86672545782,
            "range": "± 0.008774339770793959",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.0638492608000005,
            "range": "± 0.037929366730433324",
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
          "id": "748a90c3f8fe0cb439e37b6ca1cddae7a85acc58",
          "message": "Merge pull request #315 from benjamin-awd/execute/normalise-pattern-union\n\nrefactor(config): compile statement patterns once, at construction",
          "timestamp": "2026-09-05T22:09:19+08:00",
          "tree_id": "f1087712438fd71fa55e8f527e3cf3297ac58269",
          "url": "https://github.com/benjamin-awd/monopoly/commit/748a90c3f8fe0cb439e37b6ca1cddae7a85acc58"
        },
        "date": 1788617465613,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.48696084400000006,
            "range": "± 0.01863860648920868",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.2307352864200003,
            "range": "± 0.09377934148791023",
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
          "id": "ab277275aebb3e458e8f8377cd5fb9aec029819f",
          "message": "Merge pull request #317 from benjamin-awd/execute/pipeline-and-dispatch\n\nrefactor: extract DateTransformer, split extraction, dedupe dispatch",
          "timestamp": "2026-09-05T22:35:42+08:00",
          "tree_id": "3380b6525d0ca35424da5c24e5de81ce801fe37c",
          "url": "https://github.com/benjamin-awd/monopoly/commit/ab277275aebb3e458e8f8377cd5fb9aec029819f"
        },
        "date": 1788619056112,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8843550179600002,
            "range": "± 0.008956405359731115",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.13266383564,
            "range": "± 0.015388779788093554",
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
          "id": "bc5b26a5287056d7009e44d801a41600dbca1b3b",
          "message": "Merge pull request #319 from benjamin-awd/ci/speed-up-workflows\n\nci: speed up workflows (drop ocrmypdf, cache uv, cancel stale runs)",
          "timestamp": "2026-09-05T22:42:38+08:00",
          "tree_id": "a1e9e4dfa37a48a6c1319738edd93f6517fb634c",
          "url": "https://github.com/benjamin-awd/monopoly/commit/bc5b26a5287056d7009e44d801a41600dbca1b3b"
        },
        "date": 1788619467271,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9441715329600001,
            "range": "± 0.018525918268891724",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.303298497959999,
            "range": "± 0.035103385543316414",
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
          "id": "e46781cbb186a9cae9a88485f09b89ab76544536",
          "message": "Merge pull request #318 from benjamin-awd/execute/safety-check-abc\n\nrefactor(statements): share safety reconciliation, make BaseStatement abstract",
          "timestamp": "2026-09-05T22:47:17+08:00",
          "tree_id": "487b4a9355bca07f19854a867b652047fb7e922f",
          "url": "https://github.com/benjamin-awd/monopoly/commit/e46781cbb186a9cae9a88485f09b89ab76544536"
        },
        "date": 1788619743165,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9134575006600002,
            "range": "± 0.024423768554233918",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.13992487586,
            "range": "± 0.0739392913226659",
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
          "id": "623d0641a70202918b610d6bc49362900884bac7",
          "message": "Merge pull request #311 from benjamin-awd/release-please--branches--main--components--monopoly-core\n\nchore(main): release 0.23.0",
          "timestamp": "2026-09-05T22:58:54+08:00",
          "tree_id": "a9002168fbdd44a2c98243603a351c255c94d41e",
          "url": "https://github.com/benjamin-awd/monopoly/commit/623d0641a70202918b610d6bc49362900884bac7"
        },
        "date": 1788620435994,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9346207185600001,
            "range": "± 0.010816506352635064",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.257296923299999,
            "range": "± 0.09162504666052758",
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
          "id": "6ace36fdbd81579500708f6c6098ccf2e844407c",
          "message": "Merge pull request #320 from benjamin-awd/feat/python-314-support\n\nfeat: add Python 3.14 support",
          "timestamp": "2026-09-05T23:08:12+08:00",
          "tree_id": "e9bec003ad167e76980145d1ce25c832f024dc8a",
          "url": "https://github.com/benjamin-awd/monopoly/commit/6ace36fdbd81579500708f6c6098ccf2e844407c"
        },
        "date": 1788620995453,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9286915087799998,
            "range": "± 0.017352030910176796",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.379614586820001,
            "range": "± 0.02395682994493495",
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
          "id": "1d315bd8eecca1791fa08029a9d6888444ed7981",
          "message": "Merge pull request #322 from benjamin-awd/execute/appendix-cleanups\n\nfix(statements): initialise carried date, drop dead and unreachable code",
          "timestamp": "2026-09-05T23:17:27+08:00",
          "tree_id": "37f0386efa2a06688b5dc2af9a15a8fe92dd8e23",
          "url": "https://github.com/benjamin-awd/monopoly/commit/1d315bd8eecca1791fa08029a9d6888444ed7981"
        },
        "date": 1788621556332,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.5846481374800001,
            "range": "± 0.012927163605783552",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.54090591098,
            "range": "± 0.1526317917398248",
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
          "id": "c231a7685d0b3b8dded52ac16f8bd87b3b8d0c3f",
          "message": "Merge pull request #324 from benjamin-awd/feat/gemini-transaction-kind\n\nfeat(gemini): set TransactionKind on the vision path",
          "timestamp": "2026-09-05T23:29:37+08:00",
          "tree_id": "e046eed8d3d3be1ed0284bb40d1d3a81c83c6260",
          "url": "https://github.com/benjamin-awd/monopoly/commit/c231a7685d0b3b8dded52ac16f8bd87b3b8d0c3f"
        },
        "date": 1788622272089,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8564774694199999,
            "range": "± 0.0071227063810784755",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.9796108027800003,
            "range": "± 0.04952118975840343",
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
          "id": "ade1b799ea010a583ad2b96fa0a76234eaef7265",
          "message": "Merge pull request #325 from benjamin-awd/worktree-json-follow-up\n\nfeat(json): populate account last-4 and period_start (#308)",
          "timestamp": "2026-09-05T23:39:43+08:00",
          "tree_id": "360a1e3da95c4ed3d57835509144d09f1da644ac",
          "url": "https://github.com/benjamin-awd/monopoly/commit/ade1b799ea010a583ad2b96fa0a76234eaef7265"
        },
        "date": 1788622882927,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6394973135,
            "range": "± 0.012798616229890177",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.8790344158800005,
            "range": "± 0.019591427504665436",
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
          "id": "f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89",
          "message": "Merge pull request #321 from benjamin-awd/release-please--branches--main--components--monopoly-core\n\nchore(main): release 0.23.1",
          "timestamp": "2026-09-05T23:40:23+08:00",
          "tree_id": "b8de8f6f199e8397770ce9aecbcf0bcfe89b2faf",
          "url": "https://github.com/benjamin-awd/monopoly/commit/f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89"
        },
        "date": 1788622991025,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8854635116800003,
            "range": "± 0.006336192896192328",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.15373913018,
            "range": "± 0.03691496234736435",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89",
          "message": "Merge pull request #321 from benjamin-awd/release-please--branches--main--components--monopoly-core\n\nchore(main): release 0.23.1",
          "timestamp": "2026-09-05T15:40:23Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89"
        },
        "date": 1788781202035,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8903222626400001,
            "range": "± 0.0070781007894505235",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.1480381692199995,
            "range": "± 0.04432848004944261",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89",
          "message": "Merge pull request #321 from benjamin-awd/release-please--branches--main--components--monopoly-core\n\nchore(main): release 0.23.1",
          "timestamp": "2026-09-05T15:40:23Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/f2a1ea9a052b455a35e12c2a35b5ba4e264bfe89"
        },
        "date": 1789386836750,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8523738199800001,
            "range": "± 0.0273385248140858",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.63416065412,
            "range": "± 0.06806481451988954",
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
          "id": "ef028c5ee45c93d129b7df5ac257b2d605766236",
          "message": "Merge pull request #326 from benjamin-awd/consolidate-bank-fixtures\n\ntest(fixtures): consolidate text fixtures into tests/integration/banks",
          "timestamp": "2026-09-15T13:34:45+08:00",
          "tree_id": "8a72b1effa0d4a9f4f5f9a86c8b79162642fe70c",
          "url": "https://github.com/benjamin-awd/monopoly/commit/ef028c5ee45c93d129b7df5ac257b2d605766236"
        },
        "date": 1789450585512,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8926580228000001,
            "range": "± 0.006998377128520293",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.20219519252,
            "range": "± 0.02593291772202542",
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
          "id": "6a1055035c1c6ec7c0ed54727d114277ebe16bcc",
          "message": "Merge pull request #327 from benjamin-awd/dependabot/uv/anyio-4.14.2\n\nbuild(deps): bump anyio from 4.14.0 to 4.14.2",
          "timestamp": "2026-09-19T15:03:43+08:00",
          "tree_id": "83874603180262e53264986ffbaf2655c8015c54",
          "url": "https://github.com/benjamin-awd/monopoly/commit/6a1055035c1c6ec7c0ed54727d114277ebe16bcc"
        },
        "date": 1789801530286,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8879059851800001,
            "range": "± 0.006336759764709467",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.150601207459999,
            "range": "± 0.06261799648000939",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "6a1055035c1c6ec7c0ed54727d114277ebe16bcc",
          "message": "Merge pull request #327 from benjamin-awd/dependabot/uv/anyio-4.14.2\n\nbuild(deps): bump anyio from 4.14.0 to 4.14.2",
          "timestamp": "2026-09-19T07:03:43Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/6a1055035c1c6ec7c0ed54727d114277ebe16bcc"
        },
        "date": 1789992300055,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.98181475984,
            "range": "± 0.008990527949983354",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.48928326568,
            "range": "± 0.04421252058195372",
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
          "id": "1aafbd91290f41f60d85559fe51bca268e099957",
          "message": "Merge pull request #328 from benjamin-awd/simplify-architecture\n\nrefactor: simplify statement dispatch and transaction construction",
          "timestamp": "2026-09-24T18:16:58+08:00",
          "tree_id": "ca2339862a67a52892648810f999219ea5f5f573",
          "url": "https://github.com/benjamin-awd/monopoly/commit/1aafbd91290f41f60d85559fe51bca268e099957"
        },
        "date": 1790245120013,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.66770265884,
            "range": "± 0.0067187975746202935",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.04316222086,
            "range": "± 0.08499355261051637",
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
          "id": "121a983c499114615fa2b381f3abbd517c6ac11e",
          "message": "Merge pull request #329 from benjamin-awd/timeless-comments\n\ndocs: describe current behaviour in two comments",
          "timestamp": "2026-09-24T18:59:10+08:00",
          "tree_id": "525aeebc184df8c77d218f677f13c5c164ee0215",
          "url": "https://github.com/benjamin-awd/monopoly/commit/121a983c499114615fa2b381f3abbd517c6ac11e"
        },
        "date": 1790247671147,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.5390965136400001,
            "range": "± 0.008671384353287263",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.37604019328,
            "range": "± 0.05638539523379741",
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
          "id": "277eef788af5947242d9dca516caa7b91ac6543c",
          "message": "chore(release): list refactor commits in the changelog\n\nrelease-please hides refactor commits by default, so refactor-only work\n(such as #328) shipped without a changelog entry. Configure\nchangelog-sections to show them under \"Code Refactoring\". The other\nsections keep their current visibility.",
          "timestamp": "2026-09-24T19:06:28+08:00",
          "tree_id": "c38a02a0ead50fc50410bf6c23746a45efc2f435",
          "url": "https://github.com/benjamin-awd/monopoly/commit/277eef788af5947242d9dca516caa7b91ac6543c"
        },
        "date": 1790248102420,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.92786404014,
            "range": "± 0.017090271247859855",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.19432652678,
            "range": "± 0.05359514588814953",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "committer": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "id": "277eef788af5947242d9dca516caa7b91ac6543c",
          "message": "chore(release): list refactor commits in the changelog\n\nrelease-please hides refactor commits by default, so refactor-only work\n(such as #328) shipped without a changelog entry. Configure\nchangelog-sections to show them under \"Code Refactoring\". The other\nsections keep their current visibility.",
          "timestamp": "2026-09-24T11:05:24Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/277eef788af5947242d9dca516caa7b91ac6543c"
        },
        "date": 1790600407150,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9005181271200001,
            "range": "± 0.00794611431110255",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.2301690637,
            "range": "± 0.07405860156158652",
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
          "id": "03fa9149cecfe746a6aac25f7cf437020f358828",
          "message": "fix(scotiabank): accept unpadded days in personal debit dates",
          "timestamp": "2026-10-04T11:43:32+08:00",
          "tree_id": "48cfc2ff3cfcf08d90d867d3b588d98cc4e8ba29",
          "url": "https://github.com/benjamin-awd/monopoly/commit/03fa9149cecfe746a6aac25f7cf437020f358828"
        },
        "date": 1791085522607,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.88553962396,
            "range": "± 0.007833954426235915",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.08538114592,
            "range": "± 0.03859549837331889",
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
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c54229f100f8fa8343f4cd3940b51db6857bfbb6",
          "message": "chore(main): release 0.23.2 (#335)",
          "timestamp": "2026-10-04T12:02:04+08:00",
          "tree_id": "8a87cc0e9a36cc448b2fe96a744c0d337cb81b1a",
          "url": "https://github.com/benjamin-awd/monopoly/commit/c54229f100f8fa8343f4cd3940b51db6857bfbb6"
        },
        "date": 1791086635009,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.78358337178,
            "range": "± 0.010121569933561402",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.4759617675200003,
            "range": "± 0.021002944546301465",
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
          "id": "d2d7fbddd65132762b4d72b1e6ba7d5138e3e1ae",
          "message": "chore: remove unused folder",
          "timestamp": "2026-10-04T12:58:04+08:00",
          "tree_id": "76ccd512785a5c38eda2f2eca139c1810f3cf5fb",
          "url": "https://github.com/benjamin-awd/monopoly/commit/d2d7fbddd65132762b4d72b1e6ba7d5138e3e1ae"
        },
        "date": 1791090002731,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8882828623,
            "range": "± 0.005038669813185177",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.07831519044,
            "range": "± 0.06566180350551852",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "committer": {
            "name": "Benjamin Dornel",
            "username": "benjamin-awd",
            "email": "benjamindornel@gmail.com"
          },
          "id": "d2d7fbddd65132762b4d72b1e6ba7d5138e3e1ae",
          "message": "chore: remove unused folder",
          "timestamp": "2026-10-04T04:58:04Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/d2d7fbddd65132762b4d72b1e6ba7d5138e3e1ae"
        },
        "date": 1791207710068,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.91361099134,
            "range": "± 0.008511122912166809",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.17422713982,
            "range": "± 0.050516417856744184",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "49699333+dependabot[bot]@users.noreply.github.com",
            "name": "dependabot[bot]",
            "username": "dependabot[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e4cd3791364da3203d1680849a9de6a8cad472ee",
          "message": "build(deps): bump urllib3 from 2.7.0 to 2.8.0 (#336)\n\nBumps [urllib3](https://github.com/urllib3/urllib3) from 2.7.0 to 2.8.0.\n- [Release notes](https://github.com/urllib3/urllib3/releases)\n- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)\n- [Commits](https://github.com/urllib3/urllib3/compare/2.7.0...2.8.0)\n\n---\nupdated-dependencies:\n- dependency-name: urllib3\n  dependency-version: 2.8.0\n  dependency-type: indirect\n...\n\nSigned-off-by: dependabot[bot] <support@github.com>\nCo-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
          "timestamp": "2026-10-05T22:59:39+08:00",
          "tree_id": "c1794a1c6abd30e6eb6298bb933a02255e8d637d",
          "url": "https://github.com/benjamin-awd/monopoly/commit/e4cd3791364da3203d1680849a9de6a8cad472ee"
        },
        "date": 1791212552209,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6676780911,
            "range": "± 0.005964645770727854",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.00080148424,
            "range": "± 0.021907836495579227",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "dependabot[bot]",
            "username": "dependabot[bot]",
            "email": "49699333+dependabot[bot]@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "e4cd3791364da3203d1680849a9de6a8cad472ee",
          "message": "build(deps): bump urllib3 from 2.7.0 to 2.8.0 (#336)\n\nBumps [urllib3](https://github.com/urllib3/urllib3) from 2.7.0 to 2.8.0.\n- [Release notes](https://github.com/urllib3/urllib3/releases)\n- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)\n- [Commits](https://github.com/urllib3/urllib3/compare/2.7.0...2.8.0)\n\n---\nupdated-dependencies:\n- dependency-name: urllib3\n  dependency-version: 2.8.0\n  dependency-type: indirect\n...\n\nSigned-off-by: dependabot[bot] <support@github.com>\nCo-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
          "timestamp": "2026-10-05T14:59:39Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/e4cd3791364da3203d1680849a9de6a8cad472ee"
        },
        "date": 1791815465527,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.9591900879,
            "range": "± 0.018174604350368613",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.35041699362,
            "range": "± 0.0623571903395672",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "dependabot[bot]",
            "username": "dependabot[bot]",
            "email": "49699333+dependabot[bot]@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "e4cd3791364da3203d1680849a9de6a8cad472ee",
          "message": "build(deps): bump urllib3 from 2.7.0 to 2.8.0 (#336)\n\nBumps [urllib3](https://github.com/urllib3/urllib3) from 2.7.0 to 2.8.0.\n- [Release notes](https://github.com/urllib3/urllib3/releases)\n- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)\n- [Commits](https://github.com/urllib3/urllib3/compare/2.7.0...2.8.0)\n\n---\nupdated-dependencies:\n- dependency-name: urllib3\n  dependency-version: 2.8.0\n  dependency-type: indirect\n...\n\nSigned-off-by: dependabot[bot] <support@github.com>\nCo-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
          "timestamp": "2026-10-05T14:59:39Z",
          "url": "https://github.com/benjamin-awd/monopoly/commit/e4cd3791364da3203d1680849a9de6a8cad472ee"
        },
        "date": 1792412007010,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.8927560783399999,
            "range": "± 0.041878638789136544",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.9856854335200005,
            "range": "± 0.02820673272714595",
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
          "id": "5b4f5db59ecea09e23e770476ffd9e0837ce2712",
          "message": "build(deps): bump certifi to 2026.10.19 and drop unused pdm.lock (#337)\n\npdm.lock has been unused since the switch to uv (June 2025); pdm-backend\nremains only as the build backend.\n\nCo-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-21T17:33:44+08:00",
          "tree_id": "3f57d1daef5d98171e5b97c27acbd46e57a76c23",
          "url": "https://github.com/benjamin-awd/monopoly/commit/5b4f5db59ecea09e23e770476ffd9e0837ce2712"
        },
        "date": 1792575322895,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.7797771394,
            "range": "± 0.004384114922696835",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 3.4996078804199997,
            "range": "± 0.021777343908501584",
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
          "id": "8149dd5293df324a111a60cbaff209e9588338b1",
          "message": "chore: use python@3.13 in Brewfile to match .python-version\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-22T17:00:11+08:00",
          "tree_id": "e7d2160b0e5541d9f18a06731971003fc8848880",
          "url": "https://github.com/benjamin-awd/monopoly/commit/8149dd5293df324a111a60cbaff209e9588338b1"
        },
        "date": 1792659837266,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.90557295874,
            "range": "± 0.0626608933029336",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 4.06402486308,
            "range": "± 0.02525793263890222",
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
          "id": "dadc569b35b1dc617a4df3a1277a5da9e72410d3",
          "message": "chore: pin Python 3.13 for local development (#343)\n\n* chore: pin Python 3.13 for local development\n\nPython 3.14 has no prebuilt wheel for the locked regex==2024.11.6, so uv\nfalls back to compiling it from source and fails without a C compiler.\nStop ignoring .python-version so the pin is shared.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* chore: drop python from Brewfile; uv provisions it via .python-version\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* build: use uv-managed Python so pdftotext builds with the system toolchain\n\nHomebrew's Python hardcodes CC=gcc-N in sysconfig, so pdftotext was built\nwith brew's gcc and a RUNPATH to its older libstdc++, which failed to load\nagainst the system libpoppler (GLIBCXX_3.4.32 not found). gcc@11 in the\nBrewfile only existed to satisfy that.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* build: install system deps with apt on Linux, brew elsewhere\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* docs: update setup instructions for uv-managed Python and apt on Linux\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n---------\n\nCo-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-22T17:16:01+08:00",
          "tree_id": "3851d065d6c0284880b8771cb7f4053f3529eda8",
          "url": "https://github.com/benjamin-awd/monopoly/commit/dadc569b35b1dc617a4df3a1277a5da9e72410d3"
        },
        "date": 1792660658918,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.69623174204,
            "range": "± 0.005520986170661477",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.8923397690200003,
            "range": "± 0.03212744091539736",
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
          "id": "33e7878b78963bb6197d3b16db55058193daa7a6",
          "message": "build(deps): bump pdftotext to 4.0.0 and drop pkg-config (#344)\n\n* chore: pin Python 3.13 for local development\n\nPython 3.14 has no prebuilt wheel for the locked regex==2024.11.6, so uv\nfalls back to compiling it from source and fails without a C compiler.\nStop ignoring .python-version so the pin is shared.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* chore: drop python from Brewfile; uv provisions it via .python-version\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* build: use uv-managed Python so pdftotext builds with the system toolchain\n\nHomebrew's Python hardcodes CC=gcc-N in sysconfig, so pdftotext was built\nwith brew's gcc and a RUNPATH to its older libstdc++, which failed to load\nagainst the system libpoppler (GLIBCXX_3.4.32 not found). gcc@11 in the\nBrewfile only existed to satisfy that.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* build: install system deps with apt on Linux, brew elsewhere\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* docs: update setup instructions for uv-managed Python and apt on Linux\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* build(deps): bump pdftotext to 4.0.0 and drop pkg-config\n\npdftotext 4.0.0 moved to pyproject.toml and no longer needs pkg-config at\nbuild time (it links -lpoppler-cpp directly). Extraction with physical=True\nis byte-identical to 3.0.0 across 89 real statements.\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n* chore: drop redundant python-preference comment from pyproject\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n\n---------\n\nCo-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-22T17:19:24+08:00",
          "tree_id": "7e2a62ccd3d2e347e1d28e8e5eafadd47b273aa2",
          "url": "https://github.com/benjamin-awd/monopoly/commit/33e7878b78963bb6197d3b16db55058193daa7a6"
        },
        "date": 1792661058941,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.48487047606000006,
            "range": "± 0.005540812694006881",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.04422461634,
            "range": "± 0.06926065112813205",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "82356519+bsaurusrex@users.noreply.github.com",
            "name": "Brian Taylor",
            "username": "bsaurusrex"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e2de73bd432b1e73527a4ccfeab8e775a45dc8fd",
          "message": "fix(dbs): read DBS/POSB consolidated statements rendered by StreamServe (pre-2021) (#342)\n\n* fix(dbs): detect statements rendered by StreamServe (pre-2021)\n\nDBS credit card statements issued before mid-2021 carry creator \"DBS\" and a\nStreamServe producer instead of Quadient, so they fell through to the generic\nparser: rows lost their card number and some statements failed with\n\"Could not find any transactions\". The existing DBS credit config parses them\nunchanged once they're detected.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* feat: stamp each transaction with its own card on consolidated statements\n\nA consolidated statement (DBS prints one per customer) has one section per card,\neach opened by its own \"CARD NO.:\" header and with its own previous balance.\nThe account was located once per statement, so every row, and every previous\nbalance, carried the first card's number.\n\nAdd an opt-in StatementConfig.account_per_section: each transaction (and each\nprevious-balance row) takes the account of the nearest account_pattern match\nabove it. Enabled for the DBS credit config. Off by default, so other banks'\noutput is unchanged; Statement.account still returns the first account.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* fix(dbs): skip balance-only lines and read the account on consolidated statements\n\nThe last line of an account's transactions on a DBS/POSB consolidated statement\ncarries a date and the account's balance, with nothing withdrawn or deposited.\nOn pages where the table sits far enough right, it fell inside\ntransaction_bound and was read as a deposit of the balance, so the safety check\nfailed. Require a description, which that line never has.\n\nAlso read the account number from the account summary row, so transactions\ncarry the account's last 4 digits.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* fix(dbs): read DBS/POSB consolidated statements rendered by StreamServe (pre-2021)\n\nDBS/POSB consolidated (deposit) statements issued before mid-2021 have an empty\ncreator and a StreamServe producer, so they weren't detected as DBS. Under the\ngeneric parser, their debit card summary (\"DATE DESCRIPTION ... AMOUNT\") made\nthem look like credit statements, and the safety check failed.\n\n- New identifier group: \"DBS Bank Ltd\" and \"CONSOLIDATED STATEMENT\" in the text,\n  StreamServe producer.\n- New `consolidated_legacy` config, tried first: its \"Date Description\n  Withdrawal Deposit Balance\" header (no \"(-)\"/\"(+)\") occurs in no other DBS\n  layout. \"03 Jun\" dates, title-case months only (the card summary that follows\n  the accounts uses capitals and repeats spending already listed), the account\n  from each \"Account No.\" header (account_per_section), \"As at\" statement date.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* feat: resolve each transaction's account by section for every bank\n\nEvery account_pattern match now opens a section, and a transaction takes the\naccount of the nearest header above it. This replaces the opt-in\naccount_per_section flag: consolidated statements from several banks (OCBC,\nBank of America, DBS) need it, and Standard Chartered's rows were tagged with\nthe number from its summary table instead of the card above them.\n\nThe lookup moves into AccountResolver, which also fixes the _iter_matches\nreturn type that mypy flagged. The Standard Chartered fixture is regenerated:\nits rows now take the section's card, which also changes their ids.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* fix: give each previous balance the account of its own line\n\nA previous-balance row found its account by searching the statement for a line\nwith the same text, so identical balance lines in two sections both took the\nfirst section's account. get_prev_month_balances now returns each match with its\npage and line (PrevBalanceMatch), and the account is resolved from that position.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* fix(dbs): read the consolidated account from each section header\n\nThe account came from the account summary row, which is printed before every\nsection, so with section-based resolution every row would take the last summary\naccount. Some statements also print a truncated number there, leaving the\naccount empty. Each account's table opens with \"Account No. 123-456789-0\" on\nevery page, so that line is used instead.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor(dbs): reuse the shared title-case date pattern for legacy consolidated rows\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor(dbs): share the consolidated account and non-empty description patterns\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor: build account headers once and bisect them by position\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor: split the account header match into two readable steps\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor: name the account header tuple\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* docs(ocbc): describe account_pattern as a per-card section header\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* refactor: drop the unused statement-level account\n\nTransactions and previous balances already read their account from\nAccountResolver.at, so BaseStatement.account and its account_at wrapper\nhad no callers outside tests.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n---------\n\nCo-authored-by: Claude Opus 5.5 <noreply@anthropic.com>\nCo-authored-by: Benjamin Dornel <benjamindornel@gmail.com>",
          "timestamp": "2026-10-22T20:56:56+08:00",
          "tree_id": "cf03412cff84a2785b5e7ae5c0264df9c89075c3",
          "url": "https://github.com/benjamin-awd/monopoly/commit/e2de73bd432b1e73527a4ccfeab8e775a45dc8fd"
        },
        "date": 1792673905509,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.33825670976,
            "range": "± 0.0037912497490475397",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.39749833642,
            "range": "± 0.02939506773156323",
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
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "efa7a53511f04b0ee3e673eb858a59bdfc6eefa9",
          "message": "chore(main): release 0.23.3 (#346)\n\nCo-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>",
          "timestamp": "2026-10-22T20:59:52+08:00",
          "tree_id": "c1d859cb4f2c00968ff355f8cdc4283c314d06bc",
          "url": "https://github.com/benjamin-awd/monopoly/commit/efa7a53511f04b0ee3e673eb858a59bdfc6eefa9"
        },
        "date": 1792674055698,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.44258327572,
            "range": "± 0.02925926876503627",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.61077481548,
            "range": "± 0.030662967228030132",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "82356519+bsaurusrex@users.noreply.github.com",
            "name": "Brian Taylor",
            "username": "bsaurusrex"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6c2900b64b537b667147c4f70c263fb940b080f1",
          "message": "feat(amex): read American Express cards issued in the United States (#349)\n\n* feat(amex): read American Express cards issued in the United States\n\nAdds an Amex.us config beside the Singapore Platinum one. US statements are told apart by\ntheir metadata (title \"CSF.CRS.US....\", creator \"FIS Global Corp.\") plus americanexpress.com,\nand their config by the \"Account Ending 4-12345\" line every page header carries.\n\nRows are \"MM/DD/YY[*] DESCRIPTION ... [-]$AMOUNT\" in USD, the account is the last 4 of\n\"Account Ending\", and the payment summary comes from the first page's New Balance, Minimum\nPayment Due and Payment Due Date lines.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n* docs(readme): name the Singapore Amex card the existing config reads\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n\n---------\n\nCo-authored-by: Claude Opus 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-23T18:18:32+08:00",
          "tree_id": "99bcd374cd5f5e4ac706d1d76734bd77f1effb73",
          "url": "https://github.com/benjamin-awd/monopoly/commit/6c2900b64b537b667147c4f70c263fb940b080f1"
        },
        "date": 1792750785612,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.5076449782199999,
            "range": "± 0.019873189039537074",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.9907939039000002,
            "range": "± 0.049776041205509665",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "82356519+bsaurusrex@users.noreply.github.com",
            "name": "Brian Taylor",
            "username": "bsaurusrex"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "99b6bb52e0ce49ccb8921303612c909a3ba4d2b4",
          "message": "feat(capital-one): add Capital One 360 (US) bank statements (#348)\n\nA new CapitalOneUS bank (capital_one_us) for Capital One 360 statements, which list every 360\naccount in one PDF, each in its own section. Identified by the PDF metadata (author\ncapitalone.com, title \"Bank Statement\"); the existing CapitalOneCanada config is unchanged.\n\nRows carry their own account's last 4 from each section's \"360 Checking - <number>\" header,\nsigned \"+ $\" / \"- $\" amounts set the direction, and the period comes from \"Mar 1 - Mar 31, 2026\".\nThe statement prints no totals, only opening and closing balances, so safety_check is off.\n\nCo-authored-by: Claude Opus 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-23T18:19:05+08:00",
          "tree_id": "85fe82496ec800f934db993f0486e82e6b58c0f9",
          "url": "https://github.com/benjamin-awd/monopoly/commit/99b6bb52e0ce49ccb8921303612c909a3ba4d2b4"
        },
        "date": 1792750868509,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6552770829999999,
            "range": "± 0.05215398346717669",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.5609120615000003,
            "range": "± 0.045697083002076554",
            "unit": "s"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "82356519+bsaurusrex@users.noreply.github.com",
            "name": "Brian Taylor",
            "username": "bsaurusrex"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b6c6b27244b8a557d030d11b7efaaf4cd08bae2a",
          "message": "fix(chase): read masked card numbers and the payment summary (#347)\n\nChase now prints the card number masked (\"Account Number: XXXX XXXX XXXX 1234\"), which the\naccount pattern (four groups of digits) missed, so every row came back without an account.\nThe pattern now accepts X in the masked groups, as Bank of America's does.\n\nAlso adds a PaymentSummaryConfig from the payment coupon's \"Payment Due Date:\", \"New Balance:\"\nand \"Minimum Payment Due:\" lines, and the first Chase text fixture.\n\nCo-authored-by: Claude Opus 5.5 <noreply@anthropic.com>",
          "timestamp": "2026-10-23T18:20:37+08:00",
          "tree_id": "6cab75b58e7eb291dcf30c1b14d6195d44396e35",
          "url": "https://github.com/benjamin-awd/monopoly/commit/b6c6b27244b8a557d030d11b7efaaf4cd08bae2a"
        },
        "date": 1792750932621,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.3820339014000001,
            "range": "± 0.016270508247314366",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 1.48071181804,
            "range": "± 0.018405630100758456",
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
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7b5c7fd208ae3783cf53aeae45d17955c81d4781",
          "message": "chore(main): release 0.23.4 (#350)\n\nCo-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>",
          "timestamp": "2026-10-23T18:47:31+08:00",
          "tree_id": "7103168ae6143d95b0e5ca185db7d47c921d8724",
          "url": "https://github.com/benjamin-awd/monopoly/commit/7b5c7fd208ae3783cf53aeae45d17955c81d4781"
        },
        "date": 1792752541861,
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "Single file",
            "value": 0.6732289077000001,
            "range": "± 0.007180260269637185",
            "unit": "s"
          },
          {
            "name": "Integration (10 banks)",
            "value": 2.87413601098,
            "range": "± 0.022178775387202785",
            "unit": "s"
          }
        ]
      }
    ]
  }
}