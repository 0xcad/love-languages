# psr

## cmu rules
* VP - verb prhase
    * V - verb
* DP - determiner phrase
    * D - determiner
    * NP - noun phrase
        * N - noun
* PP - preposition phrase
    * P - preposition
* AP - adjective phrase
    * A - adjective and adverb

* CP shell, and TP (tense phrase)
* Sentence is NP VP

parts: V, D, N, P, Adj/Adv, P
* also C, complementizers

## [stanford rules](https://web.stanford.edu/class/linguist1/Slides/english-syntax-ho.pdf)
differences from CMU:
parts: DET, N, ADJ, ADV, V, TV (transitive verb), DTV (distransitive verb), SV (sentiential complement verbs), P

## psr notes/ideas
* past attempt tried to get 8 parts and directly map them to bf operations. this is hard though bc I either need exactly 8 parts (CMU has only 8), or harder, need to use a bf minimalization. i think this also loses information about the tree of a sentence (i mean, ig the tree is still necessary to create syntactically grammatical sentences which is great, so maybe moot point actually)
* could maybe do something like a pre-order tree traversal? the program runs in this order, and every time we hit a leaf, we do some corresponding operation based on what part of speech it is
    * this makes the tree structure more explicit but also helps us w problems like, "D must always preceed N". we shake up the order of the tree based
* maybe parts of speech aren't the "triggers", the bits that correspond to a program being ran, but the actual rules are. so if we decode a VP into (V AP) that has one effect, while (V DP) may have another
    * this might give me

* adjectives/adverbs seem the most unique:
    * can follow/preceed verbs and nouns (actually can't follow nouns...) and can "stack" endlessl
* a determiner must always preceed a noun. so if a determiner is present we know a noun follows. it's just possible though that the D might not be there, which does give us some control. I remember in NoL we had empty D on DP phrases (for examples, "Cats walk to school" has two DP's but no D'S).

ok, I think I got a pretty solid idea. To convert a sentence into a bf program, we first draw it's PSR tree (ambiguity will have to be handled later). We step down the tree and every time we use a *rule*, i.e VP: (V DP), we look up the rule and place down the corresponding bf operator.
Challenges:
* Assign rules to bf operators such that we have the most freedom in placing operators after one another in a sentence.  There are 8 operators, each can be followed by another operation, so there are 64 ways to go from one thing to another. We want rules such that we get as close to 64 valid ways to proceed.
* Convert a bf program to a sentence. Given a bf program as input, I want to construct a valid sentence afterwards. I think we could probably do this with metropolis hastings or something, or a greedy algorithm. We just start applying rules and continuing to create (maybe priotize this) as long sentences as possible. If we fail we backtrack to last valid sentence. If nothing is possible we can try doing some tricks like just incrementing, then decreming a cell (junk operations that don't do shit, but give us maybe more verbosity if needed).
To handle ambiguity we'll probably output sentences with parentheses around them for phrases. I think this method also gives us more freedom with writing sentences as programs as well. This has to be way more feasible than something like only 8 operators (although maybe as a result it'll be less interesting?).


I have like 16-ish rules rn with room for more. Current challenge, is how do we assign these things bf operators?
* For any bf program, I want to be able to make minimal changes to it, and still have a multitude of options to chunk it into sentences with it. I rarely want to be "stuck", when I have to change the program to continue, and if so, I want to be able to change it minimally.
* In a sentence I see "DP" and "VP" probably the most. "DP" must be followed by a "VP" in a sentence. There are many ways to do VP but fewer ways to do DP (unit, D NP, DP PP -- but also, NP can have AP's in it, and PP's can have DP's in a so it's more complicated)
## bf notes
* 8 operators: <>+-[],.
```
> = increases memory pointer, or moves the pointer to the right 1 block.
< = decreases memory pointer, or moves the pointer to the left 1 block.
+ = increases value stored at the block pointed to by the memory pointer
- = decreases value stored at the block pointed to by the memory pointer
[ = like c while(cur_block_value != 0) loop.
] = if block currently pointed to's value is not zero, jump back to [
, = like c getchar(). input 1 character.
. = like c putchar(). print 1 character to the console
```

* all [ must have a corresponding ]
    * i mean, [ could be DP and ] could be some kind of VP. then a loop is a sentence. but we also have to have nested loops possible...
* +, -, <, and > all need to stack *indefinitely*. this implies some kind of adjunction relationship in PSR

* ordered in terms of use: +->< / [] / . / ,
* , is used extremely rarely

* , should just be EXC, just knock that out of the way
* (VP adverb) is a good rule for something that happens rarely, or perhaps for ]
    * I could just add "," as a way to join sentences

