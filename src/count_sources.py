#!/usr/bin/env python3
"""Map each endnote to the underlying work(s) it cites, so the source count is auditable.

An endnote is not a source: several are Ibid., several re-cite a work already cited,
and several cite two or three works at once. This records that mapping explicitly.
"""
import re, sys
from collections import defaultdict
from pathlib import Path

MD = Path(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/regen/memo.md')

# note number -> list of work keys it cites
NOTE_TO_WORKS = {
    1:  ['morh_pbb2025'],
    2:  ['morh_pbb2025'],                      # Ibid.
    3:  ['adom_44pct'],
    4:  ['afdb_appraisal'],
    5:  ['gt_asensoboakye'],
    6:  ['morh_pbb2025', 'gt_asensoboakye'],   # compares the two series
    7:  ['act1147'],
    8:  ['act1147'],
    9:  ['asuogyaman_budget'],
    10: ['ag2006', 'act536'],
    11: ['act1147'],
    12: ['act1147'],
    13: ['graphic_boardinaug'],
    14: ['act1147'],
    15: ['act1135', 'taxlawgh'],
    16: ['esl_amend_bill2026'],
    17: ['mof_esl_report'],
    18: ['act899', 'act997', 'act1135', 'ag2006'],  # + AG 2006 on the pre-2015 rate
    19: ['wb_wdi', 'gss'],
    20: ['mof_esl_report'],                    # 2019 edition of the same series
    21: ['allafrica_tolls'],
    22: ['graphic_tollopinion'],
    23: ['gbc_tollppp'],
    24: ['mof_esl_report'],                    # 2016 + 2019 editions
    25: ['morh_pbb2025'],
    26: ['act1147'],
    27: ['act1147'],
    28: ['morh_pbb2025'],
    29: ['morh_pbb2025'],                      # Ibid.
    30: ['gt_parliament36bn'],
    31: ['newsghana_agbodza'],
    32: ['newsghana_agbodza'],                 # Ibid.; reports a Fourth Estate investigation
    33: ['corruptionwatch'],
    34: ['gha_inspection'],
    35: ['graphic_brokenroads'],
    36: ['graphic_boardinaug'],                # "see note 13"
    37: ['myjoy_231bn'],
    38: ['morh_pbb2025'],
    39: ['mof_budget2025'],
    40: ['fourthestate_bigpush'],
    41: ['gt_parliament36bn'],                 # "same source as note 30"
    42: ['graphic_gra_july16', 'act1141'],
    43: ['wb_isr_tsip', 'morh_pbb2025'],
    44: ['ag2006'],
    45: ['wb_24248'],
    46: ['wb_18413'],
    47: ['morh_amoakoattah'],
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
    'newsghana_agbodza': 'press', 'corruptionwatch': 'press',
    'graphic_brokenroads': 'press', 'myjoy_231bn': 'press',
    'fourthestate_bigpush': 'press', 'graphic_gra_july16': 'press',
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
for kind in ['statute', 'government', 'press', 'unclassified']:
    if by_kind[kind]:
        print(f"  {kind:12}: {len(by_kind[kind])}")
print()
reused = {k: v for k, v in works.items() if len(v) > 1}
print(f"works cited in more than one note: {len(reused)}")
for k, v in sorted(reused.items(), key=lambda x: -len(x[1])):
    print(f"  {k:24} notes {v}")
multi = {n: k for n, k in NOTE_TO_WORKS.items() if len(k) > 1}
print(f"\nnotes citing more than one work: {len(multi)}  -> {sorted(multi)}")
