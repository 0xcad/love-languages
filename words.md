# words
the problem of filling a tree with words coherently

## rules
* can't use repeat adjectives in same noun phrase
* pronouns have to respect subject/object
    * You verb ME affectionately (me is object)
    * I verb you affectionately (you is object, same for subject)
    * I verb myself (reflexive)
    * You verb yourself (reflexive)
* verbs have to conjugate with subject
    * You/I has same conjugation, but "The noun verbs" is different

## ideas
words are given
* constraints
* tags
* for nouns: pluralization
* for verbs: conjugation

so for example, a preposition `PP: P DP` could be given the constraint `location`. then `P` has to use the word `in`/`at`/`on`, and `DP` has to use a noun that gets filtered by things at `location`1

adverbs to modify adjectives
* very, incredibly, intensely, beautifully, lovingly, totally, fervently

## thinking aloud...
### example rules
example (logical/tagged constraints): `PP: P DP` could randomly choose a constraint like `location`. then the `P` and `N` it chooses has to have the tag `location` in them

example (scope constraints): the rule `A': AdvP A'` has a constraint on it, or it's just, say, in the scope. so when I choose `Adv` I filter based on adverbs that are "aware" of this rule

example (repetition/word bank constrains): you can't use the same adverb twice in the same `AdvP: Adv'` (so you could use it in the same `AdvP` if there's, say, a `Conj`). Similarly you can't use the same adjective twice in the same `NP: N'`. So this implies that we have to choose adjectives without replacement from a pool once we see `NP: N'`, same with adverbs once we see `AdvP: Adv'`

example (weighted randomness): We could assign words iteratively rather than recursively to the entire tree of trees, then make some words more rare if they've already been used a lot. Weight inversely proportional to their appearance counts, or something, and maybe if I'm really picky some words don't get incrememented by a full `+1` after every time they've been used

example (verb agreement): once we fill the DP, we could propogate with what type (I/You/it) upwards to SP or smtg. Then a VP has an SP with a tag in its constraint (i.e, subject: you), so we choose the right conjugation for the verb.
* future determiners (say, after a TV or DTV) look up and see the constraint too
* second DP in a DP DP has to be  an object? like myself/yourself?

example (exclusive filters vs inclusive filters): maybe for some words if they can only get used if they fill a constraint. i.e adverbs to modify adjectives, "duck|dear|moppet" nouns, so we do an exclusive filter on them? or fuck, effectively that's just not putting them in with the other adverbs/nouns and giving them their own named category.
    * I think some adverbs can go in both normal adverbs plus adjective-adverbs

example (theme/agent/object): `longing|thirst` can't ever be an agent. Longing can't ever be that first DP in an SP: DP VP (i.e, "MY LONGING HUNGERS" is just wrong). First DP can have a variety of theta grid values but it's not object...

example (more DP agreement?): If we do "D noun verbs DP (DP)". If D starts as "Your" the next one is "My" and vice versa. "I care for *your* desire". also I think first DP should have a higher percentage to be "My" vs "Your", like 80 to 20.

idea: maybe we traverse the tree once first to add constraints, second to add words and then those words propogate their own constraints?

idea: we could sign off with "You are my <adverb> <adjective> <moppet|dear|sweetheart>. <adverb>, L.L"
    * easy to implement too, we just have that chunk be the root and leave everything a left remainder...


### etc
I just like the sentence, "You are my <adjectives> <darling|dear|duck|moppet|sweetheart|>". I think it's a *really* effective way to naturally pack in adjectives and likens back to Strachley. So maybe I create another class that I can memoize in my table, one that already has words/constraints filled in? So I could start with the tree "DP(You) VP(TV(are) DP(D(my) NP N' AP)..." and go from there? And the nodes "You/are/my" could be filled with tags instead of words?
* so it seems like we have two structures for `+-chain` rules, 'You are my <adjectives> <moppet>' and 'My <adjectives> <noun> <verbs>'.
    * I also see, "Eager longing burningly flirts" which is cool.

