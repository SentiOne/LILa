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

import json

methods = ["2_2_intok_letap-ci",
           "2_2_intok_letap",
           "2_2_intok_let-ci",
           "2_2_intoksuff_letap-ci",
           "2_2_intoksuff_letap",
           "2_2_intoksuff_let-ci",
           "2_4_intok_letap-ci",
           "2_4_intok_letap",
           "2_4_intok_let-ci",
           "2_4_intoksuff_letap-ci",
           "2_4_intoksuff_letap",
           "2_4_intoksuff_let-ci",
           "4_4_intok_letap-ci",
           "4_4_intok_letap",
           "4_4_intok_let-ci",
           "4_4_intoksuff_letap-ci",
           "4_4_intoksuff_letap",
           "4_4_intoksuff_let-ci"]

print('"method",, "top300",,, ,"top500",,, ,"top1000",,, ,"cosine",,,')

for method in ["2_2_intok_letap", "2_2_intok_let-ci"]: # test test
    cds = json.load(open("cos_" + method + ".json"))
    ods = json.load(open("ooo_" + method + ".json"))
    accs = {"cos":[],
            "ooo3":[],
            "ooo5":[],
            "ooo10":[]}
    for d in cds: accs["cos"].append(d["acc"])
    for d in ods:
        accs["ooo3"].append(d["acc_300"])
        accs["ooo5"].append(d["acc_500"])
        accs["ooo10"].append(d["acc_1000"])
    stats = {}
    rnd = 4
    for m in accs:
        accs[m].sort()
        q_min = accs[m][0]
        q_max = accs[m][-1]
        l = len(accs[m])
        q_med = accs[m][l//2] if l%2==1 else (accs[m][l//2]+accs[m][l//2+1])/2.0
        stats[m] = {"min": round(q_min,rnd), "med": round(q_med,rnd), "max": round(q_max,rnd)}
    print('"{}",,{},{},{},,{},{},{},,{},{},{},,{},{},{}'.format(
        method,
        stats["ooo3"]["min"],stats["ooo3"]["med"],stats["ooo3"]["max"],
        stats["ooo5"]["min"],stats["ooo5"]["med"],stats["ooo5"]["max"],
        stats["ooo10"]["min"],stats["ooo10"]["med"],stats["ooo10"]["max"],
        stats["cos"]["min"],stats["cos"]["med"],stats["cos"]["max"]))
        
