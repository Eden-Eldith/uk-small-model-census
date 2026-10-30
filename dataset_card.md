---
license: cc-by-4.0
language:
- en
pretty_name: UK Small-Model Census — 30 October 2026
size_categories:
- n<1K
task_categories:
- tabular-classification
tags:
- model-discovery
- uk-ai
- independent-research
- research-metadata
- huggingface-hub
configs:
- config_name: all_models
  default: true
  data_files:
  - split: train
    path: data/models_all.csv
- config_name: models_with_locations
  data_files:
  - split: train
    path: data/models_with_locations.csv
- config_name: researcher_locations
  data_files:
  - split: train
    path: data/researcher_locations.csv
- config_name: uk_models
  data_files:
  - split: train
    path: data/uk_models.csv
- config_name: uk_connected_models
  data_files:
  - split: train
    path: data/uk_connected_models.csv
- config_name: uk_creator_models
  data_files:
  - split: train
    path: data/uk_creator_models.csv
- config_name: uk_model_evidence
  data_files:
  - split: train
    path: data/uk_model_evidence.csv
- config_name: uk_affiliations
  data_files:
  - split: train
    path: data/uk_affiliated_models.csv
- config_name: unresolved_locations
  data_files:
  - split: train
    path: data/location_unknown_models.csv
---

# UK small-model census

A complete dated cohort of **917 model repositories from 495 publishing
accounts**, with source-linked research into the people and UK connections
behind those releases. The aim is to make released work discoverable,
including work outside registered-company inventories.

The collection ran on **30 October 2026, 12:18:53–12:19:08 UTC**.
All ten API pages and all 31 website pages returned the same complete set
of 917 model identifiers. Every account has a location-research record.

Eight individual publisher accounts have explicit UK personal locations.
Model-specific follow-through identifies **16 repositories linked to
12 UK-located people across 11 publishing accounts**: 15 developer/coauthor
connections and one dataset/applications contributor. The broader view has
**30 repositories**, adding 13 UK institutional-affiliation cases and one
location conflict. **245 accounts remain unresolved**. There are 37 detailed
model assessments, including seven related collective cases with no
established model-specific UK connection.

## Exact discovery query

- Task: **Text Generation**
- Language: **English**
- Library: **PyTorch**
- Parameter range: **under 1 billion** in the interface, query `min:0,max:1B`
- Ancestry selection: **Base only**, query `base_model_relation=base`
- Sort: **Recently updated**
- Empty model-name search; no hardware, licence or inference-provider filter

