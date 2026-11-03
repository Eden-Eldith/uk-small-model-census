"""Generate paper totals and public release documentation from counted evidence."""
import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'What About the Independents Then: Investigating Small Large Language Models in the UK'
HF = 'https://huggingface.co/datasets/edeneldith/uk-small-model-census'
GH = 'https://github.com/Eden-Eldith/uk-small-model-census'
VERSION = '1.2.1'
RELEASE_DATE = '2026-11-03'
RELEASE_DATE_TEXT = '3 November 2026'


def readl(name):
    return [json.loads(x) for x in (ROOT/'data'/name).read_text(encoding='utf-8').splitlines() if x.strip()]


def write(name, value):
    (ROOT/name).write_text(value, encoding='utf-8')


def main():
    i = json.loads((ROOT/'data/inventory_statistics.json').read_text(encoding='utf-8'))
    b = json.loads((ROOT/'data/builder_statistics.json').read_text(encoding='utf-8'))
    people = readl('people_classification.jsonl')
    models = readl('model_decisions.jsonl')
    inventory_models = readl('model_inventory.jsonl')
    accounts = readl('account_inventory.jsonl')
    p = i['model_provenance']
    g = i['account_geographic_assessments']
    followthrough = [r['recursive_location_estimate'] for r in accounts if r.get('recursive_location_estimate')]
    country_estimates = [r for r in followthrough if r.get('best_country_estimate')]
    country_confidence = collections.Counter(str(r.get('estimate_confidence', 'not_established')).lower() for r in country_estimates)
    inferred_models = [r for r in inventory_models if r.get('origin_assessment_type') == 'inferred']
    inferred_scratch = sum(r['model_provenance'] == 'from_scratch' for r in inferred_models)
    location_evidence = b['uk_built_model_location_evidence']
    primary_university = b['primary_university_ever']
    unknown_university_names = ', '.join(r['name'] for r in people
        if r['analysis_scope'] == 'primary_uk_connection' and r['university_ever'] == 'unknown')
    trained = i['trained_status']
    lineage = i['own_from_scratch_lineage']
    uk = [r for r in people if r['uk_built_model_ids']]
    model_by_id = {r['model_id']: r for r in models}
    ctx = json.loads((ROOT/'data/context/census_context.json').read_text(encoding='utf-8'))
    city_groups = collections.Counter()
    for person in uk:
        places = {model_by_id[mid]['builder_location_place'] for mid in person['uk_built_model_ids']}
        city_groups.update({'unknown' if not place else 'inside' if place in ctx['ai_centre_cities'] else 'outside' for place in places})
    schooling = b['uk_built_schooling']
    counts = {'CensusVersion': VERSION, 'CensusRevisionDate': RELEASE_DATE_TEXT,
              'CensusModels': i['frozen_models'], 'CensusAccounts': i['frozen_accounts'],
              'UKBuilders': b['uk_built_people'], 'UKBuiltModels': b['uk_built_model_entries'],
              'ScratchBuilders': b['uk_from_scratch_people'], 'ScratchModels': b['uk_from_scratch_model_entries'],
              'StrictBuilders': b['strict_independent_people'], 'UKInstitutional': b['uk_built_institutional_route_people'],
              'PrimaryPeople': b['primary_uk_connected_people'], 'PrimaryInstitutional': b['primary_institutional_route_people'],
              'StrictModels': b['strict_independent_model_entries'],
              'HistoricalContextPeople': b['historical_or_collaboration_context_people'],
              'PrimaryUniversityYes': primary_university.get('yes', 0),
              'PrimaryUniversityNo': primary_university.get('no', 0),
              'PrimaryUniversityUnknown': primary_university.get('unknown', 0),
              'DirectUKBuildModels': location_evidence.get('direct_public_statement', 0),
              'InferredUKBuildModels': location_evidence.get('dated_location_inference', 0),
              'DetailedModelAssessments': len(models), 'ReviewedPeople': len(people),
              'ScratchInventoryModels': p.get('from_scratch', 0),
              'DerivedInventoryModels': p.get('derived', 0), 'MirrorInventoryModels': p.get('mirror', 0),
              'UntrainedInventoryModels': p.get('untrained', 0),
              'UnresolvedProvenanceModels': p.get('unresolved', 0),
              'InferredProvenanceModels': len(inferred_models), 'InferredScratchModels': inferred_scratch,
              'UnresolvedTrainingModels': trained.get('unknown', 0) + trained.get('not_documented', 0),
              'EstimatedTrainedModels': trained.get('probably_yes', 0),
              'UnresolvedOwnScratchLineageModels': lineage.get('unknown', 0),
              'PartialOwnScratchLineageModels': lineage.get('partial', 0),
              'InsideAICentreBuilders': city_groups['inside'], 'OutsideAICentreBuilders': city_groups['outside'],
              'UnknownBuildCityBuilders': city_groups['unknown'],
              'UKSchoolingBuilders': schooling.get('yes', 0), 'NonUKSchoolingBuilders': schooling.get('no', 0),
              'UnknownSchoolingBuilders': schooling.get('unknown', 0),
              'UKSourceConnectionAccounts': g.get('uk_source_connection', 0),
              'UKEstimateAccounts': g.get('uk_estimate', 0),
              'UKAffiliationAccounts': g.get('uk_affiliation_only', 0),
              'MixedConnectionAccounts': g.get('mixed_connections', 0),
              'NonUKConnectionOrEstimateAccounts': g.get('non_uk_connection_or_estimate', 0),
              'RegionClueAccounts': g.get('region_or_timezone_clue', 0),
              'UnresolvedGeographyAccounts': g.get('unresolved', 0),
              'UnresolvedGeographyModels': i['unresolved_geography_models'],
              'FollowthroughAccounts': len(followthrough), 'CountryEstimateAccounts': len(country_estimates),
              'HighCountryEstimateAccounts': country_confidence.get('high', 0),
              'MediumCountryEstimateAccounts': country_confidence.get('medium', 0),
              'LowCountryEstimateAccounts': country_confidence.get('low', 0),
              'UnknownAccounts': g.get('unresolved', 0), 'UnknownAccountModels': i['unresolved_geography_models']}
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
Strict-independent UK from-scratch development & \StrictBuilders{} person & \StrictModels{} \\
UK source connections / UK estimates & \UKSourceConnectionAccounts{} / \UKEstimateAccounts{} accounts & -- \\
UK affiliation only / mixed connections & \UKAffiliationAccounts{} / \MixedConnectionAccounts{} accounts & -- \\
Non-UK connections or estimates & \NonUKConnectionOrEstimateAccounts{} accounts & -- \\
Region or timezone clues & \RegionClueAccounts{} accounts & -- \\
Unresolved account geography & \UnresolvedGeographyAccounts{} accounts & \UnresolvedGeographyModels{} \\
Unresolved model provenance & -- & \UnresolvedProvenanceModels{} \\
\bottomrule
\end{tabularx}
\caption{Account, person and model denominators remain distinct. UK development includes \InferredUKBuildModels{} entries inferred from dated professional locations and \DirectUKBuildModels{} with direct project-location evidence. Country estimates retain their confidence and source basis in the appendix. Rows overlap.}
\label{tab:counts}
\end{table}
'''
    for key, val in [('IND',i['account_identity_classes']['individual']),('ORG',i['account_identity_classes']['organisation_or_collective']),('ENTITYUNKNOWN',i['account_identity_classes']['unresolved_entity_type'])]:
        table=table.replace('@'+key+'@',str(val))
    write('paper/summary_table.tex',table)
    write('paper/abstract.tex',r'''\begin{abstract}