## rules:
VP:
* V - sleeps
* `V_Transitive` DP - brushed her teeth, enjoy the music, pet (the cat on the wall)
* `V_Ditransitive` DP DP - leaves the doorman a note, finds him a job
    * again, this only works if the second DP has a determiner
    * "promise me the dog" is fine, but "leave the dog me" is not
    * - wait wait, this is a theta criterion problem. "show me the dog" and "show the dog myself" both work
* V DP PP - fits the key into the lock, pet (the cat) (on the wall)
* VP PP - sleeps (on the table)
* V AP - is hungry, seems smart
* VP ADVP - runs slowly, (fits the key into the lock) slowly
* ADVP VP - slowly runs, slowly (fits the key into the lock)
* V CP - thinks (that they left), believes (you left the doorman a note)

DP:
* D NP - the dog, the (blue car), the (big (blue car)), the ((very blue) car), her dog
* pronoun - we, she, it, they, I, Cassidy
* DP PP - the dog (in the house), `the dog (in_P (the house (on_P the street)_PP)_DP)_PP`
    * wait, this doesn't work if there is no determiner. "You (in the car) run" doesn't work for me, but idk if I want to clarify this with a rule for now or avoid it...

PRO:
* pronoun - we she, it, they, I, Cassidy

NP:
* N - dog
* AP NP - blue car, big (blue car), ((very blue) big) car

PP:
* P DP - into (the store), on (the couch), in (me), in (the house (on the street))

AP:
* (AP) A - big blue
* ADVP A - very blue

ADVP:
* ADV - quickly
* ADVP ADV - quietly early

TP (clause):
* DP VP - (He) (drives the car), (Fred) (said that I believe that he is blue)

CP:
* TP
* C TP - (that) (she walked the dog)

EXC (eclamative):
* EXC: Fuck, wow, super, oh.

## X-bar rules
I learned so much about X-bar rules to decide that while I could use it, I'm not going to use "VoiceP" as a solution for ditransitive verbs, i'm just going to encode them as a separate rule.

D - determiner
* DP: D'
* D': D NP - the dog, his (dog in the car), my dog
* D': NP - Cassidy, I, you, books

N - noun
* NP: N' - black dog in the car, really blue woman, young green fellow with the purple socks
* N': (AP) N' - (black) (dog in the car)
* N': N' (PP) - (black dog in the car) (on the road)
* N' N (PP) - dog (in the car)

V - verb
* VP: V'
* V': V' (PP)  - eat (with a knife), (eat the man) (with a fork), clings (to), longs (for)
* V': V' (AdvP) - leaves (quickly), (leaves early) (quickly)
* V': (AdvP) V' - (frequently) (leaves early)
* V': V (DP) - run, run (this house)
* V': DTV DP DP - give (the dog) (a bone)
* V': V CP  - believe (that the man is dead)

