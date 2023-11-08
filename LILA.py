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

#########################################################################################
### LILa -- laboratorium detekcji języków metodami n-gramowymi
import json,re,unicodedata
from math import inf,sqrt


#########################################################################################
## użyteczne procedury do normalizacji tekstu
#########################################################################################

_nonletter  = re.compile(r"[^\w0-9]")
_nonletterq = re.compile(r"[^\w0-9']")
_multispace = re.compile(r"[\s]+")
_punctation = re.compile(r"[-.,!?;:]+")
_hyphen     = re.compile(r"[-–—]{1,2}")
_apostrophe = re.compile(r"[’']")

def normalized_apostrophes(text): return _apostrophe.sub("'", text)
def normalized_hyphens(text): return _hyphen.sub("-", text)

def no_normalization(text): return text

_trns = str.maketrans("żółćęśąźńŻÓŁĆĘŚĄŹŃáéíóúüñÁÉÍÓÚÜÑäöüÄÖÜ",
                      "zolcesaznZOLCESAZNaeiouunAEIOUUNaouAOU")
def dediacriticized(text):
    text = text.replace("ß","ss").replace("¡","").replace("¿","").translate(_trns)
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
    return text.decode('ascii')

def only_letters_ci(text):
    text = text.lower()
    text = _nonletter.sub(" ", text)
    text = _multispace.sub(" ", text)
    return text

def letters_and_apostrophes(text):
    text = normalized_hyphens(text)
    text = normalized_apostrophes(text)
    text = _nonletterq.sub(" ", text)
    text = _multispace.sub(" ", text)
    return text

def letters_and_apostrophes_ci(text):
    text = text.lower()
    text = normalized_hyphens(text)
    text = normalized_apostrophes(text)
    text = _nonletterq.sub(" ", text)
    text = _multispace.sub(" ", text)
    return text
    

#########################################################################################
## budowanie histogramów n-gramów
#########################################################################################

## konfigurujące procedury decydujące czy dodać n-gram do histogramu:
def accept_any(start, end, text): return True

## tylko n-gramy w obrębie pojedynczego wyrazu/leksemu:
def accept_intoken(start,end,text): return (" " not in text[start:end])

## tylko ngramy stojące na końcu leksemów (tj po których występuje znak inny niż litera)
def accept_suffixes(start, end, text):
    return (end+1 >= len(text) or _nonletter.match(text[end+1]))

def accept_intoken_suffixes(start,end,text):
    return accept_intoken(start,end,text) and accept_suffixes(start,end,text)

## procedury przetwarzania ngramu przed jego dodaniem do histogramu:
def unprocessed(ngram): return ngram
def stripped(ngram): return ngram.strip()

## i samo budowanie histogramu:
def ngram_histogram(text,
                    min_n=2,
                    max_n=3,
                    accepted=accept_intoken,
                    processed=stripped,
                    hist={}):
    for n in range(min_n, max_n+1):
        for i in range(0, len(text)-n):
            ngram = processed(text[i:(i+n)])
            if len(ngram)>=min_n and accepted(i,i+n,text):
                hist[ngram] = 1 + hist.get(ngram, 0)
    return hist

## + opakowanie żeby nie przekazywać wszystkich parametrów:
def mk_histogram_builder(min_n=2,
                         max_n=3,
                         accepted=accept_any,
                         processed=stripped):
    def _builder(text,hist={}):
        return ngram_histogram(text,min_n,max_n,accepted,processed,hist)
    return _builder


#########################################################################################
## ranking n-gramów zamiast ,,pełnego'' histogramu:
#########################################################################################

def histogram2ranking(hist,topN=300):
    return sorted(hist.keys(), key=hist.get, reverse=True)[:topN]


#########################################################################################
## pseudometryka na przestrzeni histogramów
#########################################################################################

def cosine_similarity(hist0, hist1):
    num = 1.0 * sum([hist0[ngram]*hist1[ngram] for ngram in hist0 if ngram in hist1])
    den = (sqrt(sum([hist0[ngram]**2 for ngram in hist0])) *
           sqrt(sum([hist1[ngram]**2 for ngram in hist1])))
    assert(den>0) # niech się zatrzyma jeśli ma pusty dokument?
    #if den==0.0: return inf # dzięki uprzejmości autorów modułu math (sqrt(0)*sqrt(0))==0
    return num/den