The United Kingdom is investing in sovereign AI, yet a map of AI firms
is not necessarily a map of the people who can build it. I follow
a fixed Hugging Face search for English-language, PyTorch text-generation
base models below one billion parameters: \CensusModels{} repositories from
\CensusAccounts{} publishing accounts on 30 October 2026. From saved model and
profile evidence, I identify \UKBuilders{} UK-based builders across
\UKBuiltModels{} model entries, including \ScratchBuilders{} builders of
\ScratchModels{} from-scratch entries. \UKInstitutional{} of the \UKBuilders{} builders have
university or institutional routes. \textbf{I am the one identified
strict-independent builder, having developed WiggleGPT in Gosport}, with no university
attendance or institutional affiliation. The complete account appendix
retains all institutional, overseas, derivative, untrained and unresolved
cases. Hugging Face, GitHub and Zenodo provide a practical route to discover
independent domestic capability that company-centred inventories leave
outside their populations. Finding, supporting and retaining those builders
is part of developing sovereign AI. I connect this discovery failure to
the race through recursive self-improvement (RSI), artificial general
intelligence and artificial superintelligence: who builds successive
generations determines who controls the resulting capability. The 2026
Hugging Face security incident demonstrates why access to hosted models
can fail during an emergency. Britain needs domestic capacity to build,
improve and operate models, alongside the ability to find and support the
people doing that work.
\end{abstract}
''')
    results=r'''\section{Results}