Adv - adverb
* AdvP: Adv'
* Adv': (AdvP) Adv' - unusually quietly, really quickly (doesn't sound good though)
* Adv': Adv

A - adjective
* AP: A'
* A': (AdvP) A' - very green, (very) (serious about her)
* A': A (PP) - green, serious (about her), afraid (of clowns), sick (in the head)

P - preposition
* PP: P'
* P': P' (PP) - (in love) (with her neighbor), (to the store) (on the corner)
* P': P (DP) - there, in (love), to (the store), to (the store on the corner)

CP - complementizer phrase
* CP: C'
* C': C TP - (*null*) (she is dead), that (she is dead), as if (she is dead)

TP - term phrase
* TP: DP  T' - he (the goes to the store)
* T': T VP - then (goes to the store)

Conjugation:
* XP: XP Conj XP
* X': X' Conj X'
* X: X Conj X


## more notes on arrangement
distribution of operations in `corpus.txt`:
```
+ 10.933919022154317
- 6.812213521772345
, 0.0035809778456837283
. 0.4426
[ 5.098118792971734
] 5.098118792971734
< 34.75100267379679
> 35.30127960275019
```
* surprisingly, `+` is used less often than I expected, and `<` and `>` are used the most, in about equal proportion. `-` is used rarely, almost just as often as `[` and `]` (used in equal proportion of course), and `,` is as expected used pretty much negligbly.

distribution of "run lengths", the number of times a symbol appears in a row:
```
> | avg 6.78
Run of length 1: 32.76%
Run of length 2: 14.24%
Run of length 3: 21.41%
Run of length 4: 9.72%
Run of length 5: 4.97%
Run of length 6: 1.40%
Run of length 7: 1.74%
Run of length 8: 0.66%
Run of length 9: 0.85%

< | avg 7.07
Run of length 1: 25.55%
Run of length 2: 18.46%
Run of length 3: 24.17%
Run of length 4: 10.32%
Run of length 5: 3.84%
Run of length 6: 1.19%
Run of length 7: 1.58%
Run of length 8: 1.09%
Run of length 9: 0.80%

+ | avg 3.366
Run of length 1: 85.15%
Run of length 2: 2.24%
Run of length 3: 2.06%
Run of length 4: 1.54%
Run of length 5: 0.81%
Run of length 6: 0.29%
Run of length 7: 0.15%
Run of length 8: 0.70%
Run of length 9: 0.55%

- | avg 1.43
Run of length 1: 97.05%
Run of length 2: 0.45%
Run of length 3: 0.47%
Run of length 4: 0.22%
Run of length 5: 0.25%
Run of length 6: 0.22%
Run of length 7: 0.12%
Run of length 8: 0.12%
Run of length 9: 0.17%

[ | avg 1.13
Run of length 1: 86.86%
Run of length 2: 13.14%

] | avg 1.019
Run of length 1: 99.24%
Run of length 2: 0.62%
Run of length 4: 0.02%
Run of length 6: 0.02%
Run of length 8: 0.02%
Run of length 10: 0.02%
Run of length 13: 0.02%
Run of length 21: 0.02% - lmao holy shit look at this one

. | avg around 1 who cares
Run of length 1: 94.19%
Run of length 2: 5.52%
Run of length 3: 0.29%
```
ok, so what "stacks" in bf
* > and < do, and stack the most
* + stacks somewhat, - stacks rarely
* [ and ] rarely ever stack, but it still needs to be possible to stack them without effects
    * again, these also appear with the same frequency, but, ] in rare cases needs to be able to stack for longer...


