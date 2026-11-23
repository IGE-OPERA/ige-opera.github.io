# Content management via Grist

The projects, outreach, news and open-positions content of this website is
maintained in the group's [Grist](https://grist.numerique.gouv.fr) workspace
(the "La Suite numérique" Grist instance). A scheduled GitHub Actions workflow
(`grist-sync.yml`) pulls the tables every day and commits the generated
`_data/*.yml` files, so the site builds from plain files and never depends on
Grist being up at build time.

## One-time setup

1. **Create the document** in the group workspace
   (<https://grist.numerique.gouv.fr/o/docs/ws/277565/>), one table per content
   type, with **exactly these column names**:

   **Projects**            | type
   ------------------------|---------------------------
   `title`                 | Text *(required)*
   `excerpt`               | Text (newlines become line breaks)
   `url`                   | Text
   `btn_label`             | Text (button label; default "Learn more")
   `image`                 | Attachment (project logo / photo)
   `status`                | Choice: `current` / `past`
   `sort`                  | Numeric (smaller first within a status)

   **Outreach** | type
   -------------|---------------------------
   `title`      | Text *(required)*
   `excerpt`    | Text
   `url`        | Text
   `image`      | Attachment
   `sort`       | Numeric

   **News**     | type
   -------------|---------------------------
   `date`       | Date *(required; drives ordering)*
   `title`      | Text
   `text`       | Text
   `url`        | Text
   `url_label`  | Text (link text; default "Read more")

   **Positions**| type
   -------------|---------------------------
   `title`      | Text *(required)*
   `type`       | Text (PhD, Postdoc, Internship, ...)
   `excerpt`    | Text
   `url`        | Text (application link)
   `contact`    | Text
   `deadline`   | Date
   `status`     | Choice: `open` / `filled`

2. **Get an API key**: in Grist, *Account Settings → API keys*, create a key.

3. **Add the repository secrets** (Settings → Secrets and variables → Actions):

   - `GRIST_DOC_ID` — the document id, the long string in the doc URL
     (`…/o/docs/<org>/<doc-id>/…`, or use *Share → Download… link* to see it)
   - `GRIST_API_KEY` — the key created above
   - `SYNC_TOKEN` — already used by the Zotero sync (a PAT with `repo` scope)

4. **Enable the workflow**: run *Sync content from Grist* manually once
   (Actions tab → *Sync content from Grist* → *Run workflow*).

## Daily workflow for editors

- add a project = add a row in `Projects` (+ logo in the `image` cell);
- close a position = set its `status` to `filled` (or delete the row);
- announce news = add a `News` row.

The site updates within a day (or after a manual workflow run). Image
attachments are downloaded to `assets/images/{projects,outreach}/` and served
from the site.

## Fallbacks

- If Grist is unreachable, the sync aborts **without writing**: the site keeps
  its last committed content.
- You can always edit `_data/*.yml` directly in git and open a PR; the next
  successful Grist sync will overwrite the same tables (rows deleted in Grist
  disappear from the site, so keep Grist authoritative once enabled).

## Local run

```bash
GRIST_DOC_ID=... GRIST_API_KEY=... python3 scripts/sync_grist.py
# optionally, a subset of tables:
GRIST_TABLES="News Positions" GRIST_DOC_ID=... GRIST_API_KEY=... python3 scripts/sync_grist.py
```