\textbf{The strict-independent result is one person: me, building WiggleGPT
in Gosport.} I trained the model from scratch, using an RTX 3070 and
subsequently an RTX 5060 Ti, one GPU at a time. My public project record and
autobiographical account document self-funded development and no university attendance.

\input{summary_table}

The UK development cases are me (WiggleGPT), Ahmad Bader (tiny-gpt), Augusto
B. Corr\^ea (SmolLM fine-tune), Xinyu Bai (LongT5 fine-tune), and Pietro Lesci
as a joint builder of the three PolyPythias seed releases. The
from-scratch cases are Bader, Lesci and me. Bader and Lesci have
university/industry routes; I satisfy the strict-independent
definition. Corr\^ea and Bai's two UK-built releases are derivatives.
Lesci is a joint first author of the PolyPythias training study
\cite{polypythias}.

Across the \PrimaryPeople{} primary current/model-period UK-connected people, \PrimaryUniversityYes{} have
documented university attendance, \PrimaryUniversityNo{} has no attendance, and \PrimaryUniversityUnknown{} university
histories remain unknown: @UNKNOWNUNINAMES@. Institutional careers are
recorded separately; the institutional-route count is
\PrimaryInstitutional{}. This broader group includes later UK arrivals and
non-building contributors. Another \HistoricalContextPeople{} people are retained as historical
or collaboration context in the supporting evidence.

For all \CensusModels{} repository entries, coded provenance is @SCRATCH@ from-scratch,
@DERIVED@ derived, @MIRROR@ mirrors, @UNTRAINED@ untrained, and @UNRESOLVED@
unresolved. Each row identifies its source and evidence level, from an
explicit publisher declaration to a supported origin inference or detailed
model assessment. \InferredProvenanceModels{} entries use labelled
origin inferences; \InferredScratchModels{} of
the from-scratch classifications use those inferences. Confidence and the
specific training or lineage basis remain attached to each inference. The \DetailedModelAssessments{}
detailed UK-related model assessments resolve or correct the catalogue
claims. Saved weight comparisons establish SchorbGPT as GPT-2-derived
and the Isotonic bullet-points model as T5-derived. K\"oksal's LongForm-OPT
work belongs to his Munich period.

