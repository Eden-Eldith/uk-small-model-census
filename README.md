# What About the Independents Then: Investigating Small Large Language Models in the UK

Phillip Charles O'Brien (Eden Eldith) · 3 November 2026 · **Version 1.2.1**

**Published preprint.** Version 1.2.1 was published on Zenodo on 3 November 2026, with the paper, companion appendix, source and data archives.

**All versions:** [10.5281/zenodo.23923241](https://doi.org/10.5281/zenodo.23923241) · **This version (1.2.1):** [10.5281/zenodo.23923242](https://doi.org/10.5281/zenodo.23923242)

The frozen 30 October cohort contains **917 model repositories and 495 publishing accounts**. Hugging Face is the GitHub of open-source models. The study follows released work to UK builders outside university and institutional routes, and shows what company-centred sovereign-AI inventories miss. Britain needs to discover, support and retain the people who already build domestic models; a company inventory leaves independent work outside its starting population.

The paper argues that the race through recursive self-improvement (RSI), AGI and ASI makes domestic model-building urgent: Britain must become a producer or risk becoming a vassal state dependent on other powers. It examines the 2026 Hugging Face intrusion and the responders' blocked access to hosted-model analysis as a concrete failure of operational independence. It connects that evidence to the limits of the National Security Strategy's baseline ambition, active defence, talent retention and a national model-building programme. Practical proposals include regional compute, distributed training, learning routes and apprenticeships with a stake in inventions.

The sovereignty discussion also connects Rupert Lowe's calls for [sovereign AI on 24 October](https://x.com/RupertLowe10/status/2113876438617063857) and [cyber defence and British technical expertise on 2 November](https://x.com/RupertLowe10/status/2117258349569880131) to the paper's argument. As leader of Restore Britain, he expresses the same urgency about national capability; the census asks how Britain will discover and support the independent builders who could help deliver it.

[Read the paper](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/paper/What_About_the_Independents_Then_2026-10-31.pdf) · [Full 495-account appendix](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/paper/UK_Small_Model_Census_Appendix_2026-10-31.pdf) · [Dataset](https://huggingface.co/datasets/edeneldith/uk-small-model-census) · [Published Zenodo record](https://zenodo.org/records/23923242) · [Original deposit package](https://huggingface.co/datasets/edeneldith/uk-small-model-census/resolve/main/release/UK_Small_Model_Census_Zenodo_Package.zip)

## Citation

O'Brien, P. C. (2026). *What About the Independents Then: Investigating Small Large Language Models in the UK* (Version 1.2.1) [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.23923242

Use the version DOI above to cite this release, and record the Hugging Face commit used for data analysis. The all-versions DOI represents the work across releases and resolves to the latest version.

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

The original crest and author cover are retained, and earlier versions remain in repository history. The PDFs and source/data ZIPs match the files published on Zenodo. The original deposit package retains its preparation-time guide and metadata; the repository pages and citation file now record the published DOIs. The deposited source snapshot is [GitHub commit 0de665f](https://github.com/Eden-Eldith/uk-small-model-census/tree/0de665f0fe0c51afce5b55a07b933f70848397e5); use that snapshot to reproduce the deposited source bundle.

[Method](METHODS.md) · [Paper source](paper/main.tex) · [ORCID](https://orcid.org/0009-0007-3961-1182)

Original code: MIT. Original annotations and paper: CC BY 4.0. Third-party model metadata and official statistics retain their source rights. I created WiggleGPT and supplied this paper's research question, interpretation and substantive narrative. As a disabled independent researcher, I used Sol 6.1 (ultra effort, OpenAI) as an accessibility and writing aid, alongside research assistance from Astra (OpenAI) and Claude (Anthropic), under my direction.
