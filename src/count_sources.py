#!/usr/bin/env python3
"""Map each endnote to the underlying work(s) it cites, so the source count is auditable.

An endnote is not a source: several are Ibid., several re-cite a work already cited,
and several cite two or three works at once. This records that mapping explicitly.
"""
import re, sys
from collections import defaultdict
from pathlib import Path

MD = Path(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/regen/memo.md')

# note number -> list of work keys it cites (numbers follow first appearance in the text)
NOTE_TO_WORKS = {
    1:  ['morh_pbb2025'],
    2:  ['morh_pbb2025'],  # Ibid.
    3:  ['adom_44pct'],
    4:  ['gt_asensoboakye'],
    5:  ['afdb_appraisal'],
    6:  ['morh_pbb2025', 'gt_asensoboakye'],  # compares the two series
    7:  ['act1147'],
    8:  ['act1147'],
    9:  ['asuogyaman_budget'],
    10: ['morh_amoakoattah'],
    11: ['amoatey_ankrah2017'],
    12: ['barajei2023'],
    13: ['aboagye2024'],
    14: ['pokuboansi2018'],
    15: ['luong_azuma2022'],
    16: ['ag2006', 'act536'],
    17: ['act536'],
    18: ['act1147'],
    19: ['foster_pushak2011'],
    20: ['act1147'],
    21: ['graphic_boardinaug'],
    22: ['act1147'],
    23: ['act1135', 'taxlawgh'],
    24: ['esl_amend_bill2026', 'gbc_energylevy'],
    25: ['mof_esl_report'],
    26: ['act899', 'act997', 'act1135', 'ag2006'],  # + AG 2006 on the pre-2015 rate
    27: ['wb_wdi', 'gss'],
    28: ['ifs2016', 'wb_wdi'],
    29: ['mof_esl_report'],  # 2019 edition of the same series
    30: ['allafrica_tolls'],
    31: ['graphic_tollopinion'],
    32: ['gbc_tollppp'],
    33: ['mof_esl_report'],  # 2016 + 2019 editions
    34: ['morh_pbb2025'],
    35: ['act1147'],
    36: ['act1147'],
    37: ['morh_pbb2025'],
    38: ['morh_pbb2025'],  # Ibid.
    39: ['gt_parliament36bn'],
    40: ['newsghana_agbodza'],
    41: ['newsghana_agbodza'],  # Ibid.; reports a Fourth Estate investigation
    42: ['ppa_std_works'],
    43: ['ag2019_roads'],  # replaces the Corruption Watch summary
    44: ['gha_inspection'],
    45: ['afdb_idev2021', 'gbn_fufulso'],
    46: ['graphic_brokenroads'],
    47: ['graphic_boardinaug'],  # "see note 13"
    48: ['myjoy_231bn'],
    49: ['morh_pbb2025'],
    50: ['mof_budget2025'],
    51: ['afrobarometer_r8', 'cdd_release2019'],
    52: ['damoah_kumi2018'],
    53: ['fourthestate_bigpush'],
    54: ['gt_parliament36bn'],  # "same source as note 30"
    55: ['graphic_gra_july16', 'act1141', 'gna_certurgency', 'citi_gprtu', 'mg_esla2025'],  # + sources for urgency, opposition, GH¢8.81bn
    56: ['wb_isr_tsip', 'morh_pbb2025'],
    57: ['act921'],
    58: ['ag2006'],
    59: ['wb_24248'],
    60: ['wb_18413'],
}

KIND = {
    'act1147': 'statute', 'act536': 'statute', 'act1135': 'statute',
    'act899': 'statute', 'act997': 'statute', 'act1141': 'statute',
    'morh_pbb2025': 'government', 'afdb_appraisal': 'government', 'ag2006': 'government',
    'asuogyaman_budget': 'government', 'mof_esl_report': 'government',
    'mof_budget2025': 'government', 'gha_inspection': 'government',
    'morh_amoakoattah': 'government', 'wb_wdi': 'government', 'gss': 'government',
    'wb_isr_tsip': 'government', 'wb_24248': 'government', 'wb_18413': 'government',
    'adom_44pct': 'press', 'gt_asensoboakye': 'press', 'graphic_boardinaug': 'press',
    'taxlawgh': 'press', 'esl_amend_bill2026': 'press', 'allafrica_tolls': 'press',
    'graphic_tollopinion': 'press', 'gbc_tollppp': 'press', 'gt_parliament36bn': 'press',
    'newsghana_agbodza': 'press',     'graphic_brokenroads': 'press', 'myjoy_231bn': 'press',
    'fourthestate_bigpush': 'press', 'graphic_gra_july16': 'press',
    'gbc_energylevy': 'press', 'gna_certurgency': 'press', 'citi_gprtu': 'press',
    'mg_esla2025': 'press',
    'act921': 'statute', 'foster_pushak2011': 'government',
    'barajei2023': 'academic', 'aboagye2024': 'academic', 'pokuboansi2018': 'academic',
    'luong_azuma2022': 'academic', 'amoatey_ankrah2017': 'academic', 'damoah_kumi2018': 'academic',
    'ppa_std_works': 'government', 'ag2019_roads': 'government', 'ifs2016': 'government',
    'afrobarometer_r8': 'government', 'cdd_release2019': 'press', 'afdb_idev2021': 'government',
    'gbn_fufulso': 'press',
}

src = MD.read_text(encoding='utf-8')
defined = sorted(int(n) for n in re.findall(r'^\[\^(\d+)\]:', src, re.M))
refs = re.findall(r'\[\^(\d+)\]', src)
ref_count = len(refs) - len(defined)          # in-text references

missing = set(defined) - set(NOTE_TO_WORKS)
extra = set(NOTE_TO_WORKS) - set(defined)
if missing or extra:
    sys.exit(f"mapping out of sync — unmapped notes {sorted(missing)}, stale {sorted(extra)}")

works = defaultdict(list)
for note, keys in NOTE_TO_WORKS.items():
    for k in keys:
        works[k].append(note)

by_kind = defaultdict(set)
for k in works:
    by_kind[KIND.get(k, 'unclassified')].add(k)

print(f"endnotes defined      : {len(defined)}")
print(f"in-text references    : {ref_count}")
print(f"distinct works cited  : {len(works)}")
print()
for kind in ['statute', 'government', 'academic', 'press', 'unclassified']:
    if by_kind[kind]:
        print(f"  {kind:12}: {len(by_kind[kind])}")
print()
reused = {k: v for k, v in works.items() if len(v) > 1}
print(f"works cited in more than one note: {len(reused)}")
for k, v in sorted(reused.items(), key=lambda x: -len(x[1])):
    print(f"  {k:24} notes {v}")
multi = {n: k for n, k in NOTE_TO_WORKS.items() if len(k) > 1}
print(f"\nnotes citing more than one work: {len(multi)}  -> {sorted(multi)}")