The updated account geography categories contain
\UKSourceConnectionAccounts{} UK source connections,
\UKEstimateAccounts{} UK estimates, \UKAffiliationAccounts{} UK affiliation-only
cases, \MixedConnectionAccounts{} mixed connections,
\NonUKConnectionOrEstimateAccounts{} non-UK connections or estimates, and
\RegionClueAccounts{} region or timezone clues.
\UnresolvedGeographyAccounts{} accounts associated with
\UnresolvedGeographyModels{} repositories remain geographically unresolved.
The follow-through of \FollowthroughAccounts{} accounts supplies
\CountryEstimateAccounts{} country assessments: \HighCountryEstimateAccounts{}
high, \MediumCountryEstimateAccounts{} medium and \LowCountryEstimateAccounts{}
low confidence. An estimate retains its confidence and stated basis;
regional evidence retains its region. The full account table records
the subject and date of each connection, current-base estimate and
model-period inference, alongside applicable exclusion reasons.

Compute also separates pathways. Bader documents 12 CPU threads on an
Intel Core Ultra 9 185H laptop and 28,388 seconds of training; PolyPythias
used sponsored Stability AI compute. Dated UK market listings put my
two accelerator generations in the under-\pounds500 and \pounds500--1,999
bands respectively. \InsideAICentreBuilders{} of the \UKBuilders{} builders are within the fixed
AI-centre city list, \OutsideAICentreBuilders{} is outside it (Gosport), and
\UnknownBuildCityBuilders{} has an unknown build city. Primary/secondary UK
schooling is documented for \UKSchoolingBuilders{}, outside the UK for
\NonUKSchoolingBuilders{}, and unresolved for \UnknownSchoolingBuilders{}.
The supporting data provide the
full descriptive counts, evidence and sources.
'''
    tokens={'SCRATCH':p['from_scratch'],'DERIVED':p['derived'],'MIRROR':p['mirror'],'UNTRAINED':p['untrained'],'UNRESOLVED':p['unresolved']}
    results=results.replace('@UNKNOWNUNINAMES@',unknown_university_names)
    for key,val in tokens.items(): results=results.replace('@'+key+'@',str(val))
    write('paper/results.tex',results)
    readme=f'''# {TITLE}

Phillip Charles O'Brien (Eden Eldith) · {RELEASE_DATE_TEXT} · **Version {VERSION}**

**Review draft.** These repositories record work in progress for author review. The paper, appendix and package are synchronised here; formal release and Zenodo deposit await the author's approval.

The frozen 30 October cohort contains **{i['frozen_models']} model repositories and {i['frozen_accounts']} publishing accounts**. Hugging Face is the GitHub of open-source models. The study follows released work to UK builders outside university and institutional routes, and shows what company-centred sovereign-AI inventories miss. Britain needs to discover, support and retain the people who already build domestic models; a company inventory leaves independent work outside its starting population.

The paper argues that the race through recursive self-improvement (RSI), AGI and ASI makes domestic model-building urgent: Britain must become a producer or risk becoming a vassal state dependent on other powers. It examines the 2026 Hugging Face intrusion and the responders' blocked access to hosted-model analysis as a concrete failure of operational independence. It connects that evidence to the limits of the National Security Strategy's baseline ambition, active defence, talent retention and a national model-building programme. Practical proposals include regional compute, distributed training, learning routes and apprenticeships with a stake in inventions.

[Read the paper]({HF}/resolve/main/paper/What_About_the_Independents_Then_2026-10-31.pdf) · [Full {i['frozen_accounts']}-account appendix]({HF}/resolve/main/paper/UK_Small_Model_Census_Appendix_2026-10-31.pdf) · [Dataset]({HF}) · [Zenodo deposit package]({HF}/resolve/main/release/UK_Small_Model_Census_Zenodo_Package.zip)

## Actual results

