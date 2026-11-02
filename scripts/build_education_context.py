"""Reproduce the full DfE sex/FSM/ethnicity comparison from released source rows."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'data/context/dfe_education_context.csv'
SLICES = [
    ('male_fsm','Male','Free School Meals'), ('female_fsm','Female','Free School Meals'),
    ('male_nonfsm','Male','All Other Pupils'), ('female_nonfsm','Female','All Other Pupils'),
    ('all_fsm','Total','Free School Meals'), ('all_nonfsm','Total','All Other Pupils'),
    ('all_pupils','Total','Total'), ('unknown_sex_fsm','Unknown','Free School Meals'),
    ('unknown_sex_all_pupils','Unknown','Total'),
]
MEASURES = ['participation_rate','number_of_students','number_of_he_students']
LABELS = {
    'English / Welsh / Scottish / Northern Irish / British':'White British',
    'Any other White background':'Other White background',
    'Any other Mixed / Multiple ethnic background':'Other Mixed / Multiple background',
    'Any other Asian background':'Other Asian background',
    'Any other Black / African / Caribbean background':'Other Black / African / Caribbean background',
}

def main():
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==222
    assert all(r['time_period']=='202021' and r['entry_age']=='By Age 19'
               and r['geographic_level']=='National' and r['country_name']=='England' for r in rows)
    lookup={(r['ethnicity_major'],r['ethnicity_minor'],r['sex'],r['fsm_status']):r for r in rows}
    assert len(lookup)==len(rows)
    groups=list(dict.fromkeys((r['ethnicity_major'],r['ethnicity_minor']) for r in rows))
    majors=list(dict.fromkeys(major for major,minor in groups if major!='Total'))
    order=[]
    for major in majors:
        if (major,'Total') in groups:order.append((major,'Total'))
        order.extend((major,minor) for m,minor in groups if m==major and minor!='Total')
    order.append(('Total','Total'))
    assert len(order)==len(set(order))==24
    comparison=[]
    for number,(major,minor) in enumerate(order,1):
        subtotal=minor=='Total'
        row={'display_order':number,'row_type':'national_total' if major=='Total' else 'major_subtotal' if subtotal else 'detailed',
             'hierarchy_level':0 if subtotal or (major,'Total') not in groups else 1,
             'ethnicity_major':major,'ethnicity_minor':minor,
             'display_label':'All ethnic groups' if major=='Total' else major+' (all)' if subtotal else
                             'Unknown ethnicity' if major=='Unknown' else LABELS.get(minor,minor)}
        for prefix,sex,fsm in SLICES:
            source=lookup.get((major,minor,sex,fsm),{})
            for measure in MEASURES:row[prefix+'_'+measure]=source.get(measure,'')
        comparison.append(row)
    with (ROOT/'data/context/dfe_education_comparisons.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(comparison[0]));writer.writeheader();writer.writerows(comparison)
    lines=[r'\begingroup\small\setlength{\tabcolsep}{4pt}',r'\renewcommand{\arraystretch}{1.16}',
           r'\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.38\linewidth}rrrrrr@{}}',
           r'\caption{Higher-education progression by age 19 in 2024/25 (\%). England state-funded and special-school pupils aged 15 in 2020/21; every recorded major and detailed ethnicity group. Source: DfE~\cite{dfe2026}.}\label{tab:dfe}\\']
    header=[r'\toprule & \multicolumn{2}{c}{FSM eligible} & \multicolumn{2}{c}{Non-FSM} & \multicolumn{2}{c}{All sexes}\\',
            r'Recorded ethnicity & Male & Female & Male & Female & FSM & All\\\midrule']
    lines += header+[r'\endfirsthead']+header+[r'\endhead',r'\bottomrule\endfoot']
    for row in comparison:
        label=row['display_label'].replace('&',r'\&')
        cells=[f"{float(row[p+'_participation_rate']):.1f}" for p in
               ['male_fsm','female_fsm','male_nonfsm','female_nonfsm','all_fsm','all_pupils']]
        if row['row_type']!='detailed':
            if row['display_order']!=1:lines.append(r'\addlinespace[3pt]')
            cells=[r'\textbf{'+c+'}' for c in [label]+cells]
        else:cells=[(r'\hspace*{0.7em}' if row['hierarchy_level'] else '')+label]+cells
        lines.append(' & '.join(cells)+r'\\')
    lines += [r'\end{longtable}',
        r'\noindent\footnotesize Bold rows are major-group or national totals; indented rows are their detailed categories. Totals and components overlap. White British abbreviates English / Welsh / Scottish / Northern Irish / British. Non-FSM is the source category All Other Pupils. FSM eligibility and sex are recorded at age 15. One pupil with unknown recorded sex is included in the all-sex totals. The released CSVs retain all 222 source rows, original category labels, HE entrant counts and pupil denominators for every displayed percentage.',
        r'\par\endgroup']
    (ROOT/'paper/education_comparisons.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Education context: {len(rows)} source rows; {len(comparison)} complete comparison rows')

if __name__=='__main__':main()
