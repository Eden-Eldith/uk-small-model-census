# Method for the 1 November 2026 correction

The frozen 30 October 2026 query returned 917repositories from 495accounts. Text Generation, English, PyTorch, the displayed under-1B range, Base only and Recently Updated were selected with no name query. The original website/API sets agree and every original identifier remains. We do not replace the cohort with a live search.

## Classify saved evidence first

Existing metadata, model cards, profiles, dated biographies and the saved follow-through batches supply the classification inputs. Organisational publishers and explicitly derived or untrained models are categorised directly. Existing findings settle answered fields; additional research follows the remaining questions.

The account follow-through covered all 151 previously unresolved accounts. The first 34 completed investigations were retained. Three agents divided the remaining 117 accounts, starting with each frozen model's card and community discussion, then reading the creator's profile and linked social, personal and GitHub pages. The time ceiling was three minutes per account. A final targeted discovery pass followed the remaining unanswered country and origin fields, including exact creator-name/handle searches and previously unread linked pages. Missing raw-file responses were followed through the rendered file page at the same frozen revision. Previously settled biographies and model investigations were reused. The current follow-through supplies 66 country assessments (23 high, 26 medium and 17 low confidence), with 9 region/timezone-only clues and 75 geographically unresolved accounts.

The public account and model annotations record the source basis and evidence level, including publisher declarations, model-specific training evidence, exact-file comparisons and labelled inferences. The resulting model classifications are 457 from scratch, 352 derived, 36 mirrors, 60 untrained and 12 unresolved. Of the 457 from-scratch classifications, 154 use labelled origin inferences. Original training, inherited architecture or code, upstream checkpoints and subsequent modifications are separate fields. A developer's own from-scratch lineage is retained when a final released checkpoint is a later derivative. The saved GPT-2/T5 comparisons and exact weight-file identifiers supply model-specific evidence where presentation conflicts with the files.

## People, builder locations and routes

Accounts, individuals and models have different denominators. Attributable cross-links are used for the 35-person detailed evidence set; account display names and aliases are not assumed to identify 454 unique people. The 19 primary UK-connected people include contributors and later UK arrivals; they are not all UK builders.

UK-built follows the builder's location during the model-development period. Overseas compute is recorded separately. Direct project-location statements and inferences from dated professional/study locations are separately coded. 6 of the 7 identified UK-built entries use dated-location inference. A current profile by itself cannot date an old run. Collaborative model development includes Pietro Lesci's joint-first-author role in PolyPythias; the exact division of training operations is not established.

University-ever means any attendance, completed or not, anywhere. Institutional affiliation includes relevant university, laboratory or employer/industry routes, including a technology day job when the model is a home project. It is separate from affiliation at build time, model-specific backing, funding and supplied compute. Of the 3 university-unknown primary people, 2 have established institutional careers. Strict independence requires a UK-built from-scratch natural-language model, never attending university, no institutional affiliation, and affirmative independent-project evidence. Missing funding or education statements do not establish independence.

Every account remains in the appendix with all applicable exclusion and unresolved reasons. An institution's headquarters does not establish every collaborator's residence. Current overseas geography also need not be converted into historical build geography when an already-settled exclusion makes that investigation irrelevant.

## Descriptive context

The saved 30 October hardware bands are retained: under GBP 500; GBP 500–1,999; GBP 2,000–9,999; GBP 10,000–99,999; GBP 100,000+. Dated market prices are not the author's original purchase costs. Sequential replacement GPUs are not summed into a simultaneous array; unpriced or unspecified hardware remains unknown. Rented or sponsored compute is distinguished from owned devices.

The fixed city list is Cambridge, Oxford, Greater London, Southampton, Bristol, Edinburgh, Leeds and Manchester, from the cited official UK Technology 2024 brochure. Area deprivation uses the most-deprived fifth of local authorities in the relevant nation's index, by rank of average score. Only supported build-time localities are used; Gosport's borough result is not a neighbourhood claim. UK primary/secondary schooling is distinct from university. Multiple-response descriptive counts retain explicit denominators and unknown categories.

The paper cites three DfE education-context rows for England's state-school 2020/21 age-15 cohort, followed to age 19 in 2024/25. No name-character, name-origin or inferred-demographic analysis is included. Earlier local demographic materials are historical working material and are excluded from this release.

## Reproduce and publish

`python scripts/analyse.py` runs builder classification, full inventory classification and derived counts/documents from released evidence inputs, without network access. `python scripts/build_appendix.py` builds all 495 account rows; `./scripts/build_paper.ps1` compiles the original-crest LaTeX manuscript. `python scripts/package_review.py` uses explicit file lists to construct matching public data, source and Zenodo packages. Private transcripts, notes, instructions and access logs remain local. The original public version remains in repository history. Zenodo deposition is author-managed; building the package does not assign a DOI.
