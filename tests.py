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
from LILA import *

############################################################################################
## testowanie metody kosinusowej na kilku odcinkach wybranego korpusu

def conduct_cosine_test(corpus,sample_size,sample_count,hist_builder,normalized,fname,VERBOSE=True):
    if not fname.endswith(".json"): fname += ".json"
    if VERBOSE: print(fname)
    normcorp = {lang:[normalized(doc) for doc in corpus[lang]] for lang in corpus}
    RESULTS = []
    smallest = sorted([len(corpus[lang]) for lang in corpus])[0]
    for sample_from,sample_to in mk_sample_points(smallest,sample_size,sample_count):    
        if VERBOSE: print("sample {}-{}".format(sample_from,sample_to))
        tp = 0
        tc = 0
        results = []
        train,test = split_corpora(normcorp,sample_from,sample_to)
        t = milis()    
        scores_for = mk_cosine_model(train,hist_builder)
        tr_ms = milis()-t
        if VERBOSE: print("training: {}ms".format(tr_ms))
        t = milis()
        for lang in test:
            for doc in test[lang]:
                tc += 1
                scores = scores_for(doc)
                pred_lang = predicted_language(scores)
                if lang==pred_lang: tp += 1
                results.append({"text":doc,"expected":lang,"scores":scores})
        te_ms = milis()-t
        if VERBOSE: print("testing: {}ms (= {}t/s)".format(te_ms,1000.0*tc/te_ms))
        acc = 1.0*tp/tc
        if VERBOSE: print("Acc={}".format(acc))
        RESULTS.append({"sample_from":sample_from,
                        "sample_to":sample_to,
                        "acc":acc,
                        "train_s": tr_ms/1000.0,
                        "test_s": te_ms/1000.0,                    
                        "results": results})
    json.dump(RESULTS,open(fname,"w"),ensure_ascii=False, indent=2)
    
############################################################################################
## testowanie metody out-of-place dla ustalonych długości 300,500 i 1000, jw.

def conduct_ooo_test(corpus,sample_size,sample_count,hist_builder,normalized,fname,VERBOSE=True):
    if not fname.endswith(".json"): fname += ".json"
    if VERBOSE: print(fname)
    normcorp = {lang:[normalized(doc) for doc in corpus[lang]] for lang in corpus}
    RESULTS = []
    smallest = sorted([len(corpus[lang]) for lang in corpus])[0]
    for sample_from,sample_to in mk_sample_points(smallest,sample_size,sample_count):    
        if VERBOSE: print("sample {}-{}".format(sample_from,sample_to))
        tp3,tp5,tp10 = [0,0,0]
        tc = 0
        results = []
        train,test = split_corpora(normcorp,sample_from,sample_to)
        t = milis()
        scores_for = mk_ranking_model(train,hist_builder,1000)
        tr_ms = milis()-t
        if VERBOSE: print("training: {}ms".format(tr_ms))
        t = milis()
        for lang in test:
            for doc in test[lang]:
                tc += 1
                scores3 = scores_for(doc,300)
                scores5 = scores_for(doc,500)
                scores10 = scores_for(doc,1000)
                pred_lang3 = predicted_language(scores3)
                pred_lang5 = predicted_language(scores5)
                pred_lang10 = predicted_language(scores10)
                if lang==pred_lang3: tp3 += 1
                if lang==pred_lang5: tp5 += 1
                if lang==pred_lang10: tp10 += 1
                results.append({"text":doc,"expected":lang,
                                "scores_300":scores3,
                                "scores_500":scores5,
                                "scores_1000":scores10})
        te_ms = milis()-t
        if VERBOSE: print("testing: {}ms (= {}t/s)".format(te_ms,1000.0*tc/te_ms))
        acc3 = 1.0*tp3/tc
        acc5 = 1.0*tp5/tc
        acc10 = 1.0*tp10/tc
        if VERBOSE: print("Acc 300={}, 500={}, 1000={}".format(acc3,acc5,acc10))
        RESULTS.append({"sample_from":sample_from,
                        "sample_to":sample_to,
                        "acc_300":acc3,
                        "acc_500":acc5,
                        "acc_1000":acc10,                    
                        "train_s": tr_ms/1000.0,
                        "test_s": te_ms/1000.0,                    
                        "results": results})
    json.dump(RESULTS,open(fname,"w"),ensure_ascii=False, indent=2)

############################################################################################
## przykład użycia:
corp = {
    "en": json.load(open("korpus_en.json")),
    "es": json.load(open("korpus_es.json")),
    "de": json.load(open("korpus_de.json")),    
}

sample_size = 1000
sample_count = 9
norm = letters_and_apostrophes

hb = mk_histogram_builder(min_n=2,max_n=2,accepted=accept_intoken)
conduct_cosine_test(corp,sample_size,sample_count,hb,norm,"cos_2_2_intok_letap")

hb = mk_histogram_builder(min_n=2,max_n=4,accepted=accept_intoken)
conduct_ooo_test(corp,sample_size,sample_count,hb,norm,"ooo_2_4_intok_letap")
