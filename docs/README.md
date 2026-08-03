# Documentation

| Document | What it covers |
|---|---|
| [architecture.md](architecture.md) | How the plugin splits into skills, agents, and a protocol — and which of the three owns each rule |
| [flows/loop-run.md](flows/loop-run.md) | What one `/solodev:loop` run does, phase by phase, and where its state goes |
| [evidence/](evidence/) | Verification captures kept by each run's Phase 4 |

`README.md` at the repo root covers what the plugin is and how to install it. These
documents cover how it works internally, for someone changing it rather than using it.

The loop's live state — backlog, Run Log, learned rules — is **not** here. It lives in
`specs/`, because it is rewritten every run and mixing it with stable documentation
makes both harder to trust.
