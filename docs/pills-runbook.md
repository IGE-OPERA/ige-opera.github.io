# Research pills runbook

A *research pill* is a one-line, plain-language summary of one of our papers,
shown on the publication page under the paper's title. Pills are produced with
[llm4pills](https://gricad-gitlab.univ-grenoble-alpes.fr/miai-formation-gricad/llm4pills)
and — following that tool's philosophy — are meant to be **validated by the
paper's authors** before going live. This is a human-in-the-loop pipeline: the
automation only tracks what needs doing.

## The loop

1. **Detection** — when the daily Zotero sync finds new papers, it opens a
   GitHub issue listing them ("Papers needing research pills"), one checklist
   entry per paper with its DOI and Zotero key.

2. **Generation** (a group member, locally — needs a provider key):

   ```bash
   # one-time setup (UGA / GRICAD):
   git clone https://gricad-gitlab.univ-grenoble-alpes.fr/miai-formation-gricad/llm4pills.git
   cd llm4pills && uv sync && cp .env.example .env
   #   .env: ALAN_API_KEY=... (alan: UGA VPN / campus) or
   #         ALBERT_API_KEY=... (albert: French public-service key, no VPN)
   #         and the matching ALAN_MODEL / ALBERT_MODEL from `uv run llm4pills models`

   uv run llm4pills generate <DOI> --audience general
   ```

   The tool fetches the paper, writes a seven-section summary, and runs an
   automatic faithfulness review (`revise` verdicts are recorded, not hidden —
   read the sidecar `<stem>.review.json`).

3. **Validation** — the paper's author reads the pill against the paper.
   Any claim that is `unsupported`, `overstated`, or just badly phrased gets
   fixed by hand. The one-liner we publish is short, faithful and readable by
   a non-specialist.

4. **Publication** — add it to `_data/pills.yml`, keyed by the Zotero key
   shown on the issue:

   ```yaml
   8Q5QRS2W: "How Python machine-learning components can be coupled to Fortran Earth system models through the OASIS3-MCT coupler."
   ```

   Open a PR (or commit to `main`) — the publication page shows the pill.

5. **Closure** — tick the checkbox in the issue. Once every entry on a pills
   issue is ticked, the next sync closes it automatically.

## Notes

- Papers without a pill simply render without one — nothing is blocked.
- The one-line format is what we publish on the cards; the full seven-section
  pill stays in the local llm4pills output for now (a future "Research pills"
  page can publish the validated full pills).
- `alan` only answers on the UGA network (VPN with the *personnel* profile);
  `albert` is publicly reachable and works from anywhere, including CI.
