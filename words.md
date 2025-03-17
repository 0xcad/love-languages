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
