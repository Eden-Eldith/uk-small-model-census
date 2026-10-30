# UK small-model census

**917 model repositories. 495 publishing accounts. Every account reviewed.**

This project starts with released models and follows their public sources to
the people behind them. It includes individual work that falls outside
registered-company inventories. The snapshot was collected on **30 October
2026, 12:18:53–12:19:08 UTC**.

[Data and CSV downloads](https://huggingface.co/datasets/edeneldith/uk-small-model-census)
· [Methods](METHODS.md) · [LaTeX paper source](paper/main.tex)

## Exact filters

**Text Generation · English · PyTorch · under 1B · Base only · Recently updated**

There is no name search, hardware, licence or inference-provider filter.
The size query is `num_parameters=min:0,max:1B`; the base query is
`base_model_relation=base`. The full query is in [config/filters.json](config/filters.json).

All ten API pages and all 31 website pages yielded the same 917 unique model
IDs. Every reported parameter count was strictly below one billion. The
original set is retained, including metadata mismatches, derivatives and
untrained releases.

## Findings

| Account-level location evidence | Accounts |
|---|---:|
| Explicit UK personal location | 8 |
| UK affiliation only | 1 |
| Mixed or conflicting locations | 6 |
| Non-UK geographic evidence | 235 |
| Unresolved | 245 |

Model-specific follow-through identifies **16 repositories linked to
UK-located people across 11 publishing accounts**, representing 12 named
people. Of those repositories, 15 have a documented publisher/developer or
paper-coauthor connection; one has a dataset/applications contributor.
These roles do not all imply that the named person operated the training run.

The broader UK-connected view contains **30 repositories**: those 16, another
13 with UK institutional affiliations, and one with conflicting locations.
The release includes **37 detailed model assessments**, including seven
related collective releases without an established model-specific UK link.
Three of the 16 UK-location-connected repositories model microbiome
sequences rather than ordinary English, despite matching catalogue tags.

The findings include Ahmad Bader's documented TinyStories training on a
laptop CPU and Phillip C. O'Brien's WiggleGPT architecture experiment trained
from scratch on consumer GPUs. Standard model training, fine-tuning,
institutional collaboration, hardware and funding are recorded separately.
The census does not infer self-funding from an individual account or
non-existence from unresolved location.

The non-UK account category includes labelled organisational locations and
professional affiliations; it is not a count of individually verified
residents. No citizenship or birthplace inference is used. Full source URLs,
short evidence excerpts and role distinctions are in the data release.

## Reproduce the published analysis

Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/analyse.py
```

For an immutable snapshot, pass the Hugging Face dataset commit SHA as
`--revision SHA` to the download command. The downloader checks each file
against `data/manifest.json` and does not overwrite differing local files
without `--overwrite`.

The analysis regenerates the full join and derived CSVs from the released
source annotations, checks all 495 accounts and 917 model IDs, and requires
model-level evidence for every claimed UK linkage. It does not manufacture
new geographic findings from a keyword list.

## Collect a new dated cohort

```sh
python scripts/collect.py --stage listing
python scripts/collect.py --stage enrich
python scripts/enrich_github.py
```

The listing stage follows every API pagination link and compares the complete
website result set. The enrichment stage collects public profiles and
revision-pinned model cards into the ignored `work/` directory. Optional
`GH_TOKEN` or `GITHUB_TOKEN`, or `--git-credential` with an existing Git
credential, raises the public GitHub API quota. Credentials are never written
to the dataset. No model weights are downloaded and repository code is not
executed.

A fresh collection will reflect a changing catalogue. Geographic annotations
require a new source review; the published annotations describe this dated
snapshot. See [METHODS.md](METHODS.md) for the evidence rules.

The API approach was prompted by
[this Stack Overflow question](https://stackoverflow.com/questions/75810246/how-to-get-all-hugging-face-models-list-using-python)
and uses the [Hub API](https://huggingface.co/docs/hub/api), including the
current interface's parameter-range and ancestry query fields.

## Paper

*Beyond Company Inventories: Finding UK-Based Model Builders on Hugging Face*
discusses the completed findings and their relevance to mapping UK AI
capability. Build with a LaTeX installation containing `biblatex` and Biber:

```powershell
./scripts/build_paper.ps1
```

Alternatively run `pdflatex main`, `biber main`, then `pdflatex main` twice
inside `paper/`. The author will handle the Zenodo paper upload; no new
paper DOI is claimed before that deposit.

Author: **Phillip C. O'Brien (Eden Eldith)**,
[ORCID 0009-0007-3961-1182](https://orcid.org/0009-0007-3961-1182).
Codex and three research agents assisted collection, public-source research,
analysis and drafting. The author created WiggleGPT, one included model.

Original code: [MIT](LICENSE). Original annotations and paper text:
[CC BY 4.0](DATA_LICENSE.md). Underlying models, source datasets and
third-party text retain their original rights and attribution.

Corrections are welcome through an issue with the model/account ID and an
attributable public source. Private location details are not needed.
