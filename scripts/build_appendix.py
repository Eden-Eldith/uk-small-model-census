"""Build the complete, navigable 495-account companion appendix.

Reads the released compact inventory and person/model decisions. No private
research directories or live services are required. Use --help for input paths.
"""
import argparse
import collections
import csv
import html
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, LongTable, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'What About the Independents Then: Investigating Small Large Language Models in the UK'
REVISION_DATE = '1 November 2026'
TEAL = colors.HexColor('#12616A')
INK = colors.HexColor('#1B2935')
LIGHT = colors.HexColor('#EAF1F3')


def clean(value):
    return str(value if value is not None else '').translate(str.maketrans({
        '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2013': '-', '\u2014': '-',
        '\u00a0': ' ', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
    }))


def esc(value):
    return html.escape(clean(value), quote=True)


def pretty(value):
    return clean(value).replace('_', ' ')


def letter_sort_key(value):
    letters = ''.join(c for c in clean(value).casefold() if c.isalpha())
    return not bool(letters), letters


def hardware_description(value):
    if isinstance(value, (list, tuple)):
        return '; '.join(filter(None, (hardware_description(item) for item in value)))
    if isinstance(value, dict):
        if value.get('status') == 'unknown':
            return ''
        fields = []
        for key, item in value.items():
            if key in {'status', 'sources', 'source_url', 'basis', 'physical_country'}:
                continue
            description = hardware_description(item)
            if description:
                fields.append(pretty(key).capitalize() + ': ' + description)
        return '; '.join(fields)
    if isinstance(value, bool):
        return 'yes' if value else 'no'
    return clean(value)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key, value in row.items():
            if value and value[:1] in ('[', '{'):
                try:
                    row[key] = json.loads(value)
                except json.JSONDecodeError:
                    pass
    return rows


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def unique(values):
    return list(dict.fromkeys(v for v in values if v))


def link(url, label):
    if not isinstance(url, str) or not url.startswith(('https://', 'http://')):
        return esc(label)
    return f'<link href="{esc(url)}" color="#12616A">{esc(label)}</link>'


def source_links(sources, prefix='Sources', maximum=2):
    urls = unique((item.get('url') or item.get('source_url')) if isinstance(item, dict) else item for item in sources or [])
    if not urls:
        return ''
    # The complete sources and factual bases are in the released machine-readable
    # rows. These compact links provide direct navigation without unwieldy URLs.
    return '<br/><b>' + prefix + ':</b> ' + ', '.join(
        link(url, str(i)) for i, url in enumerate(urls[:maximum], 1))


