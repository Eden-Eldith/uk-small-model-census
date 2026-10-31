"""Generate paper totals and public release documentation from counted evidence."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'What About the Independents Then: Investigating Small Large Language Models in the UK'
HF = 'https://huggingface.co/datasets/edeneldith/uk-small-model-census'
GH = 'https://github.com/Eden-Eldith/uk-small-model-census'


def readl(name):
    return [json.loads(x) for x in (ROOT/'data'/name).read_text(encoding='utf-8').splitlines() if x.strip()]


def write(name, value):
    (ROOT/name).write_text(value, encoding='utf-8')


def main():
    i = json.loads((ROOT/'data/inventory_statistics.json').read_text(encoding='utf-8'))
    b = json.loads((ROOT/'data/builder_statistics.json').read_text(encoding='utf-8'))
    counts = {'CensusModels': i['frozen_models'], 'CensusAccounts': i['frozen_accounts'],
              'UKBuilders': b['uk_built_people'], 'UKBuiltModels': b['uk_built_model_entries'],
              'ScratchBuilders': b['uk_from_scratch_people'], 'ScratchModels': b['uk_from_scratch_model_entries'],
              'StrictBuilders': b['strict_independent_people'], 'UKInstitutional': b['uk_built_institutional_route_people'],
              'PrimaryPeople': b['primary_uk_connected_people'], 'PrimaryInstitutional': b['primary_institutional_route_people'],
              'UnknownAccounts': i['account_location_status']['unknown'], 'UnknownAccountModels': i['unresolved_location_models']}
    write('paper/generated_counts.tex', ''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in counts.items()))
    table = r'''\begin{table}[htbp]
\centering\small
\begin{tabularx}{\textwidth}{Xrr}
\toprule
Population or classification & People/accounts & Models \\
\midrule
Frozen publishing accounts and repositories & \CensusAccounts{} accounts & \CensusModels{} \\
Reviewed individual publishing identities & @IND@ accounts & -- \\
Organisation or collective publishers & @ORG@ accounts & -- \\
Publisher entity type unresolved & @ENTITYUNKNOWN@ accounts & -- \\
Primary current/model-period UK connections & \PrimaryPeople{} people & -- \\
UK development: direct or dated-location inference & \UKBuilders{} people & \UKBuiltModels{} \\
UK from-scratch development & \ScratchBuilders{} people & \ScratchModels{} \\
UK builders with institutional routes & \UKInstitutional{} people & -- \\
Strict-independent UK from-scratch development & \StrictBuilders{} person & 1 \\
Unresolved account geography & \UnknownAccounts{} accounts & \UnknownAccountModels{} \\
\bottomrule
\end{tabularx}
\caption{Account, person and model denominators remain distinct. UK development includes six model entries inferred from dated professional locations and one with direct project-location evidence. Rows overlap.}
\label{tab:counts}
\end{table}
'''
    for key, val in [('IND',i['account_identity_classes']['individual']),('ORG',i['account_identity_classes']['organisation_or_collective']),('ENTITYUNKNOWN',i['account_identity_classes']['unresolved_entity_type'])]:
        table=table.replace('@'+key+'@',str(val))
    write('paper/summary_table.tex',table)
    write('paper/abstract.tex',r'''\begin{abstract}
The United Kingdom is investing in sovereign AI, yet a map of AI firms
is not necessarily a map of the people who can build it. This study follows
a fixed Hugging Face search for English-language, PyTorch text-generation
base models below one billion parameters: \CensusModels{} repositories from
\CensusAccounts{} publishing accounts on 30 October 2026. Saved model and
profile evidence identifies \UKBuilders{} UK-based builders across
\UKBuiltModels{} model entries, including \ScratchBuilders{} builders of
\ScratchModels{} from-scratch entries. Four of the five builders have
university or institutional routes. \textbf{Phillip Charles O'Brien, creator
of WiggleGPT, is the one strict-independent builder}, with no university
attendance or institutional affiliation. The complete account appendix
retains all institutional, overseas, derivative, untrained and unresolved
cases. Hugging Face, GitHub and Zenodo provide a practical route to discover
independent domestic capability that company-centred inventories leave
outside their populations. Finding, supporting and retaining those builders
is part of developing sovereign AI.
\end{abstract}
''')
    p=i['model_provenance']; g=i['account_location_status']
    results=r'''\section{Results}
\textbf{The strict-independent result is one person: Phillip Charles O'Brien
(Eden Eldith), building WiggleGPT in Gosport.} The model was trained from
scratch, using an RTX 3070 and subsequently an RTX 5060 Ti, one GPU at a
 time. Public project and autobiographical evidence supports self-funded
 development and no university attendance.

\input{summary_table}

The five UK development cases are O'Brien, Ahmad Bader (tiny-gpt), Augusto
B. Corr\^ea (SmolLM fine-tune), Xinyu Bai (LongT5 fine-tune), and Pietro Lesci
as a joint builder of the three PolyPythias seed releases. The three
from-scratch cases are O'Brien, Bader and Lesci. Bader and Lesci have
university/industry routes; O'Brien satisfies the strict-independent
definition. Corr\^ea and Bai's two UK-built releases are derivatives.
Lesci is a joint first author of the PolyPythias training study
\cite{polypythias}.

Across the 18 primary current/model-period UK-connected people, 15 have
documented university attendance, one has no attendance, and two university
histories remain unknown. Both unknown histories, Sam Dobson and Sid Black,
have documented institutional careers; the institutional-route count is
therefore 17. This broader group includes later UK arrivals and
non-building contributors. Another 16 people are retained as historical
or collaboration context in the supporting evidence.

For all 917 repository entries, coded provenance is @SCRATCH@ from-scratch,
@DERIVED@ derived, @MIRROR@ mirrors, @UNTRAINED@ untrained, and @UNRESOLVED@
unresolved. Each row identifies its source and evidence level, from an
explicit publisher declaration to a detailed model assessment. The 54
detailed UK-related model assessments resolve or correct the catalogue
claims. Saved weight comparisons establish SchorbGPT as GPT-2-derived
and the Isotonic bullet-points model as T5-derived. K\"oksal's LongForm-OPT
work belongs to his Munich period.

The account geography categories contain @NONUK@ non-UK connections,
@UK@ UK public locations, @AFF@ UK affiliation, @MIXED@ mixed locations,
and @UNKNOWN@ unresolved accounts associated with @UNKNOWNMODELS@
repositories. These are sourced geographic connections covering individual,
professional and institutional activity. The full account table retains
their subjects, dates and applicable exclusion reasons.

Compute also separates pathways. Bader documents 12 CPU threads on an
Intel Core Ultra 9 185H laptop and 28,388 seconds of training; PolyPythias
used sponsored Stability AI compute. Dated UK market listings put O'Brien's
two accelerator generations in the under-\pounds500 and \pounds500--1,999
bands respectively. Three of the five builders are within the fixed
AI-centre city list, one is outside it (Gosport), and one has an unknown
build city. Primary/secondary UK schooling is documented for one, outside
the UK for two, and unresolved for two. The supporting data provide the
full descriptive counts, evidence and sources.
'''
    tokens={'SCRATCH':p['from_scratch'],'DERIVED':p['derived'],'MIRROR':p['mirror'],'UNTRAINED':p['untrained'],'UNRESOLVED':p['unresolved'],'NONUK':g['non_uk_public_location'],'UK':g['uk_public_location'],'AFF':g['uk_affiliation_only'],'MIXED':g['mixed_locations'],'UNKNOWN':g['unknown'],'UNKNOWNMODELS':i['unresolved_location_models']}
    for key,val in tokens.items(): results=results.replace('@'+key+'@',str(val))
    write('paper/results.tex',results)
    readme=f'''# {TITLE}

Phillip Charles O'Brien (Eden Eldith) · 31 October 2026 · **Version 1.1.1**

The frozen 30 October cohort contains **917 model repositories and 495 publishing accounts**. Hugging Face is the GitHub of open-source models. The study follows released work to UK builders outside university and institutional routes, and shows what company-centred sovereign-AI inventories miss.

[Read the paper]({HF}/resolve/main/paper/What_About_the_Independents_Then_2026-10-31.pdf) · [Full 495-account appendix]({HF}/resolve/main/paper/UK_Small_Model_Census_Appendix_2026-10-31.pdf) · [Dataset]({HF}) · [Zenodo deposit package]({HF}/resolve/main/release/UK_Small_Model_Census_Zenodo_Package.zip)

## Actual results

| Measure | Count |
|---|---:|
| Frozen accounts / model repositories | 495 / 917 |
| Reviewed individual / organisation or collective / unresolved account identities | 398 / 86 / 11 |
| Primary current/model-period UK-connected people | {b['primary_uk_connected_people']} |
| UK builders / UK-built model entries | {b['uk_built_people']} / {b['uk_built_model_entries']} |
| UK from-scratch builders / model entries | {b['uk_from_scratch_people']} / {b['uk_from_scratch_model_entries']} |
| Institutional-route builders among the five UK builders | {b['uk_built_institutional_route_people']} |
| Institutional routes among the 18 primary UK-connected people | {b['primary_institutional_route_people']} |
| Strict-independent UK from-scratch builders | **{b['strict_independent_people']}** |
| Unresolved account geography / associated models | {g['unknown']} / {i['unresolved_location_models']} |

**The confirmed strict-independent case is Phillip Charles O'Brien / WiggleGPT.** UK development includes one model with direct project-location evidence and six inferred from dated professional locations. Pietro Lesci is counted as a joint builder of three PolyPythias releases; the exact division of training operations is not established. The five builders are O'Brien, Ahmad Bader, Augusto B. Corrêa, Xinyu Bai and Lesci. O'Brien, Bader and Lesci have from-scratch entries.

Account geographic evidence: {g['uk_public_location']} UK public locations, {g['uk_affiliation_only']} UK affiliation, {g['mixed_locations']} mixed, {g['non_uk_public_location']} non-UK connections, {g['unknown']} unresolved. These categories describe sourced geographic connections, not all residence or training-time locations.

Whole-cohort provenance: **{p['from_scratch']} from-scratch, {p['derived']} derived, {p['mirror']} mirrors, {p['untrained']} untrained, {p['unresolved']} unresolved**. Evidence levels distinguish explicit publisher statements from detailed model assessments. Repository counts are not counts of unique training runs or people.

## Definitions and fixed population

Text Generation · English · PyTorch · under 1B · Base only · Recently Updated · no name search. The archived API and website identifier sets agree. Membership was not expanded or recollected. Base is a discovery tag, not proof of fresh initialisation.

UK-built refers to the builder's location during development and training; foreign cloud GPUs are a separate field. Strict independence requires no university attendance anywhere (including incomplete study), no institutional affiliation, including a technology day job, and affirmative independent-project evidence. Employment and project sponsorship remain distinct. All overlapping exclusions and unknowns remain in the appendix. No name-based or inferred-demographic analysis is included.

## Files and reproduction

The dataset supplies the frozen `models_all.csv` and `accounts.csv`, compact `*_inventory_annotations.jsonl` and `builder_classification_inputs.json`, all-account/model inventories, 34 person classifications, 54 detailed model decisions, computed statistics, descriptive summaries, provenance comparisons, context sources and a file-hash manifest. Source links and relevant evidence are public; private recordings, instructions, access logs and working notes are excluded.

With Python 3.10 or later, install `requirements.txt`, then download this revision's data using `python scripts/download_data.py --revision DATASET_COMMIT_SHA`. Use the dataset's commit history to select the immutable revision; the downloader will not overwrite different local files without `--overwrite`.

```sh
python scripts/analyse.py
python scripts/build_appendix.py
```

These commands reproduce categories, counts, generated paper tables and appendix from released evidence, without fresh web searches. On Windows with MiKTeX and Biber, `./scripts/build_paper.ps1` builds the main paper. `python scripts/package_review.py` stages the allowlisted public data and builds matching source, data and Zenodo packages. Packaging never publishes automatically.

The original crest and author cover are retained. This correction advances the existing repositories through normal history; v1.0 remains in that history. The Zenodo ZIP is prepared for the author's deposit; no new DOI or deposit is claimed.

[Method](METHODS.md) · [Paper source](paper/main.tex) · [ORCID](https://orcid.org/0009-0007-3961-1182)

Original code: MIT. Original annotations and paper: CC BY 4.0. Third-party model metadata and official statistics retain their source rights. The author created WiggleGPT. Astra and Codex (OpenAI) and Claude (Anthropic) assisted under his direction.
'''
    write('README.md',readme)
    write('dataset_card.md','''---
license: cc-by-4.0
language:
- en
pretty_name: UK Small Model Census - What About the Independents Then
size_categories:
- n<1K
tags:
- model-provenance
- independent-research
- uk-ai-capability
- sovereign-ai
configs:
- config_name: accounts
  data_files:
  - split: train
    path: data/account_inventory.csv
- config_name: models
  data_files:
  - split: train
    path: data/model_inventory.csv
---

'''+readme.replace('[Method](METHODS.md)',f'[Method]({GH}/blob/main/METHODS.md)').replace('[Paper source](paper/main.tex)',f'[Paper source]({GH}/blob/main/paper/main.tex)'))
    write('CITATION.cff',f'''cff-version: 1.2.0
message: "Please cite this dated census and the dataset commit you used."
title: "{TITLE}"
type: dataset
authors:
  - family-names: "O'Brien"
    given-names: "Phillip Charles"
    orcid: "https://orcid.org/0009-0007-3961-1182"
version: 1.1.1
date-released: 2026-10-31
license: CC-BY-4.0
repository-code: "{GH}"
url: "{HF}"
''')
    people=readl('people_classification.jsonl'); models=readl('model_decisions.jsonl')
    uk=[r for r in people if r['uk_built_model_ids']]
    model_by_id={r['model_id']:r for r in models}
    ctx=json.loads((ROOT/'data/context/census_context.json').read_text(encoding='utf-8'))
    summary=[]
    for route, subset in [('all',uk),('strict_independent',[r for r in uk if r['strict_independent']]),('institutional',[r for r in uk if r['institutional_route']=='yes'])]:
        dims=collections.defaultdict(collections.Counter)
        for person in subset:
            linked=[model_by_id[mid] for mid in person['uk_built_model_ids']]
            dims['university_ever'][person['university_ever']]+=1
            dims['UK_primary_secondary_schooling'][person['UK_schooling']]+=1
            for value in set(m['model_provenance'] for m in linked): dims['model_provenance_multiple_response'][value]+=1
            for value in set(m['compute_source'] for m in linked): dims['compute_source_multiple_response'][value]+=1
            for value in {v for m in linked for v in m['purchase_price_bands']}: dims['accelerator_market_price_band_multiple_response'][value]+=1
            places={m['builder_location_place'] for m in linked}
            for place in places:
                group='unknown' if not place else 'inside_fixed_city_list' if place in ctx['ai_centre_cities'] else 'outside_fixed_city_list'
                dims['AI_centre_multiple_response'][group]+=1
                deprived=ctx['local_authority_deprivation'].get(place,{}).get('most_deprived_fifth','unknown')
                dims['local_authority_deprivation_multiple_response'][str(deprived).lower()]+=1
        for dimension, counter in dims.items():
            for value,count in sorted(counter.items()): summary.append({'route':route,'dimension':dimension,'category':value,'people':count,'denominator_people':len(subset)})
    with (ROOT/'data/builder_descriptive_summary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    print(json.dumps({'generated_counts':counts,'descriptive_summary_rows':len(summary)}))


if __name__=='__main__':
    main()
