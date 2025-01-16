a continuation of the `README` document focused on stacking rules

* very important to stack: `> < + -`
* "reversible": `> <` and `+ -`
    * "collapsible" strings: `++--`, `><`, `>><<`, `>>+<<>>-<<`, `+>-<->+<`, `++>-<->><+<--`

goal: assign rules in a way that I can stack `> < + -` with relative ease and minimal effects. `][` still need to be able to stack (at least in a theoretical way). `,` I'll definitley deal with outside of PSR and `.` I'll maybe try to find a way to include
* I think the absolute, number one goal, the best metric for success, is that **the length of the text conversion of any problem should be as small as possible**. If I nail this I think everything else may follow
    * which implies: we have to make stacking as efficient as possible, pretty much.
    * observation: bf programs can be significantly "compressed" by reducing all chains of symbols to just that symbol, followed by the number of times it appears. similarly, if we replaced all instances of `+++` with like, just one symbol that meant `+3`, and then used `-` or `--` afterwards to control the remainder -- that's *still* shorter. therefore *it really behooves us to make one word correspond to multiple symbols, when appropriate* / if possible.
* for a secondary, aestetic goal:
    * longer sentences in strachey: `D (Adj) N (Adv) V (P) D (Adj) N`
    * shorter: `N V D N`


left-weighted trees:
* start with an `XP`, `n` copies of `X': X' YP`, any terminal `X'`, then `n` cycles of `YP` trees

right-weighted trees:
* start with an `XP`, `n` copies of `(X': X' YP) YP-tree`, any terminal `X'`

## most likely to follow:
`-`: `] - [ > <` (less likely to stack, actually, but not by a big margin)
`+`: `+ > < [ ]` (stacks extremely heavily)
`>`: `> + [ - ]` (seems to stack heavily)
`<`: `< + - [ ]`
`[`: `- < > + [` (pretty even for `- < >` then drops off)
`]`: `< > ] +`

## assignment

conclusion to this: don't think adverbs should map to `]`
* I think, because it's rare that this is needed, and because it sounds strange, I'm going to make adverbs correspond to `]`. This can stack but also, why do it more than twice?
    * means `Adv': Adv` corresponds to `]`, and `AdvP` and `Adv': AdvP Adv'` mean nothing.
        * or means `AdvP` and `Adv': AdvP Adv'` are neutral
    * straight up makes all adverbs equal to `]`, which maybe is bad actually
    * `[-]` is pretty common in bf, what if `AdvP` was `-`? That would require a `+` before it if we wanted to use it "neutrally", but makes an adverb equivalent to `-]`.
    * ehhh... at the end of the day, I do think adverbs should be able to stack more

conclusion to this: `(N': AP N'), AP, (A': A)` all `+`, two/three of `A': (AdvP A'), Adv', AdvP` are `-`, third neutral
    * two of the three Adv/A rules have to be `-`, other has to be neutral, if I want to change in the future
    * this gives us `+3` stacking, a way to get any multiple of `+` by inserting adverbs, and paves the way for `-` stacking with adverbs
* `+` stacks can get pretty long. what if we made `(N': AP N') AP (A': A)` -- all the rules associated with adding a single adjective to a noun-bar -- equivalent to `+`. so in essence an adjective becomes three `+++`.
    * see above, this is a great idea
    * adjective stacks are always followed by an `N'`. We need to make it so that that `N'` can contain enough `-`'s to set a "remainder" for the `+` sequence, which means 0-2. `N'` rules remaining are `N': N`, `N': N PP`, and `N': N' PP` (so head, head and preposition, and `N'` and preoposition)
    * `N': N' PP` allows us to potentially introduce more adjectives if we want, or switch to recurring on prepositions. `PP` allows us to have other rules to recur on propositions
    * options that give us a *choice* for the remainder:
        * woman (in the car), woman (in the car) (with the hat)
            * options: can either have PP be net negative, `N': N PP` and `N': N' PP` net neutral
        * complement/adjunct distinction: woman (of science), woman (in the car)
        * woman (in love), woman (in love with her neighbor)
    * alternatively: we can just add in an adverb on an adjective, then leave nouns and prepositions to fuck around with later. this gives us `(A': AdvP A')`, `AdvP`, and `Adv'` to play with. we have to make two of these `-`, one neutral. I vote `A': AdvP A'` and `Adv'`