def cosine_distance(hist0, hist1): return 1.0-cosine_similarity(hist0, hist1)

## znacznie przyspieszamy proces normalizując "wektory":
def normalized_histogram(hist):
    norm = sqrt(sum(hist[ngram]**2 for ngram in hist))
    return {ngram: hist[ngram]/norm for ngram in hist}

## ...bo wtedy w sumie liczymy iloczyn skalarny:
def fast_cosine_similarity(normhist0,normhist1):
    return sum([normhist0[ngram]*normhist1[ngram]
                for ngram in normhist0 if ngram in normhist1])

def fast_cosine_distance(hist0, hist1): return 1.0-fast_cosine_similarity(hist0, hist1)


#########################################################################################
## pseudometryka na przestrzeni rankgingów (``misplacement''/ ``out-of-order metrics'')
#########################################################################################

def ranking_distance(rank0, rank1, topN=300):
    misplacement = 0
    for i in range(min(topN,len(rank0))):
        ngram = rank0[i]
        misplacement += abs(rank1.index(ngram)-i) if ngram in rank1 else topN+1
    return misplacement

def ranking_similarity(rank0, rank1, topN=300): # dla zachowania porządku
    return -1*ranking_distance(rank0, rank1, topN)

def norm_ranking_similarity(rank0, rank1, topN=300): # dla zachowania skali, wygładzony
    return 1.0/(1+ranking_distance(rank0, rank1, topN))
# przy czym jest znacznie bardziej zakrzywiony od kosinusów więc lepiej używać -1*...


#########################################################################################
## budowanie modeli (profili językowych i procedur predykcji języka)
#########################################################################################

def corpus_histogram(corpus,hist_builder):
    hist = {}
    for doc in corpus: hist = hist_builder(doc,hist)
    return hist

def mk_cosine_model(corpora, hist_builder):
    # 1. buduje profile języków z korpusu:
    profiles = {}
    for lang in corpora:
        hist = {}
        for doc in corpora[lang]: hist = hist_builder(doc,hist)
        profiles[lang] = normalized_histogram(hist)
    # 2. buduje dla nich procedurę dopasowania doc->(lang->score)
    def _scores(document):
        vector = normalized_histogram(hist_builder(document,{}))
        return {lang: fast_cosine_similarity(vector,profiles[lang]) for lang in profiles}
    return _scores

def mk_ranking_model(corpora, hist_builder, top_rank=1000):
    # 1. buduje profile języków z korpusu:
    profiles = {}
    for lang in corpora:
        hist = {}
        for doc in corpora[lang]: hist = hist_builder(doc,hist)
        profiles[lang] = histogram2ranking(hist,top_rank)
    # 2. buduje dla nich procedurę dopasowania doc->(lang->score)
    def _scores(document,topN=top_rank):
        vector = histogram2ranking(hist_builder(document,{}))
        return {lang: ranking_similarity(vector,profiles[lang],topN) for lang in profiles}
    return _scores


#########################################################################################
# ewaluacja tekstu w oparicu o dostępne profile
#########################################################################################

def predicted_language(lang_scores):
    return sorted(lang_scores.keys(), key=lang_scores.get, reverse=True)[0]

def similarity_scores(document_vector,profiles,similarity_metric):
    return {lang:similarity_metric(document_vector,profiles[lang]) for lang in profiles}


#########################################################################################
# procedury pomocniczne do automazywacji testowania
#########################################################################################

import time
def milis(): return round(time.time() * 1000)

def mk_sample_points(corp_size,test_size=1000,samples=10):
    span = int((corp_size-test_size)/(samples-1))
    return [(i*span,i*span+test_size) for i in range(0,samples)]

def split_corpora(corpora,sample_from,sample_to):
    train = {}
    test = {}
    for lang in corpora:
        corpus = corpora[lang]
        test[lang] = [doc for doc in corpus[sample_from:sample_to]]
        train[lang] = [doc for doc in (corpus[:sample_from]+corpus[sample_to:])]
    return (train,test)

def m_F1(tp,fp,fn): return (2.0*tp)/(2.0*tp+fp+fn)
def m_P(tp,fp,fn): return 1.0*tp/(tp+fp)
def m_R(tp,fp,fn): return 1.0*tp/(tp+fn)
## chociaż przy domkniętym korpusie (tj każdy tekst to dokładnie 1 z N języków)
## zachodzi F1=P=R=accuracy bo fp jednego języka to fn drugiego.