| Measure | Count |
|---|---:|
| Frozen accounts / model repositories | {i['frozen_accounts']} / {i['frozen_models']} |
| Reviewed individual / organisation or collective / unresolved account identities | {i['account_identity_classes']['individual']} / {i['account_identity_classes']['organisation_or_collective']} / {i['account_identity_classes']['unresolved_entity_type']} |
| Primary current/model-period UK-connected people | {b['primary_uk_connected_people']} |
| UK builders / UK-built model entries | {b['uk_built_people']} / {b['uk_built_model_entries']} |
| UK from-scratch builders / model entries | {b['uk_from_scratch_people']} / {b['uk_from_scratch_model_entries']} |
| Institutional-route builders among the {b['uk_built_people']} UK builders | {b['uk_built_institutional_route_people']} |
| Institutional routes among the {b['primary_uk_connected_people']} primary UK-connected people | {b['primary_institutional_route_people']} |
| Strict-independent UK from-scratch builders | **{b['strict_independent_people']}** |
| UK source connections / UK estimates | {g.get('uk_source_connection', 0)} / {g.get('uk_estimate', 0)} |
| UK affiliation only / mixed connections | {g.get('uk_affiliation_only', 0)} / {g.get('mixed_connections', 0)} |
| Non-UK connections or estimates | {g.get('non_uk_connection_or_estimate', 0)} |
| Region or timezone clues | {g.get('region_or_timezone_clue', 0)} |
| Unresolved account geography / associated models | {g.get('unresolved', 0)} / {i['unresolved_geography_models']} |

**The confirmed strict-independent case is Phillip Charles O'Brien / WiggleGPT.** UK development includes {location_evidence.get('direct_public_statement', 0)} model with direct project-location evidence and {location_evidence.get('dated_location_inference', 0)} inferred from dated professional locations. Pietro Lesci is counted as a joint builder of three PolyPythias releases; the exact division of training operations is not established. The builders are O'Brien, Ahmad Bader, Augusto B. Corrêa, Xinyu Bai and Lesci. O'Brien, Bader and Lesci have from-scratch entries.

The geographic table uses the updated account assessments. The legacy source-location category remains in the data as source history. Follow-through of {len(followthrough)} formerly unanswered accounts supplies {len(country_estimates)} country assessments: {country_confidence.get('high', 0)} high, {country_confidence.get('medium', 0)} medium and {country_confidence.get('low', 0)} low confidence. Country estimates remain estimates with their confidence and source basis; region-only evidence retains the region. Builder location during training is recorded separately.

Whole-cohort provenance: **{p['from_scratch']} from-scratch, {p['derived']} derived, {p['mirror']} mirrors, {p['untrained']} untrained, {p['unresolved']} unresolved**. Labelled origin inferences cover {len(inferred_models)} entries, including {inferred_scratch} of the from-scratch classifications. Each inference retains its confidence and source basis, alongside explicit publisher statements and detailed model assessments. Repository, training-run and person counts remain separate.

## Definitions and fixed population

Text Generation · English · PyTorch · under 1B · Base only · Recently Updated · no name search. The archived API and website identifier sets agree. Membership was not expanded or recollected. Base is a discovery tag, not proof of fresh initialisation.

UK-built refers to the builder's location during development and training; foreign cloud GPUs are a separate field. Strict independence requires no university attendance anywhere (including incomplete study), no institutional affiliation, including a technology day job, and affirmative independent-project evidence. Employment and project sponsorship remain distinct. All overlapping exclusions and unknowns remain in the appendix. No name-based or inferred-demographic analysis is included.

## Files and reproduction