conclusion:
    * set `AdvP` to `-`, `Adv': AdvP Adv'` to `]`, and `AdvP Conj` to `++`
    * having conjugation "cancel out" the things it connects is a really good idea
    * phrase "(really and truly) quietly" encodes `-]`
* but now though, going back to `-`, it seems like `-]` is even more common than `--`
* but anyways... currently an adverb phrase in isolation is just one `-`
* with adverbs, I have two `V` rules. under NLR I cannot make smtg like "quickly run" lead into `-]`, (`]` being with `V': AdvP V'`), but I could with LNR. using LNR also won't jeopordize the above rules, but it could make other parts of way harder...
    * **LNR with right child:** wait wait... I could also make it so that if a node has only *one* child, it's a *right* child, which kind of already gives me the benefit of NLR for phrases?
    * I know `-]` is technically more common, but if I do that verb rule then this only allows me to stack `-]-]`. is that worth it? doesn't seem like it.
* oh, potentially easy, just do `AdvP: AdvP Conj AdvP` to pull this off? that rule can be `-]-` (LNR), and then we add smtg after it?
* better, we could just do adverb phrase stacking to get `-]-`?
    * ok, so I think this means we use NLR still, have `Adv': AdvP Adv'` map to `]`, and `AdvP` map to `-`. we use right-weighted adverb trees (those are most nautral anyways), and smtg like three adverbs stacked together like this yields `-]-]-`
* problem: now I can't get to just `]`. I can do `+]` with "((unusually and serenely) quietly) and (quickly and speedily)". I can do `+]-` with "(((unusually and serenly) quietly) and quickly".
* solution: set `Adv': Adv' Conj Adv'` to be just `+`. Then "((quickly and quietly) fluidly) and serenly" is just `]`, which is really awful, but that does work

conclusion: changed some rules and switched to LNR
    * also: turns out `[-[-[-`... is actually fairly common, so having that stack would be great
* I've decided to switch to LNR, I think. I think this will make `[` simpler, but also, maybe be more "honest" with things like "and" across a long sentence?.
    * "really quickly" encodes `--]` (and note that `[--]` is equivalent to `[-]` in bf... uh, if we don't underflow, uh oh)
    * "truly and (really quickly)" encodes `-++--]` or `-]`
* ok, scratch all of the before, what if I set `AdvP: Adv'` to be `null`, `Adv': Adv` to be `-`
    * `Adv': Adv' Conj Adv'` encodes `++`
    * AdvP: "really quickly" encodes `-[-`
    * AdvP: "truly really... quickly" encodes `-[-[ ... -[-`
    * AdvP: "really (quickly and serenly)" encodes `-[`
    * AdvP: "(quickly and quietly) (serenly and solemnly)" encodes `[`
    * `AdvP: AdvP Conj AdvP` is null, which lets us stack `[[`

conclusion:
    * in progress
* per, now we kind of have `+-[` somewhat handled, I think the distribution so far is fair game, too; `+` is most common in my corpus, stacks the most, then `-` shows up like 11% of the time, `]` 7%... I might have to tackle more of these cases later as well. but now let's think about `>` and `<`? have determiners, nouns, verbs, prepositions, and need `><]`. Could also do smtg with S ("I tell her" vs "tell her", no DP required). Also, note that you can always move an adverb to the start of a sentence, i.e "quickly, I run there", which is just movement on "I run there quickly" and "I quickly run there". I know that this is movement, but I can probably bend the rules and just have `S: Adv , S` be a rule as well
* I have the rule `DP: Pronoun` now which is cool, but also somewhat limited bc it can't be modified by adjectives
* just to start: let `DP: Pronoun` be `>`, `DP: DP Conj DP` `<<`.


* consider stacking `>` with prepositional phrases. a typical PP ("in the house") is three words. If something like the D/N are neutral, then to pull its weight a preposition could be like, four symbols. then I need something for `<` that's worth three symbols, right, and that's how I get my one.


## misc
remember, smtg I forgot earlier: determiner phrases don't have to have a D in them (in the case of a plural subject, or pronoun/name); and conjunction still exists

### rules
N - noun
* NP: N'
* N': AP N' - `+`
* N': N' PP
* N': N PP
* N': N

Adv - adverb
* AdvP: Adv' - `null`
* Adv': AdvP Adv' - `[`
* Adv': Adv - `-`
* AdvP: AdvP Conj AdvP - `null`
* Adv': Adv' Conj Adv' - `++`

A - adjective
* AP: A' - `+`
* A': AdvP A' - `-`
* A': A PP
* A': A - `+`