# 2025-03-17
for some reason `find_bf` seems to be logically correct, but the `ops_path`s of the trees change as we go??

DONE:
* fixed bug with `combine_weights` modifying input...
* fixed bug with weights not being inverted in our memo fn
* more planning
* choice search can now add to memo table

TODO:
* view that planning doc and start by moving `tree_to_words` to its own file...
    * and then maybe extend `TreeNode` again to have constraints/words in it?

# 2025-03-21
Goals again:
* verb conjugation - DONE
* subject/object - KINDA DONE?
* noun agreement - DONE
* switch between "your" and "my" in sentences...
* pool of words for certain phrases (i.e adverbs in AdvP, adjectives in NP (not conj...), nouns in `DP`)
    * adverbs in AP's also need to be different
        * adverbs in AdvP that are modifying *another* adverb need to be the same class
* (less important) theta grid
* "You are my.... `blank`"
    * on a tree, need to also save:
        * word
        * word subcatagory ("moppet", "baby", a pet name)


agreement:
* sentence starts with `SP: DP VP`
* case first `DP`:
    * `DP: DP Conj DP`: recurse on second `DP` here
    * `DP: D NP`: "it" subject, add `person: third` tag to current node and `SP`
    * `DP: NP`: plural subject, add `pluralize: True` tag to current node and `SP`
    * `DP: Pronoun`: do an 80/20 chance of filling with "I/you" and save result
        * add `person: first` or `person: second` tag to current node and `SP`
* now, start at `SP` again, and traverse `DP`, filling out words respectively
    * we start at root in case we recursed on a `DP Conj` rule
* when we're done we just go to VP. when we get to a `V` leaf, we look at all the constraints and conjugate/pluralize as needed
    * TODO: what does this look like? because I'm sure I can get a general function wherin I fill in constraints, and then...

TODO: what do we do next time we see a `DP`? because that `D` is either going to be "you" or "my"
    * idea: add a `possesion: first|second|third` tag to represent this? pass up to parents as long as parents don't have that info
    * then when we add a `D` later we see `posession` is in the parent list of tags, so we can do probability for like, not doing that...

If I see a `DP: DP Conj DP`, I want to make it so the wordbanks for `Pronoun` and `N` draw *without* replacement. However I only want that change to happen under this scope. How can I do that?
    * I could make a tag on just this level for like, "replace noun: false, replace pronoun: false". I copy the wordbank. I process left/right/third branches, then afterwards, I make the word bank what it was originally....


# DONE
* created function to turn strings into trees (for, "You are my `blank`" tree)
* modified `get_neighbors` function to accomodate for partially complete trees
* modified `heuristic` function to be more accepting of "possible" solutions" by allowing us to skip one `NONE` in solns...
    * this yields slower times but in certain cases, more optimal solns
* fixed a bug in `find_bf` logic -- now correctly invert bf strings

* verb agreement is done
* noun pluralization is done
* pronoun accusatives if in DP

* bug fix with words not being deepcopied
* created new WORD class
    * word equality is based on the root word it's given
* logical bug: RAPTURE OFFER YOU MY ARDOUR.
    * fixed! subject agreement works now
* posession/pluralization alternation - DONE
* word pools with replacement - DONE

TODO:
* "You are my"...

word pools with replacement: - DONE
* if we go under a
    * `NP` -- draw `A` with out replacement
    * `DP: DP Conj DP` -- draw `N` without replacement
    * `AP` -- *restrict* what `Adv` we can draw
    * `Adv': AdvP Adv` and we're in left child -- *restrict* what `Adv` we can draw
idea:
* we have a set of leafs in WordBank for if we should do without replacement for a node. if we change this, we make a *copy* of that table entry (that's our destructive shit). otherwise we just use the original list. at the start of each node we call `WordBank.refresh()`, which sets replacement nodes to be their original values
* `WordBank.refresh()`
* `WordBank.replacement_set`
* `WordBank.add_replacement_map(leaf)`
* and then also modify `fill_word` to use the replacement map ofc
* modify `_select` ofc
