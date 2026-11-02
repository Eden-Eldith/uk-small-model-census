# What About the Independents Then: Investigating Small Large Language Models in the UK

Phillip Charles O'Brien (Eden Eldith) · 2 November 2026 · **Version 1.2.1**

The frozen 30 October cohort contains **917 model repositories and 495 publishing accounts**. Hugging Face is the GitHub of open-source models. The study follows released work to UK builders outside university and institutional routes, and shows what company-centred sovereign-AI inventories miss. Britain needs to discover, support and retain the people who already build domestic models; a company inventory leaves independent work outside its starting population.

The paper connects discovery to recursive self-improvement: existing AI helps people develop further models, broadens who can participate, and makes timely support consequential for subsequent domestic capability. It develops the commercial case for useful small models, reciprocal public investment, and operational sovereignty through the NHS procurement and software-maintenance examples.

[Read the paper](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/paper/What_About_the_Independents_Then_2026-10-31.pdf) · [Full 495-account appendix](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/paper/UK_Small_Model_Census_Appendix_2026-10-31.pdf) · [Dataset](https://huggingface.co/datasets/edeneldith/uk-small-model-census) · [Zenodo deposit package](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/release/UK_Small_Model_Census_Zenodo_Package.zip)

## Actual results

| Measure | Count |
|---|---:|
| Frozen accounts / model repositories | 495 / 917 |
| Reviewed individual / organisation or collective / unresolved account identities | 398 / 86 / 11 |
| Primary current/model-period UK-connected people | 19 |
| UK builders / UK-built model entries | 5 / 7 |
| UK from-scratch builders / model entries | 3 / 5 |
| Institutional-route builders among the 5 UK builders | 4 |
| Institutional routes among the 19 primary UK-connected people | 17 |
| Strict-independent UK from-scratch builders | **1** |
| UK source connections / UK estimates | 10 / 2 |
| UK affiliation only / mixed connections | 1 / 11 |
| Non-UK connections or estimates | 387 |
| Region or timezone clues | 9 |
| Unresolved account geography / associated models | 75 / 98 |

**The confirmed strict-independent case is Phillip Charles O'Brien / WiggleGPT.** UK development includes 1 model with direct project-location evidence and 6 inferred from dated professional locations. Pietro Lesci is counted as a joint builder of three PolyPythias releases; the exact division of training operations is not established. The builders are O'Brien, Ahmad Bader, Augusto B. Corrêa, Xinyu Bai and Lesci. O'Brien, Bader and Lesci have from-scratch entries.

The geographic table uses the updated account assessments. The legacy source-location category remains in the data as source history. Follow-through of 151 formerly unanswered accounts supplies 66 country assessments: 23 high, 26 medium and 17 low confidence. Country estimates remain estimates with their confidence and source basis; region-only evidence retains the region. Builder location during training is recorded separately.

Whole-cohort provenance: **457 from-scratch, 352 derived, 36 mirrors, 60 untrained, 12 unresolved**. Labelled origin inferences cover 237 entries, including 154 of the from-scratch classifications. Each inference retains its confidence and source basis, alongside explicit publisher statements and detailed model assessments. Repository, training-run and person counts remain separate.

## Definitions and fixed population

Text Generation · English · PyTorch · under 1B · Base only · Recently Updated · no name search. The archived API and website identifier sets agree. Membership was not expanded or recollected. Base is a discovery tag, not proof of fresh initialisation.

UK-built refers to the builder's location during development and training; foreign cloud GPUs are a separate field. Strict independence requires no university attendance anywhere (including incomplete study), no institutional affiliation, including a technology day job, and affirmative independent-project evidence. Employment and project sponsorship remain distinct. All overlapping exclusions and unknowns remain in the appendix. No name-based or inferred-demographic analysis is included.

## Files and reproduction

The dataset supplies the frozen `models_all.csv` and `accounts.csv`, compact `*_inventory_annotations.jsonl` and `builder_classification_inputs.json`, all-account/model inventories, 35 person classifications, 55 detailed model decisions, computed statistics, descriptive summaries, provenance comparisons, context sources and a file-hash manifest. Source links and relevant evidence are public; private recordings, instructions, access logs and working notes are excluded.

The education context includes all 222 official DfE source observations and a complete 24-row ethnicity/sex/FSM comparison. The paper shows male and female rates for FSM and non-FSM pupils across Black African, Caribbean, mixed-background, Asian, White, other and unknown categories. Original pupil denominators and HE entrant counts are retained in the accompanying CSVs.

With Python 3.10 or later, install `requirements.txt`, then download this revision's data using `python scripts/download_data.py --revision DATASET_COMMIT_SHA`. Use the dataset's commit history to select the immutable revision; the downloader will not overwrite different local files without `--overwrite`.

```sh
python scripts/analyse.py
python scripts/build_appendix.py
```

These commands reproduce categories, counts, generated paper tables and appendix from released evidence, without fresh web searches. On Windows with MiKTeX and Biber, `./scripts/build_paper.ps1` builds the main paper. `python scripts/package_review.py` stages the allowlisted public data and builds matching source, data and Zenodo packages. Packaging never publishes automatically.

The original crest and author cover are retained. This correction advances the existing repositories through normal history; v1.0 remains in that history. The Zenodo ZIP is prepared for the author's deposit; no new DOI or deposit is claimed.

[Method](METHODS.md) · [Paper source](paper/main.tex) · [ORCID](https://orcid.org/0009-0007-3961-1182)

Original code: MIT. Original annotations and paper: CC BY 4.0. Third-party model metadata and official statistics retain their source rights. I created WiggleGPT and supplied this paper's research question, interpretation and substantive narrative. As a disabled independent researcher, I used Sol 6.1 (ultra effort, OpenAI) as an accessibility and writing aid, alongside research assistance from Astra (OpenAI) and Claude (Anthropic), under my direction.
