## Install

The module requires only Python3 and Unidecode library

```
pip install Unidecode
```

In order to use it simply import LILA.py
```
from LILA import *
```


## Text normalization

The module contains a few useful text normalization procedures and regexes, in particular:
- conversion of hyphens and quotes into ascii,
- latinization (dropping diacritics and accents),
- elimination of non-letter symbols

```
>>> dediacriticized("¡Feliz Año Nuevo!")
'Feliz Ano Nuevo!'
>>> letters_and_apostrophes_ci(dediacriticized("Übung macht den Meister :)"))
'ubung macht den meister '
>>> only_letters_ci("Don't panic!")
"don t panic "
```

It's easy to build custom ones from these.


## Building a classifier

Train corpora should be provided as a dictionary from language code/label to list of utf-8
strings (one string per document). Normalization should be applied at this stage, e.g.
```
>>> corpus = {
    "en": json.load(open("korpus_en.json")),
    "de": json.load(open("korpus_en.json")),
    "es": json.load(open("korpus_en.json")),
}

>>> normalized = letters_and_apostrophes_ci
>>> corpus = {lang:[normalized(doc) for doc in corpus[lang]] for lang in corpus}
```

The module implements two metrics popular in language classification systems. Both are based
on n-gram histogram. A procedure for building one can be generated with higher-order procedure
`mk_histogram_builder` -- its four optional arguments are minimal and maximal n-gram length,
n-gram acceptance and n-gram preprocessing procedures:

```
>>> hb = mk_histogram_builder(min_n=2,max_n=4,accepted=accept_intoken,processed=stripped)
>>> hb("policz mi histogram dla tego tekstu")
{'po': 1, 'ol': 1, 'li': 1, 'ic': 1, 'cz': 1, 'mi': 1, 'hi': 1, 'is': 1, 'st': 2, 'to': 1, 'og': 1, 'gr': 1, 'ra': 1, 'am': 1, 'dl': 1, 'la': 1, 'te': 2, 'eg': 1, 'go': 1, 'ek': 1, 'ks': 1, 'pol': 1, 'oli': 1, 'lic': 1, 'icz': 1, 'his': 1, 'ist': 1, 'sto': 1, 'tog': 1, 'ogr': 1, 'gra': 1, 'ram': 1, 'dla': 1, 'teg': 1, 'ego': 1, 'tek': 1, 'eks': 1, 'kst': 1, 'poli': 1, 'olic': 1, 'licz': 1, 'hist': 1, 'isto': 1, 'stog': 1, 'togr': 1, 'ogra': 1, 'gram': 1, 'tego': 1, 'teks': 1, 'ekst': 1}
```

There are four n-gram acceptance strategies implemented already:
- `accept_any` -- adds all found n-grams,
- `accept_intoken` -- only n-grams contained within single lexeme,
- `accept_suffixes` -- only n-grams containing last character of lexeme,
- `accept_intoken_suffixes` -- only lexeme suffixes.

For pre-processing there are these two:
- `unprocesses` -- an identity,
- `stripped` -- removing leading and trailing white spaces, e.g. with `accept_any` strategy).


Once having a `corpus` dictionary (`lang->[documents]`) and a histogram builder procedure `hb`
it's enough to use one of model-building procedures:
- `mk_cosine_model` -- based on cosine distance between n-gram histograms-as-vectors,
- `mk_ranking_model` -- based on out-of-placement metric (Cavnar & Trenkle, 1994).

```
>>> model1 = mk_cosine_model(corpus,hb)
>>> model1("der schnee ist weiß")
{'en': 0.16159130685823997, 'es': 0.1457812620102102, 'de': 0.3696150834426688}
>>> model1("la nieve es blanca")
{'en': 0.1497045427025336, 'es': 0.2006750733646224, 'de': 0.11740020349012875}
>>> model1("the snow is white")
{'en': 0.2937208192557997, 'es': 0.049568374684066795, 'de': 0.06644535429581588}
```

Similarly to the corpora, text to be classified should get normalized too:
```
>>> model1(normalized("der Schnee ist weiß!!!"))
{'en': 0.1511548267361471, 'es': 0.13636588396343255, 'de': 0.347015073786404}
```

Most likely prediction can be picked with `predicted_language` procedure:
```
>>> predicted_language(model1(normalized("Good food & great service!")))
'en'
```

In case of out-of-place models, model-building procedure accepts optional argument `top_rank`
which limits the number of n-grams used in modeling.
Nb this model returns negative integer scores.

```
>>> model2 = mk_ranking_model(corpus,hb,top_rank=1000)
>>> model2("the snow is white")
{'en': -5694, 'es': -11817, 'de': -10942}
>>> predicted_language(model2(normalized("der Schnee ist weiß")))
'de'
```

For 3 languages with 30k document corpora each and `n` between 1 and 4, building a model
takes 5-50s.


## Testing

The module contains a few utilities allowing evaluation and comparison of generated models.
These are used in `tests.py` script.

In order to conduct 9 experiments by selecting (each time different) 1k documents
per language as a test sample and the rest as train sample, with intoken 2-grams and cosine
similarity metrics, asciized normalization:
```
>>> sample_size = 1000
>>> sample_count = 9
>>> norm = letters_and_apostrophes
>>> hb = mk_histogram_builder(min_n=2,max_n=2,accepted=accept_intoken)
>>> conduct_cosine_test(corpus,sample_size,sample_count,hb,norm,"test1")
```
the last procedure saves results as `test1.json`, which contains 9 dictionaries with keys:
- `sample_from` -- start index of test sample window,
- `sample_to` -- end index of test sample window,
- `acc` -- accuracy on test sample,
- `train_s` -- model training time in seconds,
- `test_s` -- model testing time in seconds,
- `results` -- a list of partial results (raw text, expected language and language scores).

The script `incorrect_classifications.py` converts the above .json file into .csv containing
a table of best, worst and median result for a series of experiments, followed by list of
incorrect classifications with some basic metrics (e.g. ratio of two highest scores).

Finally `tabela.py` can be used to generate .csv reports.

---

Language corpora from various sources on CC license can be found e.g. there:
https://wortschatz.uni-leipzig.de/en/download


```
wget https://downloads.wortschatz-leipzig.de/corpora/spa_news_2022_30K.tar.gz
tar xf spa_news_2022_30K.tar.gz
cp spa_news_2022_30K/spa_news_2022_30K-sentences.txt .
rm -rf spa_news_2022_30K/
```

these are in .tsv format:
```
import csv,json
txts = []
for row in csv.reader(open("spa_news_2022_30K-sentences.txt"),delimiter="\t"):
  txts.append(row[1])
json.dump(txts,open("korpus_es.json", "w"), ensure_ascii=False, indent=2)
```