The dataset supplies the frozen `models_all.csv` and `accounts.csv`, compact `*_inventory_annotations.jsonl` and `builder_classification_inputs.json`, all-account/model inventories, {len(people)} person classifications, {len(models)} detailed model decisions, computed statistics, descriptive summaries, provenance comparisons, context sources and a file-hash manifest. Source links and relevant evidence are public; private recordings, instructions, access logs and working notes are excluded.

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
'''
    write('README.md',readme)
    method_path = ROOT/'METHODS.md'
    method = method_path.read_text(encoding='utf-8')
    followthrough_text = f'''The account follow-through covered all 151 previously unresolved accounts. The first 34 completed investigations were retained. Three agents divided the remaining 117 accounts, starting with each frozen model's card and community discussion, then reading the creator's profile and linked social, personal and GitHub pages. The time ceiling was three minutes per account. A final targeted discovery pass followed the remaining unanswered country and origin fields, including exact creator-name/handle searches and previously unread linked pages. Missing raw-file responses were followed through the rendered file page at the same frozen revision. Previously settled biographies and model investigations were reused. The current follow-through supplies {len(country_estimates)} country assessments ({country_confidence.get('high',0)} high, {country_confidence.get('medium',0)} medium and {country_confidence.get('low',0)} low confidence), with {g.get('region_or_timezone_clue',0)} region/timezone-only clues and {g.get('unresolved',0)} geographically unresolved accounts.\n\n'''
    method = re.sub(r'The account follow-through covered.*?(?=The public account)', lambda _:followthrough_text, method, count=1, flags=re.S)
    provenance_text = f'''The public account and model annotations record the source basis and evidence level, including publisher declarations, model-specific training evidence, exact-file comparisons and labelled inferences. The resulting model classifications are {p['from_scratch']} from scratch, {p['derived']} derived, {p['mirror']} mirrors, {p['untrained']} untrained and {p['unresolved']} unresolved. Of the {p['from_scratch']} from-scratch classifications, {inferred_scratch} use labelled origin inferences. Original training, inherited architecture or code, upstream checkpoints and subsequent modifications are separate fields. A developer's own from-scratch lineage is retained when a final released checkpoint is a later derivative. The saved GPT-2/T5 comparisons and exact weight-file identifiers supply model-specific evidence where presentation conflicts with the files.\n\n'''
    method = re.sub(r'The public account.*?(?=## People)', lambda _:provenance_text, method, count=1, flags=re.S)
    method = re.sub(r'Six of the seven identified UK-built entries use dated-location inference\.', f"{location_evidence.get('dated_location_inference',0)} of the {b['uk_built_model_entries']} identified UK-built entries use dated-location inference.", method)
    method = re.sub(r'for the \d+-person detailed evidence set', f'for the {len(people)}-person detailed evidence set', method)
    method = re.sub(r'The \d+ primary UK-connected people', f"The {b['primary_uk_connected_people']} primary UK-connected people", method)
    unknown_primary = [r for r in people if r['analysis_scope']=='primary_uk_connection' and r['university_ever']=='unknown']
    unknown_institutional = sum(r['institutional_route']=='yes' for r in unknown_primary)
    method = re.sub(r'Both university-unknown primary people have established institutional careers\.|Of the \d+ university-unknown primary people, \d+ have established institutional careers\.', f'Of the {len(unknown_primary)} university-unknown primary people, {unknown_institutional} have established institutional careers.', method)
    method = re.sub(r'The paper cites three DfE education-context rows.*?(?=## Reproduce and publish)',
        'The paper includes all 24 recorded major and detailed DfE ethnicity groups, with Male/Female and FSM/non-FSM higher-education progression rates. The released context CSV retains all 222 original observations for England state-funded and special-school pupils aged 15 in 2020/21, followed to age 19 in 2024/25. A comparison CSV preserves each rate, pupil denominator and HE entrant count, including the recorded Unknown-sex observation. Major subtotals and detailed groups are labelled separately. FSM is the recorded eligibility indicator at age 15; non-FSM is All Other Pupils. Working-class disadvantage extends beyond FSM eligibility. These are official aggregate educational statistics; the census retains its separate university/institutional-route fields.\n\n',
        method,count=1,flags=re.S)
    write('METHODS.md',method)
    changelog_section=f'''## {VERSION} — {RELEASE_DATE_TEXT}

- Revises the paper into my first-person voice and adds the authorised disability/accessibility and Sol 6.1 writing-aid disclosure.
- Increases line and paragraph spacing and restores substantive reasoning from my dictated account: networking access, practical collaboration, learning and apprenticeship routes, model-assisted model development, reciprocal research partnerships, regional compute and technical control.
- States the reasoning and practical requirements for talent discovery directly, retaining first person for my experience and aims rather than presenting the analytical argument as personal wishes.
- Restores the strategic thesis in full: winning AI, RSI, AGI and ASI; the zero-sum race for primacy; the risk of Britain becoming a vassal state; and the case for urgent national mobilisation.
- Adds the Hugging Face incident with Hugging Face, OpenAI and AISI references, connects operational dependence to the critique of baseline sovereign capability, and restores the concrete defence, active-testing, retention and safety-knowledge arguments.
- Restores the useful-model commercial argument, corpus and instruction-tuning examples, scaling rationale, reciprocal contribution, NHS/Palantir procurement contradiction and maintenance examples. Adds sources for military robotics, counter-drone systems and Gosport's mapped data centre.
- Restores exact-name versus capability search, voluntary public discoverability, discovery-budget and selection accountability, learner/school patent returns, practical hardware skills, Astra's task-training role and distributed training as a national programme.
- Restores all 222 official education observations and a complete 24-row ethnicity/sex/FSM comparison, including Black African, Caribbean and mixed-background groups, detailed Asian and White groups, totals and unknowns. Original rates, denominators and HE entrant counts are retained.
- Adds a clickable contents page, complete PDF bookmarks, table and companion-appendix shortcuts, distinct cover/front-matter page labels, and document subject, keywords and language metadata. Version/date labels use the generated release values.
- Incorporates selected wording and organisation from the author's NotebookLM voice-log draft: sovereignty as statecraft, closed institutional discovery loops, the foreign-model/domestic-builder discovery paradox, practical education from consumption to production, and a concise programme with named institutional responsibilities. Discloses NotebookLM's drafting contribution; retains the frozen cohort, established results and source-linked factual account.
- Preserves the frozen 917-model / 495-account cohort and existing classifications: {p['from_scratch']} from scratch, {p['derived']} derived, {p['mirror']} mirrors, {p['untrained']} untrained and {p['unresolved']} unresolved; {b['uk_built_people']} UK builders, {b['uk_from_scratch_people']} from-scratch builders and {b['strict_independent_people']} strict independent.
- Restores the sourced population-change and class-access argument, including Boriswave, the 2063 projection, political history and the case for developing talent among people already here. The builder dataset still has no inferred ethnicity classifications.
- Adds the Sovereign AI Fund FOI evidence, NHS legacy-system prevalence and the distinction between free reading and paid bulk corpus access.
- Adds the author's repository-metadata correction as a concrete search limitation: English and other task/library filters may hide additional UK builders. Records a possible Base/under-1B-only follow-up while preserving the frozen cohort and all reported counts.
- Integrates the voice-log source register: AlphaEvolve's model-development improvements, the UN General Assembly superintelligence statement, US strategic objectives, deterrence research, NHS and defence operational control, government AI procurement and technical continuity.
- Adds Anthropic Institute's account of AI-assisted AI development and the progression toward autonomous successor development to the recursive self-improvement argument.
- Restores the power, cooling, heat, grid, solar, regional and offshore infrastructure argument, with concrete deployment and capital-market examples. Adds the named commercial discovery databases, model-building outcomes for skills programmes, university licensing precedent, fertility data and the record of missed migration commitments.
- Synchronises the review manuscript, full account appendix and source/data/Zenodo packages as ongoing repository work. Private transcripts and working notes remain local; formal release and Zenodo deposit remain held for author approval.

'''
    previous=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    previous=re.sub(r'^# Census revision history\s*','',previous)
    previous=re.sub(r'^## '+re.escape(VERSION)+r' — .*?(?=^## |\Z)','',previous,flags=re.S|re.M)
    write('CHANGELOG.md','# Census revision history\n\n'+changelog_section+previous.lstrip())
    write('dataset_card.md','''---
license: cc-by-4.0
language:
- en
pretty_name: "'''+TITLE+'''"
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
version: {VERSION}
date-released: {RELEASE_DATE}
license: CC-BY-4.0
repository-code: "{GH}"
url: "{HF}"
''')
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