def register_font():
    candidates = [
        (Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/arial.ttf',
         Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/arialbd.ttf'),
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
         Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont('Census', str(regular)))
            pdfmetrics.registerFont(TTFont('Census-Bold', str(bold)))
            pdfmetrics.registerFontFamily('Census', normal='Census', bold='Census-Bold', italic='Census', boldItalic='Census-Bold')
            return 'Census'
    return 'Helvetica'


class BookmarkParagraph(Paragraph):
    def __init__(self, text, style, key=None, title='', level=1, **kwargs):
        super().__init__(text, style, **kwargs)
        self.key, self.outline_title, self.level = key, title, level

    def split(self, avail_width, avail_height):
        parts = super().split(avail_width, avail_height)
        if parts and self.key:
            parts[0].key, parts[0].outline_title, parts[0].level = self.key, self.outline_title, self.level
        return parts

    def draw(self):
        if self.key:
            _, top = self.canv.absolutePosition(0, self.height)
            self.canv.bookmarkPage(self.key, fit='FitH', top=top)
            self.canv.addOutlineEntry(self.outline_title, self.key, level=self.level, closed=True)
        super().draw()


def account_identity(account, people, number, style, continuation=False):
    name = account['account']
    if continuation:
        return Paragraph(f'<b>{esc(name)}</b><br/>(continued)', style)
    names = sorted(unique(account.get('person_names', []) + [p['name'] for p in people]), key=letter_sort_key)
    lines = [link(account.get('profile_url', ''), name),
             f'{esc(pretty(account.get("reviewed_account_type", "unknown")))} / {esc(account.get("platform_account_type", "unknown"))}; <b>{account["model_count"]}</b>']
    if names:
        lines.append(esc('; '.join(names)))
    display = account.get('display_name')
    normalize = lambda value: ''.join(c.lower() for c in value if c.isalnum())
    if display and normalize(display) not in {normalize(v) for v in names + [name]}:
        lines.append('Display: ' + esc(display))
    return BookmarkParagraph('<br/>'.join(lines), style, f'account-{number}', f'{number}. {name}')


def model_text(model):
    text = link(model.get('model_url') or 'https://huggingface.co/' + model['model_id'], model['model_id'])
    text += '<br/><b>' + esc(pretty(model.get('model_provenance', 'unresolved'))) + '</b>'
    evidence = {'publisher_statement': 'declared', 'detailed_model_assessment': 'assessed',
                'reviewed_model_evidence': 'reviewed', 'inferred_from_saved_development_evidence': 'inferred',
                'unresolved': 'unresolved'}.get(
                    model.get('provenance_evidence_level'), pretty(model.get('provenance_evidence_level', '')))
    if evidence:
        text += '; ' + esc(evidence)
    confidence = model.get('origin_assessment_confidence') or model.get('provenance_confidence')
    if confidence:
        text += '; <b>' + esc(confidence) + ' confidence</b>'
    details = []
    for field, label in [('own_from_scratch_lineage', 'Own original lineage'),
                         ('trained_status', 'Trained'), ('checkpoint_operation', 'Operation')]:
        if model.get(field):
            details.append(label + ': ' + pretty(model[field]))
    if details:
        text += '<br/>' + esc('; '.join(details))
    if model.get('model_provenance_scope'):
        text += '<br/>' + esc(model['model_provenance_scope'])
    if model.get('provenance_basis'):
        text += '<br/><b>Basis:</b> ' + esc(model['provenance_basis'])
    sources = model.get('provenance_sources', [])
    if sources:
        first = sources[0]
        url = first.get('url') if isinstance(first, dict) else first
        text += ' ' + link(url, '[evidence]')
    return text


def geography_text(account, models, decisions, first):
    parts = []
    if first:
        estimate = account.get('recursive_location_estimate') or account.get('best_location_estimate') or {}
        country = estimate.get('best_country_estimate') or estimate.get('country')
        region = estimate.get('best_region_estimate') or estimate.get('region')
        if country or region:
            place = '; '.join(unique([estimate.get('best_city_estimate') or estimate.get('city'), region, country]))
            label = 'Best country/base' if country else 'Best region'
            confidence = estimate.get('estimate_confidence') or estimate.get('confidence')
            parts.append('<b>' + label + ':</b> ' + esc(place))
            if confidence:
                parts[-1] += '; <b>' + esc(confidence) + ' confidence</b>'
            kind = estimate.get('estimate_type') or estimate.get('direct_or_inferred')
            if kind:
                parts.append(esc(pretty(kind)))
            period = estimate.get('estimate_period') or estimate.get('period')
            if period:
                parts.append(esc(period))
            basis = estimate.get('estimate_basis') or estimate.get('basis')
            if basis:
                parts.append('<b>Basis:</b> ' + esc(basis))
            sources = account.get('recursive_location_sources') or estimate.get('sources') or account.get('location_sources', [])
            if estimate.get('source_url'):
                sources = [{'url': estimate['source_url']}] + sources
            parts[-1] += source_links(sources, 'Location sources', maximum=6)
        else:
            status_labels = {'unknown': 'not established', 'non_uk_public_location': 'non-UK connection', 'uk_public_location': 'UK public location', 'uk_affiliation_only': 'UK affiliation only', 'mixed_locations': 'mixed connections'}
            parts.append('<b>Public:</b> ' + esc(status_labels.get(account.get('location_status'), pretty(account.get('location_status', 'unknown')))))
            if account.get('location_status') != 'unknown':
                parts[-1] += '; ' + esc(account.get('public_location_country') or 'see evidence')
            subject = account.get('location_subject')
            if subject and subject not in ('unknown', 'public_geographic_connection', 'identified_individual_or_creator'):
                parts.append('Subject: ' + esc(pretty(subject)))
            sources = source_links(account.get('location_sources', [])).replace('<br/><b>Sources:</b>', '')
            if sources:
                parts[-1] += sources
    all_unknown = all(decisions.get(m['model_id'], m).get('uk_build_status', 'unknown') == 'unknown' for m in models)
    if all_unknown:
        parts.append('<b>Build:</b> unknown.')
        return '<br/>'.join(parts)
    build_signatures = {tuple(str(decisions.get(m['model_id'], m).get(k, '')) for k in ('uk_build_status', 'builder_location_place', 'builder_location_country', 'builder_location_period', 'builder_location_evidence_type')) for m in models}
    build_seen = set()
    for model in models:
        d = decisions.get(model['model_id'], model)
        signature = tuple(str(d.get(k, '')) for k in ('uk_build_status', 'builder_location_place', 'builder_location_country', 'builder_location_period', 'builder_location_evidence_type'))
        if signature in build_seen:
            continue
        build_seen.add(signature)
        status = d.get('uk_build_status', 'unknown')
        label = 'Build ' + model['model_id'].split('/', 1)[-1] if len(build_signatures) > 1 else 'Build'
        value = '<b>' + esc(label) + ':</b> UK ' + esc(status)
        if status != 'unknown':
            place = d.get('builder_location_place') or d.get('builder_location_country')
            if place:
                value += '; ' + esc(place)
        period = d.get('builder_location_period')
        if period and period not in ('unknown', 'not established'):
            value += '; ' + esc(period)
        kind = d.get('builder_location_evidence_type')
        if kind and kind != 'unresolved':
            value += '; ' + esc(pretty(kind))
        value += source_links(d.get('builder_location_sources', []), 'Build sources').replace('<br/>', ' ')
        parts.append(value)
    return '<br/>'.join(parts)


def route_text(account, models, decisions, people, first):
    parts = []
    if first:
        reasons = list(account.get('outcome_reasons', []))
        for p in people:
            item = '<b>' + esc(p['name']) + '</b>: U ' + esc(p.get('university_ever', 'unknown'))
            item += '; I ' + esc(p.get('institutional_affiliation_ever', 'unknown'))
            item += '; strict ' + ('yes' if p.get('strict_independent') else 'not included')
            item += source_links(p.get('sources', []), 'Person sources', maximum=1).replace('<br/>', ' ')
            parts.append(item)
            for reason in p.get('outcome_reasons', []):
                if not any(r == reason or r.endswith(': ' + reason) for r in reasons):
                    reasons.append(reason)
            reasons.extend('Unresolved: ' + r for r in p.get('unresolved_fields', []))
        if not people:
            uni = account.get('university_ever_by_linked_person', {})
            if uni:
                parts.append('<b>University:</b> ' + esc('; '.join(f'{k}: {v}' for k, v in uni.items())))
            for key, label in [('reported_university_ever', 'University'),
                               ('reported_institutional_affiliation_ever', 'Institutional affiliation')]:
                if account.get(key):
                    parts.append('<b>' + label + ':</b> ' + esc(account[key]))
            evidence = account.get('education_and_institution_evidence')
            if isinstance(evidence, list):
                parts.append(source_links(evidence, 'Education / institutional sources', maximum=2).removeprefix('<br/>'))
        if reasons:
            labels = {
                'documented_non_uk_geographic_connection': 'non-UK connection',
                'university_attendance_documented_for_linked_person': 'university attendance',
                'all_frozen_releases_derived_untrained_or_mirrors': 'all releases derived / untrained / mirrors',
                'organisation_or_collective_publisher': 'organisation / collective',
                'university attendance': 'university attendance',
                'institutional or industry affiliation': 'institution / industry affiliation',
                'UK natural-language model building not established': 'UK LM building unestablished',
                'UK from-scratch natural-language model building not established': 'UK scratch LM building unestablished',
                'identified contribution is not an attributable model-building role': 'contributor role, not identified builder',
            }
            concise = []
            for reason in unique(reasons):
                # Named flags above retain the per-person outcomes; shared reason
                # labels are listed once. Model-specific uncertainty stays named.
                prefix, separator, suffix = reason.partition(': ')
                key = suffix if separator and suffix in labels else reason
                concise.append(labels.get(key, pretty(key)))
            parts.append('<b>Reasons:</b> ' + '; '.join(esc(v) for v in unique(concise)))
        question = account.get('open_question', '')
        if question and question != 'Builder location at model-development time is not established unless stated in the model-level table.':
            parts.append('<b>Open:</b> ' + esc(question))
    support_seen = set()
    for model in models:
        d = decisions.get(model['model_id'])
        if d:
            support_keys = ('institutional_affiliation_at_build', 'project_backing', 'external_project_funding', 'hardware', 'compute_source', 'physical_compute_country', 'training_duration_reported')
            signature = tuple(str(d.get(k, '')) for k in support_keys)
            if signature in support_seen:
                continue
            support_seen.add(signature)
            shared = sum(tuple(str(decisions.get(m['model_id'], {}).get(k, '')) for k in support_keys) == signature for m in models)
            label = 'Listed models' if shared == len(models) else model['model_id'].split('/', 1)[-1]
            value = '<b>' + esc(label) + ':</b> build-I ' + esc(d.get('institutional_affiliation_at_build', 'unknown'))
            value += '; backing ' + esc(d.get('project_backing', 'unknown'))
            value += '; funding ' + esc(d.get('external_project_funding', 'unknown'))
            hardware = hardware_description(d.get('hardware') or model.get('compute_used') or 'unknown') or 'unknown'
            if any(word in hardware.lower() for word in ('not stated', 'not established', 'not specified', 'not documented')):
                hardware = 'unknown'
            value += '<br/><b>Compute:</b> ' + esc(hardware)
            value += '<br/>Source: ' + esc(hardware_description(d.get('compute_source')) or 'unknown') + '; country: ' + esc(hardware_description(d.get('physical_compute_country')) or 'unknown')
            if d.get('training_duration_reported'):
                value += '<br/>Training: ' + esc(hardware_description(d['training_duration_reported']))
            parts.append(value)
        elif model.get('compute_used') not in (None, '', 'unknown', 'not established'):
            raw_hardware = model['compute_used']
            hardware = hardware_description(raw_hardware)
            if not hardware:
                continue
            value = '<b>' + esc(model['model_id'].split('/', 1)[-1]) + ' compute:</b> ' + esc(hardware)
            provider = raw_hardware.get('provider') or raw_hardware.get('service') if isinstance(raw_hardware, dict) else ''
            value += '<br/>Source: ' + esc(hardware_description(model.get('compute_source') or provider) or 'unknown') + '; country: ' + esc(hardware_description(model.get('compute_country')) or 'not established')
            if model.get('training_duration_reported'):
                value += '<br/>Training: ' + esc(hardware_description(model['training_duration_reported']))
            value += source_links(model.get('compute_sources', []), 'Compute sources', maximum=4)
            parts.append(value)
    return '<br/>'.join(parts) or 'Unestablished.'


def build(args):
    accounts = read_csv(args.accounts)
    models = read_csv(args.models)
    people = read_jsonl(args.people)
    decisions = {d['model_id']: d for d in read_jsonl(args.decisions)}
    assert len(accounts) == 495 and len({a['account'] for a in accounts}) == 495
    assert len(models) == 917 and len({m['model_id'] for m in models}) == 917
    by_account = collections.defaultdict(list)
    for model in models:
        by_account[model['account']].append(model)
    people_by_account = collections.defaultdict(list)
    for person in people:
        for account in person.get('accounts', []):
            people_by_account[account].append(person)
    assert set(by_account) == {a['account'] for a in accounts}
    accounts.sort(key=lambda r: letter_sort_key(r['account']))
    font = register_font()
    styles = getSampleStyleSheet()
    body = ParagraphStyle('CensusBody', fontName=font, fontSize=7.5, leading=8.7,
                          textColor=INK, spaceAfter=0, splitLongWords=True)
    header = ParagraphStyle('CensusHeader', parent=body, fontName=font + '-Bold' if font == 'Census' else 'Helvetica-Bold', textColor=colors.white, fontSize=8.5, leading=11)
    intro = ParagraphStyle('CensusIntro', parent=body, fontSize=10, leading=14, spaceAfter=10)
    title = ParagraphStyle('CensusTitle', parent=intro, fontName=header.fontName, fontSize=23, leading=29, textColor=TEAL, spaceAfter=18)
    subheading = ParagraphStyle('CensusSubheading', parent=intro, fontName=header.fontName, fontSize=16, leading=20, spaceAfter=14)
    width, height = landscape(A4)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(args.output), pagesize=(width, height),
                          leftMargin=30, rightMargin=30, topMargin=38, bottomMargin=32,
                          title=TITLE + ' - Complete Account Appendix',
                          author="Phillip Charles O'Brien (Eden_Eldith)",
                          subject='Frozen 917-model / 495-account UK Small Model Census companion appendix')

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(TEAL)
        canvas.drawString(30, height - 23, 'WHAT ABOUT THE INDEPENDENTS THEN | COMPLETE ACCOUNT APPENDIX')
        canvas.setStrokeColor(colors.HexColor('#AFC3C7'))
        canvas.line(30, 26, width - 30, 26)
        canvas.setFillColor(INK)
        canvas.drawString(30, 15, 'Frozen cohort: 30 October 2026 | Revision: ' + REVISION_DATE + ' | 495 accounts / 917 models')
        canvas.drawRightString(width - 30, 15, str(document.page))
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id='Appendix', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer)])
    story = [Spacer(1, 10), Paragraph(TITLE, title), Paragraph('Companion appendix: all 495 publishing accounts', subheading),
             Paragraph("Phillip Charles O'Brien (Eden_Eldith)<br/>Independent researcher, Gosport, United Kingdom<br/>ORCID: " + link('https://orcid.org/0009-0007-3961-1182', '0009-0007-3961-1182') + '<br/>' + REVISION_DATE, intro),
             Paragraph('This appendix retains every account and model in the frozen Hugging Face cohort. Account and model identifiers link to the original repositories; numbered evidence links open the supporting sources. The PDF bookmarks list every account alphabetically, sorting by letters and ignoring punctuation, spaces and digits.', intro),
             Paragraph('<b>Reading the evidence.</b> Best country/base estimates show their confidence, factual basis and sources. Build-time findings carry their evidence type and dates; physical compute location is recorded separately. Model origins distinguish publisher statements from inferences based on saved development evidence, with confidence shown. Own original lineage remains visible for later training stages.', intro),
             Paragraph('<b>Strict independent:</b> UK-based from-scratch natural-language model building, no university attendance, and no institutional affiliation or backing under the study definition. Employment and university history are separate from sponsorship of the exact project. Exclusion reasons overlap; unknowns remain unknown. Organisational accounts and contextual contributors remain visible. Names are public attributions, not a demographic classification.', intro),
             Paragraph('<b>Compact fields:</b> the account column gives reviewed type / Hugging Face user-or-org type and model count. U = university attendance ever; I = institutional affiliation ever; build-I = institutional affiliation at development. "Declared" denotes a publisher statement; "inferred" denotes an inference from saved development evidence; "reviewed" or "assessed" denotes the saved model-evidence assessment. Each row links selected evidence; the dataset retains the full source list, dates, factual basis and individual reasons.', intro),
             Paragraph('Full structured evidence and the matching machine-readable tables: ' + link('https://huggingface.co/datasets/edeneldith/uk-small-model-census', 'Hugging Face dataset') + '. Method and reproducible source: ' + link('https://github.com/Eden-Eldith/uk-small-model-census', 'GitHub repository') + '.', intro)]
    if args.working_note:
        story.insert(3, Paragraph('<b>Working revision:</b> ' + esc(args.working_note), intro))
    groups = collections.OrderedDict()
    for number, account in enumerate(accounts, 1):
        letters = letter_sort_key(account['account'])[1]
        initial = letters[:1].upper()
        key = initial if initial.isalpha() and initial.isascii() else '0-9 / other'
        groups.setdefault(key, []).append((number, account))
    # Group initials follow the same letters-only key as the account ordering.
    story.append(Paragraph('<b>Jump to accounts:</b> ' + ' | '.join(
        f'<link href="#group-{i}" color="#12616A">{esc(key)} ({len(items)})</link>'
        for i, (key, items) in enumerate(groups.items())), intro))
    column_widths = [125, 218, 210, doc.width - 553]
    displayed_models = []
    story.append(PageBreak())
    rows = [[Paragraph(t, header) for t in ['Account / public people', 'Frozen models / provenance', 'Geographic evidence / build time', 'Route, support, compute and outcomes']]]
    group_rows = []
    for group_number, (letter, entries) in enumerate(groups.items()):
        group_style = ParagraphStyle('Group', parent=subheading, spaceBefore=0, spaceAfter=0, fontSize=11, leading=13)
        group_rows.append(len(rows))
        rows.append([BookmarkParagraph(f'Accounts: {esc(letter)}', group_style, f'group-{group_number}', letter, level=0), '', '', ''])
        for number, account in entries:
            account_models = sorted(by_account[account['account']], key=lambda r: letter_sort_key(r['model_id']))
            assert len(account_models) == int(account['model_count'])
            assert {m['model_id'] for m in account_models} == set(account['model_ids'])
            linked_people = sorted(people_by_account.get(account['account'], []), key=lambda p: letter_sort_key(p['name']))
            # Four models per row bounds row height without truncating IDs.
            chunk_size = 4
            for offset in range(0, len(account_models), chunk_size):
                chunk = account_models[offset:offset + chunk_size]
                first = offset == 0
                displayed_models.extend(m['model_id'] for m in chunk)
                rows.append([
                    account_identity(account, linked_people, number, body, continuation=not first),
                    Paragraph('<br/><br/>'.join(model_text(m) for m in chunk), body),
                    Paragraph(geography_text(account, chunk, decisions, first), body),
                    Paragraph(route_text(account, chunk, decisions, linked_people, first), body),
                ])
    table = LongTable(rows, colWidths=column_widths, repeatRows=1, hAlign='LEFT', splitByRow=1, splitInRow=1)
    settings = [
            ('BACKGROUND', (0, 0), (-1, 0), TEAL),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LINEBELOW', (0, 0), (-1, 0), .6, TEAL),
            ('LINEBELOW', (0, 1), (-1, -1), .25, colors.HexColor('#BCCDD0')),
        ]
    for row in group_rows:
        settings.extend([('SPAN', (0, row), (-1, row)), ('BACKGROUND', (0, row), (-1, row), colors.HexColor('#D3E3E6')), ('NOSPLIT', (0, row), (-1, row+1))])
    table.setStyle(TableStyle(settings))
    story.append(table)
    assert len(displayed_models) == 917 and len(set(displayed_models)) == 917
    doc.build(story)
    print(json.dumps({'output': str(args.output), 'accounts': len(accounts), 'models': len(displayed_models), 'pages': doc.page}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accounts', type=Path, default=ROOT / 'data/account_inventory.csv')
    parser.add_argument('--models', type=Path, default=ROOT / 'data/model_inventory.csv')
    parser.add_argument('--people', type=Path, default=ROOT / 'data/people_classification.jsonl')
    parser.add_argument('--decisions', type=Path, default=ROOT / 'data/model_decisions.jsonl')
    parser.add_argument('--output', type=Path, default=ROOT / 'output/pdf/UK_Small_Model_Census_Appendix_2026-10-31.pdf')
    parser.add_argument('--working-note', default='', help='Optional status note for a private working draft.')
    build(parser.parse_args())


if __name__ == '__main__':
    main()