### recursive nouns
#### adjective stacking on noun (AP N'), right-weighted
*delicate large Canadian... woman*
LNR: A' AP N' A' AP N' A' AP N' ... A AP N' (N')
NLR: N' AP A' N' AP A' N' AP A' ... N' AP A' (N')

where A': A
AP: A'
N': AP N' except in parens

NLR allows us to just cycle `N' AP A'` arbitrary times, and then we end with any `N'` (in this case, `N': N`)

#### preposition stacking (N' PP), left-weighted
*((dog in the car) on the floor) with the tuba*
NLR: NP ...N' N' (N') PP P' DP D' NP N1' PP P' DP D' NP N1' PP P' DP D' NP N1'... PP P' DP D' NP N1'

where N': N' PP (except in parens, which is N PP)
N1' is an alias for N': N
NP: N'
PP: P'
P': P DP
DP: D'
D': D NP

NLR allows us to stack `n` `(N': N' PP)` rules in a row, followed by any `N'` (in this case, `N PP`), but then we have to follow with `n` cycles of `PP` treets, which in their typical form look like `PP P' DP D' NP N1'`

`--------------`

### recursive verbs
#### adverb verb stacking (AdvP V'), right-weighted tree
she *quickly deliberately early mournfully (runs|gives)*
LNR: Adv', AdvP, V', Adv', AdvP, V', ... Adv', AdvP, V', (V' (DP) (DP)) VP
NLR: VP, V' AdvP Adv' V' AdvP, Adv' ... V' AdvP Adv' (V' (DP) (DP))

where Adv': Adv
AdvP: Adv'
V': AdvP V' except in parens

NLR allows us to stack arbitrary `V' AdvP Adv'` rules in a row, followed by any `V'` rule

#### adverb verb stacking (V' AdvP), left-weighted tree
she *(runs|gives) quickly deliberately early mournfully*
LNR: (V' (DP) (DP)) V' Adv' AdvP V' Adv' AdvP V' Adv' AdvP ... V' Adv' AdvP VP
NLR: VP ...V' V' V' (V' (DP) (DP)) AdvP Adv' AdvP Adv' AdvP Adv' AdvP Adv'...

where Adv': Adv
AdvP: Adv'
V': V' AdvP except in parens

NLR allows us to stack `n` `(V': V' AdvP)` rules in a row, follwoed by any `V'` rule, but then we have to follow with `n` cycles of `AdvP` trees, which in their typical form look like `AdvP Adv'`

#### verb-preposition stacking (V' PP), left-weighted tree
*(((eat with a knife) in the kitchen) during the evening) before our dinner*
NLR: VP...V' V' V' (V') PP P' DP D' NP N' PP P' DP D' NP N' PP P' DP D NP N'... PP P' DP D' NP N'

where V': V' PP (except in parens, where it could be anything, or just V': V)
PP: P'
P': P DP
DP: D'
D': D NP
NP: N'
N': N

NLR allows us to stack arbitrary `n` `(V': V' PP)` rules in a row, followed by any `V'` rule, but then we have to follow with `n` cycles of `(PP)` trees, which in their typical form look like `PP P' DP D' NP N'`

`--------------`

### recursive adverbs
#### adverb modifying adverb
this sounds even worse if you do it more than twice
*really quickly*, *unusually quietly*
LNR: Adv' AdvP Adv' Adv' AdvP
NLR: AdvP Adv' AdvP Adv' Adv'
NLR: AdvP (Adv': AdvP Adv') Adv' Adv'

where Adv': Adv and AdvP: Adv
`--------------`

### recursive adjectives
#### adverbs stacking on adjective (AdvP A'), right-weighted tree
*initially unusually quietly blue*

NLR: AP A' AdvP Adv' | A' Advp Adv' | A' AdvP Adv'... A' AdvP Adv' (A1')

where AP: A'
AdvP: Adv'
Adv': Adv
A': AdvP A'
A1': A

NLR allows us to stack arbitrary `A' AdvP Adv'` rules in a row, followed by any `A'` rule


`--------------`

### recursive prepositions
#### P: P' PP (left-weighted tree)
*on (the paper on (the desk in (the room in (the house on (the street)))))*

NLR: PP ...P' P' P' P' P1' DP D' NP N' | PP P' DP D' NP N' | PP P' DP D' NP N'... PP P' DP D' NP N'

where PP: P'
P': P' PP
P1': P DP
DP: D'
NP: N'
N': N


NLR allows us to stack `n` arbitrary `(P': P' PP)` rules in a row, followed by any `P'` tree (here `P1' DP D' NP N'`, but then we have to follow with `n` cycles of `PP` trees, which in their typical form look like `PP P' DP D NP N'`

#### P: P' PP (right-weighted tree)
(((((on the paper) on the desk) in the room) in the house) on the street)

we can also reorder this so our trees branch to the right, not the left

NLR: PP P' P1' (DP tree) PP P' P1' (DP tree) PP P1' (DP tree)

which gives us the simpler recurrence, just `PP P' P1' DP D' NP N'` on loop
`--------------`

### recursive complementizers (/ everything, really)
*I belive (that she thinks (that we think (that the man is dead)))*
`--------------`

### recursive conjugation
#### adjective-conjugation stacking
*green and yellow and red and blue*

this one you actually get a couple of different trees depending on how you stack it, but as far as i can tell the same patterns:

LNR/NLR: A A A...
where A: A Conj A
for every "A" you get one "and", two leaf/head adjectives

head-conjugation is pretty good for something you need rarely, especially smtg like A Conj A. In the phrase, "the (yellow and green) man" vs "the (yellow) man", we get to insert the A Conj A rule anywhere after an A' for free
LNR: `D' (A) A' AP N'_{AP N'} N'_{N} DP`
NLR: `DP D NP N' AP A' (A) N'_{AP N'} N'_{N}`

Phrase conjugation in NLR can start anything as long as we have two of the phrases to back it up. But consider: if I could make two "neutral phrases", then any phrase conjugation would be a free symbol.
NLR: `DP_conj DP (rest of those rules) DP (rest of those rules)`

### misc notes
* again, just map EXC to `,` and be done with it
* it might feel beneficial to have `>>`, which is often "stacked", be possible to express with the simplest sentence `(D)_DP (V)_VP`. So both of these correspond to `>>`. Or honestly, maybe even do `(D)_DP (V (D)_DP)_VP` correspond to smtg like `>>>`.