[Original query](https://huggingface.co/models?pipeline_tag=text-generation&num_parameters=min:0,max:1B&library=pytorch&language=en&base_model_relation=base&sort=modified)
and [recorded configuration](config/filters.json).
All 917 reported parameter counts in this snapshot are strictly below one
billion. Catalogue membership and verified training provenance are separate.

## Reading the data

| File/configuration | Unit and purpose |
|---|---|
| `all_models` | Every one of the 917 original matches; no geographic or quality exclusion |
| `models_with_locations` | All 917 rows joined to publisher/creator evidence and explicit UK connection types |
| `researcher_locations` | One record for each of the 495 publisher accounts; identities, location basis, short quotations and URLs |
| `uk_models` | Models with an identified person's public UK location; includes company research and non-language tasks where the catalogue admitted them |
| `uk_creator_models` | The 15 rows with identified publishers/developers or model-paper coauthors; excludes the dataset/applications-only contributor row |
| `uk_connected_models` | Broader union including institutional affiliations and unresolved UK/non-UK location conflicts |
| `uk_model_evidence` | Training origin, task, architecture, hardware and support, reported independently for UK-connected cases |
| `uk_affiliations` | Model-specific UK affiliation evidence; not a claim of individual residence |
| `unresolved_locations` | Models whose publisher-location research remains unresolved |

`train` is the dataset viewer's table split name. These tables are research
metadata, not a language-model training corpus. Nested CSV cells contain
JSON strings; `.jsonl` companions preserve structured annotations.

The **raw** folder contains the complete public API records, website-listing
records and publisher mapping. It contains no model weights. `collection.json`
records the exact requests and completeness comparison. `statistics.json`
contains the final counts. `model_card_sources.csv` and `profile_sources.csv`
record retrieval provenance; `manifest.json` records file hashes.

## Location evidence and interpretation

Three research agents each examined a non-overlapping assignment of 165
accounts. Public Hub profiles, model cards, explicitly linked GitHub identities,
personal sites and institutional sources were followed. Publisher accounts,
model creators and republishers are distinguished in the evidence and notes.

The `location_status` labels describe the account review:

- `uk_public_location`: an individual's explicit public UK location, or an
  organisation's location with its separate evidence basis.
- `non_uk_public_location`: a documented non-UK geographic link. The basis
  distinguishes personal self-location, professional affiliation and
  organisation headquarters; the label does not locate every contributor.
- `uk_affiliation_only`: UK institutional evidence without a separate
  attributable personal-location statement.
- `mixed_locations`: a distributed group or conflicting location sources;
  details determine which interpretation applies.
- `unknown`: the examined sources did not establish an attributable location.

Model-level `uk_connection_types` distinguish `individual_public_location`,
`creator_public_location`, `contributor_public_location`, `institutional_affiliation`, `conflicting_location`
and `organisation_location`. These can overlap. A company address is not
assigned to all its researchers. Citizenship, ethnicity and birthplace are
not inferred. Infrastructure tags such as `region:us` are not author locations.

The detailed model table distinguishes documented pretraining from an
autogenerated card claim, fine-tuning, partial training and missing evidence.
Unknown funding does not mean independent funding. Unknown location does
not mean outside the UK. The source documentation supplies training claims;
this census did not rerun models or assess their quality.

## Scope

This is the complete result of the specified query at the recorded time,
not all UK AI research. Metadata omissions, other hosting services, larger,
private or deleted models fall outside the sampling frame. Some matching
repositories contain adapters, untrained models, fine-tunes or biological
sequence models. They remain in the raw cohort, with relevant distinctions
in the derived evidence. Counts refer to repositories or publisher accounts,
not automatically to distinct independent researchers.

All 495 public profiles were retrieved successfully. Of 917 pinned raw
model-card requests, 892 returned text and 25 returned HTTP 401. Where a
public HTML model card was used instead, its source is labelled accordingly.

## Code, paper and attribution

[Collection and analysis code](https://github.com/Eden-Eldith/uk-small-model-census)
includes the exact filters and methods. The LaTeX paper is titled
*Beyond Company Inventories: Finding UK-Based Model Builders on Hugging Face*.
Its author will handle the Zenodo deposit; no new paper DOI is claimed here.

Author: **Phillip C. O'Brien (Eden Eldith)**,
[ORCID 0009-0007-3961-1182](https://orcid.org/0009-0007-3961-1182).
The author created WiggleGPT, a model included in the cohort. Codex and
three research agents assisted collection, source research and drafting.
This was not a blinded independent human review of every annotation.

Original compilation and annotations: **CC BY 4.0**. Original code: **MIT**.
Source metadata and brief quotations retain their attribution and applicable
rights. The census does not relicense any underlying models or datasets.
See [licence and attribution](LICENSE.md).

Please cite the dated snapshot and the dataset commit used. Corrections
can be submitted through a dataset discussion or the code repository's
issues, with an attributable public source.

```bibtex
@dataset{obrien2026uksmallmodels,
  author = {O'Brien, Phillip C.},
  title = {UK Small-Model Census: Public Releases and Researcher Location Evidence},
  year = {2026},
  version = {1.0.0},
  url = {https://huggingface.co/datasets/edeneldith/uk-small-model-census},
  note = {Snapshot collected 30 October 2026; cite the dataset commit used}
}
```
