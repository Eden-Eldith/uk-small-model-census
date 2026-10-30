# Study scope and method

## Question

Which publicly documented UK-based researchers can be found behind Hugging Face model releases matching the user's exact small-model discovery filters? How well does this repository-first search surface work outside company and university inventories?

## Cohort

The browser query selects text generation, English, PyTorch, the displayed under-one-billion-parameter range (`min:0,max:1B`), and Base only (`base_model_relation=base`). Results are ordered by recently updated. No name search, geographic, hardware, licence, inference-provider or minimum-download filter is used. The complete cohort is retained, including small, unpopular, educational and institutional releases.

On 30 October 2026, the website reported **917 models**. We retrieved every API page using the server's `Link: next` URL and independently retrieved all 31 website pages. Both yielded the same 917 unique identifiers, from 495 publisher accounts. All 917 displayed parameter counts were strictly below one billion. Counts describe a dated catalogue snapshot, not all language models ever created.

`data/collection.json` records the query, time interval, pagination and identity-set comparison. `data/raw/models.jsonl` preserves public API records. `data/models_all.csv` is the complete flattened cohort. `numParameters` comes from the website listing, not a number guessed from a model name.

## Meaning of filters

The cohort is defined by the Hub's own discovery metadata. English tags do not measure English capability. A PyTorch tag records catalogue compatibility rather than a new runtime test. Base only is a catalogue ancestry filter; it does not independently establish random-initialisation pretraining, original architecture, training quality, hardware ownership or independence. Those properties are checked from model documentation for UK findings and reported separately.

The API also uses infrastructure-region tags such as `region:us`. Those are never treated as researcher location. Flags, names, English-language text, dataset geography and company headquarters do not establish an individual's nationality or residence.

## Researcher identification

All 495 accounts are assigned once to one of three research agents, with 165 accounts each. Each reviewer examines the public Hugging Face profile, linked identity sources and relevant model cards. Explicitly linked GitHub profiles are retrieved centrally to preserve a traceable identity chain. Model cards are requested at the API-recorded revision. A profile missing from the API is not treated as nonexistent if its public page remains available.

The reviewer records the actual model creator where the sources identify one. Publisher, republisher, organisation and named researcher are distinguished. An organisation's address alone is not attributed to all its contributors. Accounts with several creators can have mixed locations; model-specific links are retained.

Location labels are: `uk_public_location`, `non_uk_public_location`, `uk_affiliation_only`, `mixed_locations`, and `unknown`. The evidence basis states whether a label comes from a public self-reported location, a personal biography, institutional affiliation, or organisation location. 'UK-based' is a geographic description; citizenship and birthplace are not inferred. Historical or ambiguous locations remain qualified in the notes.

Every location assertion includes a source URL, the relevant short text, its basis and retrieval date. Unknown is a recorded research outcome, not a non-UK classification. All accounts remain in the release, including those with no adequate public location evidence. The paper reports the unresolved fraction alongside positive findings.

## UK model evidence

For identified UK researchers, review the linked model documentation for training origin (from scratch, derivative, or unresolved), architecture contribution, training hardware, and institutional/company support. Do not infer self-funding from an empty affiliation field, or complete national autonomy from an open licence. Preserve the model author's stated mechanism and distinguish that from comparative performance that was actually evaluated.

## Interpretation

The primary outputs are a complete discovery cohort and source-supported geographic findings. Repository counts, publisher counts, named researchers and confirmed original-training projects are different quantities. Multiple checkpoints from one project do not represent multiple independent researchers. This study does not rank model quality or claim an exhaustive census of untagged, private, deleted, non-Hugging-Face or larger models.

The author's prior cross-platform searches found no other case satisfying a narrower conjunction of British/long-term UK residence, independent funding, personal consumer hardware, from-scratch pretraining and public documentation. Those findings motivate the present work. This new systematic cohort is analysed on its own evidence and uses UK location as requested; it does not silently import those narrower eligibility conditions.

## Public outputs

GitHub contains collection/analysis code, methods and paper sources. Hugging Face is intended to host the raw public model metadata and derived tables, including the complete cohort and UK views. The author will handle the Zenodo paper upload. Local working copies of complete profile pages and model cards support the investigation; the public dataset uses relevant factual fields, short source quotations and source links rather than unrelated personal details.

The paper discloses AI assistance and the author's relationship to WiggleGPT. The user's own original research remains represented under the same cohort and evidence rules.
