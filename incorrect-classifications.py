#!/usr/bin/python3

"""
This file is part of LILa
Copyright (C) 2022-2023 SentiOne

LILa is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


###############################################################################
## skrypt ładuje wskazany plik .json od tests.py i listuje błędy klasyfikiacji
## wraz z długością tekstu oraz stosunkiem najlepszego wyniku do
## drugiego-najlepszego (relatywna różnica wyników, im mniejsza tym wynik
## pewniejszy).

import json,sys

fname = sys.argv[1]
ds = json.load(open(fname))
accs = []
for d in ds: accs.append(d["acc"])
accs.sort()
q_min = accs[0]
q_max = accs[-1]
l = len(accs)
q_med = accs[l//2] if l%2==1 else (accs[l//2]+accs[l//2+1])/2.0

rnd = 4

print('"{}"'.format(fname))
print('"accuracy:"')
print('"min","median","max"')
print('{},{},{}'.format(round(q_min,rnd),
                        round(q_med,rnd),
                        round(q_max,rnd)))

print('\n"misclassifications:"')

c = 0
for s in json.load(open("eksperyment_4_4_intok_let-ap-N.json")):
    c += 1
    print('"sample #{} (F1={})"'.format(c,s["acc"]))
    print('"expected","result",,"score_en","score_es","score_de",,"textlen","dist.ratio",,"text"')
    for r in s["results"]:
        sc = sorted(r["scores"].keys(), key=r["scores"].get, reverse=True)
        pred = sc[0]        
        if r["expected"]==pred: continue        
        dist_ratio = r["scores"][sc[1]]/r["scores"][sc[0]] if r["scores"][sc[0]]>0 else 0.0
        print('"{}","{}",,{},{},{},,{},{},,"{}"'.format(r["expected"],pred,
                                                        r["scores"]["en"],
                                                        r["scores"]["es"],
                                                        r["scores"]["de"],
                                                        len(r["text"]),
                                                        dist_ratio,
                                                        r["text"]))
        
            
    
    
    
