#!/usr/bin/python

# Love Letters, copyright (c) 2014 Nick Montfort <nickm@nickm.com>
# Original by Christopher Strachey, 1952
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
# IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Updated 10 March 2015 to correct the word lists. Sources are photographs
# of Christoper Stachey's notes in the Bodleian Library from J.R. Carpenter
# and table 14.1 in Noah Wardrip-Fruin's article "Digital Media Archaeology."
# Updated 31 May 2018 to add compatibility with Python 3 (Python 2 still works), also moved all print statements/functions to bottom

from random import choice
import textwrap

first = ['DARLING', 'DEAR', 'HONEY', 'JEWEL']
second = ['DUCK', 'LOVE', 'MOPPET', 'SWEETHEART']
adjectives = ['ADORABLE', 'AFFECTIONATE', 'AMOROUS', 'ANXIOUS', 'ARDENT', 'AVID', 'BREATHLESS', 'BURNING', 'COVETOUS', 'CRAVING', 'CURIOUS', 'DARLING', 'DEAR', 'DEVOTED', 'EAGER', 'EROTIC', 'FERVENT', 'FOND', 'IMPATIENT', 'KEEN', 'LITTLE', 'LOVEABLE', 'LOVESICK', 'LOVING', 'PASSIONATE', 'PRECIOUS', 'SWEET', 'SYMPATHETIC', 'TENDER', 'UNSATISFIED', 'WISTFUL']
nouns = ['ADORATION', 'AFFECTION', 'AMBITION', 'APPETITE', 'ARDOUR', 'CHARM', 'DESIRE', 'DEVOTION', 'EAGERNESS', 'ENCHANTMENT', 'ENTHUSIASM', 'FANCY', 'FELLOW FEELING', 'FERVOUR', 'FONDNESS', 'HEART', 'HUNGER', 'INFATUATION', 'LIKING', 'LONGING', 'LOVE', 'LUST', 'PASSION', 'RAPTURE', 'SYMPATHY', 'TENDERNESS', 'THIRST', 'WISH', 'YEARNING']
adverbs = ['AFFECTIONATELY', 'ANXIOUSLY', 'ARDENTLY', 'AVIDLY', 'BEAUTIFULLY', 'BREATHLESSLY', 'BURNINGLY', 'COVETOUSLY', 'CURIOUSLY', 'DEVOTEDLY', 'EAGERLY', 'FERVENTLY', 'FONDLY', 'IMPATIENTLY', 'KEENLY', 'LOVINGLY', 'PASSIONATELY', 'SEDUCTIVELY', 'TENDERLY', 'WINNINGLY', 'WISTFULLY']
verbs = ['ADORES', 'ATTRACTS', 'CARES FOR', 'CHERISHES', 'CLINGS TO', 'DESIRES','HOLDS DEAR', 'HOPES FOR', 'HUNGERS FOR', 'IS WEDDED TO', 'LIKES', 'LONGS FOR', 'LOVES', 'LUSTS AFTER', 'PANTS FOR', 'PINES FOR', 'PRIZES', 'SIGHS FOR', 'TEMPTS', 'THIRSTS FOR', 'TREASURES', 'WANTS', 'WISHES', 'WOOS', 'YEARNS FOR']

def maybe(words):
    if choice([False, True]):
        return ' ' + choice(words)
    return ''

def longer():
    return (' MY' + maybe(adjectives) + ' ' + choice(nouns) +
            maybe(adverbs) + ' ' + choice(verbs) + ' YOUR' +
            maybe(adjectives) + ' ' + choice(nouns) + '.')

def shorter():
    return (' ' + choice(adjectives) + ' ' + choice(nouns) + '.')

text = ''
you_are = False
for i in range(0,5):
    type = choice(['longer', 'shorter'])
    if type == 'longer':
        text = text + longer()
        you_are = False
    else:
        if you_are:
            text = text[:-1] + ': MY' + shorter()
            you_are = False
        else:
            text = text + ' YOU ARE MY' + shorter()
            you_are = True

print('')
print(choice(first) + ' ' + choice(second))
print('')
print(textwrap.fill(text, 80))
print('')
print('                                        YOURS ' + choice(adverbs))
print('')
print('                                        M.U.C.')
print('')
