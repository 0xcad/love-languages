# search
the problem of finding our traversal

### more notes:
caching nodes
* observe that if I throw out that `path_ops` thing (this could just be an external variable anyways it seems) then all nodes in the graph are equivalent under these values:
    * commitments array, the current rule, if it's a choice node or not, and force recurse right
* so instead of having horrible memory complexity, I could just start hashing nodes and stick them in a lookup table (perhaps of fixed size), only generate new nodes when they're not in the table, and then put them in the table. this is pretty much just how a cache works, that's my node cache.

low hanging fruit improvements to A*
* the real cost is words. it's words, it's words, so go back to using `word_cost`
* A* shouldn't overestimate the actual cost, so we need to lower the values in our heuristic
* it should be more beneficial to eliminate characters from our string, than to produce extra characters that we need to undo. therefore, the negative weight of the size of `undo_ops` should be *less* than the negative weight of what's remaining

improvements to A*
* A* feels really, painfully slow! the intuition is, shouldn't it get *faster* the longer it runs, as the algorithm becomes more acquainted with a graph that is so similar? this begs of memoization / a DP approach.
* first idea:
    * whenever we're at a terminal node, we look at the current sentence so far, and we memoize it. we save it's true cost (the number of words in it) and the operations in it's path.
    * we're still at a terminal node. we add all of the items in our memoization table as neighbors. these are like, "super nodes", where if we go to one of these it represents  going to a ton of things all at once. we treat their entire ops string as a single operation/rule to add, then apply the same heuristic to them.
    * observe that we can take this even further: we don't have to do entire sentences all at once, we can go to the prefixes of any sentence as well
        * this does feel like comparing prefixes across all other prefixes is costly though...
        * I mean, we can go even further. we can collapse nodes into chunks at all points, not just terminal points, memoize them. then in our `get_neighbors` fn at a given point -- we can maybe look up the memoization values that are "legal" from where we are
        * to get legal values -- we get all of the node's actual neighbors, and find all prefixes/infixes that start with the same rules as those neighbors? no, we have to also check the current scope/commitments. here's a counterexample for otherwise, consider the case where I'm looking for a "PP" rule, "I run `PP`". I see the `PP` infix "in the yellow hat gives the monkey a bannana", I can't add that.

^this still implies memoizing infixes / phrases
If I see the sentence, "The man in the yellow hat gives the monkey a bannana", I can memoize or utilize several things:
* "The man in the yellow hat gives the monkey a bannana" (S)
* "The man in the yellow hat" (DP)
    * "The man" (DP)
    * "in the yellow hat" (PP)
        * "the yellow hat" (DP)
            * "yellow hat" (NP)
* "gives the monkey a bannana" (VP)
    * "the monkey" (DP)
    * "a bannana" (DP)
I guess it feels unrealistic to save anything that's only one word

If I save the smallest chunks first, the bigger chunks can just point to those in memory
* oh fucking christ this is just the binary tree (!!), and I'm just saving all nodes whose left and right trees sum to more than one word
    * somewhere in here there is a beautiful symmetry to linguistics -- holy shit I'm so tired but I see this and it's almost unreasonably beautiful; so in x-bar we can replace phrases with any other phrase of the same kind. I want to propose a type of graph search, where at each node, we save all the ways to make that phrase we encountered so far. then our neighbors -- are all of the combinations of phrases we've seen so far.
* and I suppose there's some lookup table where I can get an option of phrases at each level


so I guess first steps:
* make it more memory efficient with hashing nodes...
* tweak just the weights, so if it improves?
* lowkey a test file would be goated, just a couple of goal phrases, the time it takes to compute them, and their cost...
* first step for memoizaiton:
    * at each exit node -- memoize everything in the scope above, and it's path ops. you will need to figure out how to build the binary tree as you go (consider the case of memoizing the node `N': AP N'`...)
    * modify `get_neigbors` in the graph finder. whenever I see a `target_rule`, look it up in a dict, then return the set that should be all memoized options of that rule...
    * you can probably start memoizing by building up from leaves all trees of a fixed height, then go from there...

# 2025-01-30
first goal: hash nodes, and make `ops_path` something we store later
* modified `cache` of search nodes to store the `ops_path`


### rule order search
the problem with the previous astar algorithm (sentence order search) is that essentially I just have to "get lucky" to find things. and memoization helps me avoid incurring that cost every time, but it's still there. assume I had a operation that was only in a single rule. then I shouldn't be stumbling along a graph, I should know exactly where my operation will build, start with that, and work outwards.
* `<<+++` would be very hard for sentence order, becuase it has to go "the wrong way" for a long time

idea: if I'm looking for `+++++` or smtg, my starting place should be all nodes that contain `+` ops in their rules. then I need to work my way down the tree from those rules to the leaves. if I add a rule like a `<<` somewhere in between, then I need to recurse for the reverse of that
* generally, I think my starting place is actually all rules, my search will just prioritize the ones that have a `+` in their ops.
* if I have my substring, then I want my search to look for `null` rules or nodes to fill in the gaps
* build down first, then up
* in building up, if I run into any rules I *don't* want then, I want to look for an offset. if I have a complete tree I get to start again from any rule, which is quite powerful i think.
* this does not use the in order tree traversal from before.
* infinite, negative loops are still going to be possible -- but the goal is that my priority queue will see how many words they're taking, how far away they are from the queue, and just avoid that.
* I can still do memoization, I can memoize trees that are built all the way to the bottom. in the future, when I'm searching for the bottom I can use these.
* when I'm back to building the tree up again -- this is just going to switch to building back down as soon as I add any height, so I'm fine.
    * it becomes even more important then that A* heurisitc doesn't overestimate my path, that it's admissable, bc otherwise I'll get shitty results as soon as I bake in memoization

consider I'm looking for `+++++` from first principles
* what are the rules that even have `+` in them?
    * `N': AP N'`: `+`
    * `N': AP A'`: `+`
    * `A': A'`: `+`
    * `Adv': Adv' Conj Adv'`: `++`
    * ^these are open in our priority queue

tbh that `Adv'` rule probably looks like it's the best to start with bc it has the most of what I want.
* so I look at `Adv'` rules. are there any that have `+` in them? yes, `Adv' Conj`, that's great (rip)
* [1] I stick `Adv' Conj` on the left of this thing to get `++ ++`, still short so I stick `++` on the right to get `++ ++ ++`
* now I'm looking for `-` on either the left, or right side, and then `null`
* start on the left, can I get `-` ? yes I can, that's `Adv': Adv`, so now I have `-++ ++ ++`
    * note: I collapsed that space bc `Adv'` is an exit node
* at this point I have my goal, so I'm looking for `null`
* I don't see any `null` `Adv'` rules though. so what, I just pick between throwing down a `+`


misc notes while I'm doing this
* [1] I should probably do a BFS on the depth to build this up...
* if I use a priority queue this will help build up memoized entries as aI go

more notes:
* consider the rule `S: S S` for connecting sentences, even if I don't have to actually introduce it. I think this gives me intution that sentences are inherently special, they're just particularly recursive. maybe whenever I run into *any* error that I need to undo, I start a new search just for that error?
    * uhhh there should be a max depth on this...
    * ^but smtg *like* that would allow me to do really well in terms of finding phrases to memoize...
* let's say again I'm looking for `<<++++>>>`
    * wait, do I start looking for `<` or `+`?
    * what is the actual path? it could look like `<<<< (you and I verb. my nouns verb.) |>>--++++++<(The very lazy dog)>(runs.)|>>> (my nouns verb for your noun).`

## 2025-01-25
assume for the sake of algorithm design that the problem of converting a bf sequence into a collection of sentences that perfectly minimizes the number of words, is an O(n^2) problem.

then observe that I can solve the problem of finding a "good enough" shortest path in anywhere from O(n) to O(n^2); I can just divide the input bf sequence into smaller components of a *constant size*, solve each of those constant size problems in O(c^2) which is a constant, and then string them all together in O(n) time to get a final solution. so if I accept imperfection it's linear, with a constant proportional to how much imperfect I get.

DONE: added caching on tree notes

# 2025-01-31
TODO:
* add memoization to phrases, and put those in the tree
    * on the heuristic function, detect if a node is an exit node
    * if it's an exit node, then we need to follow a series of `came_from` nodes to reconstruct the tree. write a function to do this
    * write a generic class that will take objects, and store them in a binary tree. use this above
    * memoize all the ancestors of the exit node and their completed trees
    * in the `get_neighbors` function, look at the node's current `target_node`. add all of the memoized neighbors that we saw earlier
    * experiment with a variety of things, including if we memoize small trees first and then do the search, the max depth of memoization for trees (that might be really important), a more efficient way to tell if a tree is complete. we'll probably need doubly linked trees, too I'm guessing...

DONE:
* added caching on graph nodes
* reorganized rules and rule trees

building trees in graph searches:
* I think every search node has to have its own tree, unfortunately
* the data in trees are rules
* oh wait wait we can do this better. each nodes tree is the same as the prev one? that lowkey doesn't actually work though because of backtracking... but hell, I'll just try it anyways and if I have to use copy then so be it
* we probably have to do the same stack thing, where we keep a stack of all trees

I forgot we have more information available to us:
* if an element is a force recurse right node, don't put it in the tree
    * lemma: there can only be one FRRN in a tree at a given time? yeah that seems right
* if the previous element is a choice node, put it to the left of the prev element tree
* if the previous element is FRR, then go up in the prev tree until there's a valid spot ot insert, insert it there (which will be on the right)
* otherwise, insert it as the right child as the previous tree

TODO: fix copy function, reason over changing the tree parent's children when we do "came_from" (it's confusing, whatever...)

# 2025-02-01
I have a theory that I don't need to ever make a `copy` of the tree -- but I do need to make copies of the pointers at each element. each node points to where in the tree it lives, and we just re-write the tree on backtracking. to be safe with this, at each node we should also set the left/right children to be None or something, if they're truthy, before doing any operations...
* plan: each node stores a pointer to the current value of the tree

* problem: it's possible to "knock out" a tree during backtracking. for example, we go to `N': AP N'`, we backtrack to `N': N` (and replace `N': AP N'` as desired, good), but then we decide to stop searching *that* one too and come back to `AP: A'`. `AP: A'`'s parent is `N': AP N'`, as desired, `N': AP N'` has the right parent, as desired, but now `NP: N'` has `N': N` as its child, which is wrong...
    * soln: uhh, just let it be, but then when our tree is ready we climb up `parents` and set all the children as desired. requires our doubly linked tree knows not just which parent is has, but if it's a left or right child
    * we only need to do the solution once, when we create our node (which is perfect because we have to climb up the tree anyways). however for debug printing sake I'm going to do this tree climb thing every time

ugh, left recursive rules are awful. we need to go back up the tree, and insert them in between two other nodes. however, if we backtrack away from them, then we need to undo the whole thing...
* can I just copy the whole tree on left recursive rules? I still need to do insert though, which will suck...
* ^done that, but I only copied a subtree. anyways though, another problem, that I'm not sure is dependent on left recursive nodes or whatever...
    * the previous solution, where we climb up `parents` and correct children, works great. except it can only correct up to descendents of parents. if we backtrack up and a node is like, a cousin of another node, the cousin could be wrong.
    * so still, if we go to like, the right VP, then backtrack so we're back on the other side of the tree again, our tree is incorrect

TODO:

DONE:
* reorganized more code
* fixed earlier hashing function
* made good progress on constructing trees as we go in our graph (that's what cache is for now)
* fixed a hashing bug by wrapping graph nodes in another class

# 2025-02-02
TODO:
* memoization at nodes still, we're on that beat.
* now add in memoized nodes to neighbors
    * update GraphSearchNodes to take them
    * update neighbors function -- either start recursing right, start a new sentence, recurse right elsewhere, break those cases up
    * update the heuristic function to use `path_ops` if a node has a tree

DONE:
* fixed a bug with DTV DP DP, simplified cases in GraphNode neighbors...
* started memoizing trees
* wrote code to memoize all possible trees of fixed height
* reorganized code


# 2025-02-07
what are the neighbors when a memoized tree is inserted?
* if the tree fills in the right child, we need to essentially just recreate the rightmost graph node. we go right, each time storing what we make in our commitments list. we merge/append this new commitments list with the commitment list of whatever we came from
* this implies that tree search nodes need to know the gn that spawned them
* if the tree fills in the left child, we want to insert a FRR graph node of the choice node that spawned it. copy graph node, pop most commitments, FRR

* ^oh, sike, these are just the same case. we still want to recreate the exit node, my other code will handle it for us from there

DONE:
* started adjusting graph search nodes for trees
* modified commitments to get tree neighbors

IN PROGRESS:
* add trees to graph search node trees...
* finish modifying graphsearchnode with trees...

TODO:
* modify commitments to treat the spawning node differently, it should really be in like, it's own spot or smtg. but yes, arguably I don't want to have triple nested arrays...

# 2025-02-08
bug: I think the tree, that we have to point forwards to in `current.cache` (whenever we insert a tree) has to be its rightmost node
* in the process of fixing

another bug:
* somehow the `correct_parents` thing is *not* working
* one node is being set to be both the left and right child of its parent. worse, this is happening for every node in the tree. specifically, the right child is becoming both the left and the right child....
* which is because both is left child and is right child is set, which is so wrong

* ...and the bug is happening because in our tree memo process, some trees are set to be both left and right children

another bug:
* if we came from an exit node, the next tree that we insert could be a child of a FRR node -- i.e, we go back up the tree
* in this case, if we insert a FRR node we need to set the the current pointer to be where the tree is? this also solves our `insert_left_recursive` or whatever problem i think....

another bug:
* looks like on some rules with third children, they get set both as left children and third children. similar error to what I had before with right children but I know that part was fixed during tree memo...
* this happens with rule `DP: DP Conj DP`, a rule that itself has a third child...
* when `insert_right` sets it to be a third child -- I see that it's already a *left* child, which is problematic

another bug:
* somehow `is_complete` wasn't getting casted to a bool

what the fuck, it's significantly slower with memoization `T_T`
* by like, a significant margin, 0.037s without to 0.6s with
    * that's for the string `++++++`

another bug:
* finding FRR node is sometimes None?
* this is happening with `A': AdvP A'`
* this is the offending tree, as you can see the `A': A 26096` got inserted as a sibling of `A': AdvP A'`, not as its left child
* we're looking for a `A': AdvP A'` from `26096`
```
* `AP: A'` 26624 -> parent `N': AP N'` 26800 (incomplete) True None None
> leaf
> `A': A' Conj A'` 26272 -> parent `AP: A'` 26624 (incomplete) None True None
  * `A': AdvP A'` 26448 -> parent `A': A' Conj A'` 26272 (incomplete) True None None
    > incomplete
    > incomplete
  * leaf
  * `A': A` 26096 -> parent `A': A' Conj A'` 26272 (complete) None None True
    > leaf
    > leaf
```
and this is part of the path
```
Path (reverse order):
`A': AdvP A'` || `A': A` || `A': A' Conj A'` || choice node: `A': AdvP A'` || choice node: `A': AdvP A'` || `AP: A'`
```
that's really fucked up, that shouldn't ever be an option
wait i modified the path print function we got this instead now
```
Path (reverse order):
`A': AdvP A'` || `A': A` || `A': A' Conj A'` || complete AdvP: Adv' tree || choice node: `A': AdvP A'` || `AP: A'`
```
* hey where even is that `AdvP` tree? I don't see it
* tracing the path:
    * we successfully insert that AdvP, everything looks great, but then we insert the `A': A' Conj A'` (an option we can legally get to from the exit node of the `AdvP` tree)
    * this is where the error happens though, we insert the `A': A' Conj A'` rule and now we *lose* the left child of the `A': AdvP A'`. I bet the parent pointer is still set, just the left pointer got unset
* ok, I fixed the problem where we lost the left child, lowkey our tree still looks correct but we're getting an error
    * one problem though is OHHHH
* problem: it's a problem with the commitments of the rightmost child
    * we *shouldn't* have the option to go to a `A' Conj` rule, we should be going to a FRR `A': AdvP A'` instead. there must be a problem with the spawning node then

bug with commitments:
* the spawning node is already in the commitments, no need to put that back in there

^turns out it was a bug in commitments, and in the `get_neighbors` function of graph nodes

parent_tree/tree is the Adv' node
* node is the A' A' conj A' node
* target rule is A'

still significantly slower with memoization `T_T`
* 0.1057s without to 1.257s with for `+++++`
* 23.405s without to idk really long, too long for `>+>+++>`
* 42.749s without memoization for `>+>+++>+++++++>++++++++++<<<<-`
    * after I got rid of tree generation stuff, which is pretty good
    * tbh I think I got ludicrous time savings from when I first started, just by caching graph nodes and rules

TODO:
* experiment with seeing if it's possible to get the program to use memoized nodes in its execution, I feel like that should be faster but it's really not...
    * anything using `[` and `]` is going to be a nightmare, I feel like I should just use memoization for that...
* consider just moving on to next idea for graph search

spending a lot of time on copying trees, maintaining that list, etc with memoization...
* str commitments
* copying trees fs

observation:
* in `>+>` with memoization, in our final path we never actually used a memoized tree
* neither in `+++`
* if we make it cheaper to use trees, we just take longer and still don't use them

DONE:
* created a checker for the correctness of trees
* fixed a bug with tree memo process creating incorrect trees
* fixed a bug with inserting trees after FRR nodes
* fixed a bug when memoizing new trees that shouldn't have had child attributes
* fixed a bug where `is_complete` wasn't getting casted to a bool
* fixed a crazy bug with generating new commitments as well as getting neighbors...

# 2025-02-10
ideas on how to continue:
* modify the function to memoize trees only when we're at an exite node, i.e to reconstruct them from the path, not as we go
* analyze why trees are *never* getting chosen as paths.
    * only memoize trees that show up in our final path
    * rerun a search algorithm with those trees, do any get used? I feel like it has to be a problem with our search

ok, so my path thing was actually incorrect, we *are* using memoized trees
* furthermore, if we don't memoize as we go, it does take *longer* for us to come to an answer, for `>+>` it's a difference of 3 to 13 seconds
* the paths that I'm seeing with and without memoization are the same
* but really and truly, at the end of the day even with memoization I can't see this strategy ever actually working, so I think I'm going to scrap this -- but take all that I learned from it, which is a lot -- and go with my tree approach

## tree search:
### neighbors
* when we start searching, every rule is available to us as a node/neighbor
    * minutia: somewhere in here there's some nuance about left recursive rules ??
* once we pick a node/neighbor, the next neighbors are all the rules we can use to complete the current tree. we travel *DOWN* the tree.
    * minutia: is this BFS or DFS? probably BFS, I would assume, so we pick the node that has the least depth that has an incomplete part and recurse on that
* once a tree is complete, we travel *UP* the tree until we get to `S: DP VP`

once we reach the root, we take whatever, idk, "productive" part of the path we find, the substring that exists in the bf code we're looking for, and calculate the "remainder" of that. we split the bf program around this, add the relevant remainders, and recurse.

### heuristic
* we look at the *entire* program
* we compare the current bf program being generated to the entire search program, the score is how much we have that's contiguously similar (this lowkey seems pretty expensive, but I claim we can chunk up a bf program into regions of constant size)
    * we weight "rare" things. for example, if we have a `]` or `[` that should be so much more valuable than a `>` or `<`. So maybe not "rare", but things that we think will produce a significant remainder
    * we could potentially do even better if we acknowledge that our tree has "gaps" in it. so for example, we insert a "space" where incomplete nodes are. then "++ >>-" could map to "++(+>)>>-" with probably some negative weight...

### memoization
* can access fucking anything we want, at the start of a program, in our table, or "target rule" trees as we go
* I could probably do something smart to limit the size of my memoization table. I memoize everything, but when I pull neighbors, to decrease the branching, I only look at a constant number of the most "popular" trees. the trees that have been used the most. this creates a positive reinforcement effect, so if I ever use a tree that's *not* popular, i.e I recreate it, then I give it a boosted count whose size is proportional to the constant number of trees in my memoization set

### advantages
* this just seems so much more "rule aware". if I have a `]` otherwise, first I have to search through every possibility of useless shit that I can see before I get to `]` and start moving forwards with that
* this respects the idea of "remainders". to continue the `]` example, in the graph search program I have to arrive at `]` already "neutral". Again this is *so* incredibly against what our heuristic function wants us to do, this is never going to happen. but my rules are set up so that ideally, the size of remainders needed will always decrease, which pretty much means that programs and their representations are finite
* it's symmetric in terms of remainders, which is nice, they can happen on both sides of a desired rule
* this builds the trees as I go, which feels like a more honest representation of the final product than the graph search thing (although conceptually, graph search was just really fucking cool as an idea)


copying nodes:
* when we produce possible children to go to, we always set their parent. however, we don't set the parent node's, say, left pointer, to go to
    * when we choose a child, we do set the parent's left pointer
* when we produce possible parents to go to, we don't set the current node's parents, but the do set the new node's children
    * when we choose a parent, we do set the current node's parent pointer

LCS with wildcards:
* i.e [...+ + None > > - >...]
* TODO: figure this out, lol

TODO:
* probably need to start doing copies on tree search, that looks super fucked up right now...

DONE:
* created `choice_search` method for new tree search (no memoization for now)

# 2025-02-16
debugging shit

we choose `D': NP` which our algorithm seems to like
* we add an NP: NP Conj NP on that. however that's no good, we backtrack and try `NP : N'`
* so *ideally* we would have `NP: N'` being inserted as the *right* child. however now we end up inserting on the *third* child, so the `D': NP` still has the `NP: NP Conj NP` on it

so when we go back to a new neighbor, I guess before we add anything we need to *clear* the space, or just start replacing roots
* I guess -- backtracking should remember where a root has been, when we add it? at least if we're growing down. so maybe -- we add a node, we remember it's children.
* this only happens if we backtrack, so like, neighbors are already called. I think we can do this in the path heuristic function though?
* oh, shit, here's a potential problem. because we're doing "yield from", the neighbors function is getting called with the *current* tree every time?
    * yield i think is still lowkey better from a memory perspective but what do I know
    * yeah already that seems to help shit, but we also have a problem now in that if I have both left and right children available my tree still might not work, so I should go through with that prev idea
* this will produce more problems still. imagine if we add a child node A, add a few more parents to the root, then backtrack to use child node B instead. the tree will now have those parents added, which is wrong. so perhaps a node needs to remember its root, or a search node needs to inherit the root of its parent, unless we're adding another root?
    * this does give us an easy invariant though, that the number of nodes in a tree should be equal to the number of items in the path, and if that's not true we fucked up somewhere

another bug: - FIXED
* trees aren't being listed as complete if they actually are... fixed?
* NONE's are being canceled out when they shouldn't be, huge problem - fixed

another bug: - kinda FIXED
* some trees are being marked as 'complete' but they have incomplete children
    * what happens: we go to a neighbor, let's say a leaf, we add it, the node becomes complete. then if we backtrack, add an incomplete node, that node should no longer be complete

another bug: - COULD NOT REPRODUCE (??)
I see a `]` in the ops path and yet the fscore is only `-5`, not `inf`
    * idk, could not reproduce, fuck, what do I know

another bug: - CONSIDERED
* the original goal was to find the *highest* incomplete node and recurse on that. however, a bug in the code meant that I was only ever finding the highest incomplete on the left subtree, effectively just doing a DFS. tbh though, DFS might just be better

revising earlier bug: - DONE
* is it always the case that when we insert a left child (since we insert left children first), that the right siblings should not be true?
* we have subtree `A`, we insert a bunch of shit on the left, then eventually `B`. `B` is an exit node, it has two leafs, so we start inserting things to the right of `A` (why? - because that means now that everything from `A` to `B` is complete)
* I'm just convinced that I need to copy nodes, I couldn't get by otherwise. I need to switch between two possible "realities" essentially (??), I could lose cousins if I don't copy (??)
* if we can backtrack to a node, that means we called `get_neighbors()` on it before. I claim somehow that I only need to copy a node when I call `get_neighbors()` on it, but what do I know

in DFS, where can we even go?
* a node is the direct child of what came before it
* a node is the direct parent of what came before it
* two nodes are unrelated even though they were inserted chronologically
    * a node is a right child -- in which case what came before it was an exit node
    * a node is a parent -- in which case what came before it was an exit node

astar:
* get the min node that we have to go on
* check if a goal is reached
    * otherwise, get neighbors
    * for each neighbor, calculate its score using heuristic
    * add neighbor as a candidate

DONE:
* made progress on a bug coming from `yieldfrom` that produced incorrect trees
    * part of the bug is still fixed, but conceptually, it's possible we may still find error
* fixed a conceptual bug where I had 'Nones' cancel out, that was bad
* fixed a bug about tree completeness
* identified that I'm actually doing a DFS (lol, rip)
* fixed an earlier bug where I just started copying trees
* fixed a bug with my heuristic
* created a `d_id` (debug id) for debugging

idea:
* words cost asymptotically more the more we have, to discourage long sentences? but also long sentences allow for looping, which we like...
* make leafs cost less in the short run? just to encourage the tree to do that?

TODO:
* there's a problem somewhere (happens whenever did error happens) where our path isn't the same length as our tree. it's wrong, it's weird
* conceptually: how do we make a tree "surface" quicker? I liked that idea about words costing asymptotically more as sentence gets longer but idk how to do that exactly

# 2025-02-17
misc notes:
* longest overlap may not be highest cost overlap, so I need to fix that
    * i.e `- ] None >>>` could overlap with `-]` and `>>>` but `-]` is higher cost
* idea: at a certain point just flush the open set, as in get rid of everything but current node. this prevents backtracking -> finds lowest cost to surface, effectively
    * or for same effect -- instead of flushing just add a *massive* point deduction. the problem is, when do I do this? it feels like something I should modify afterwards?

note from debugging:
* when building *down*, i.e at incomplete nodes, should I remove the ability to do recursive nodes? that's only an option when building up?

* also, I have a node that looks like
`['>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', None]`
with an fscore of -2 and a heuristic score of -18. bump that heuristic score up, that's way more valuable.

discovered something arguably pretty great, but it's another bug:
* I found a path
['>', '>', '>', '>', '>', '>', '>', '>', '>'] >>>>>>>>>
fscore -6.0 -18
that's literally just a *complete* sentence that is the *entire* input string (The noun and the noun verb)
and yet we did not return. what's the problem? this is *perfect*, why didn't we exit?

# 2025-02-19
ok, shit I think I might understand why this doesn't work
my node requires I call `self.neighbors` on it in order to actually, like, correct it. when I generate neighbors I can't be sure if any of them are correct because I haven't actually connected the neighbors to the tree yet

# 2025-02-22
I call the heuristic cost estimate on all of my neighbors. however, this feels like the *wrong* place to do that, since no neighbor is actually fully connected at this point. tbh I'm not even sure how this has been working so far. i feel like what would just be *easier* would be to make it so that neighbors are always complete trees? or perhaps -- to have the heruistic add, then "undo" a neighbor?

tbh not copying literally fucking everything at this point might be premature optimization.

so we definitely have a bug in `copy_tree`, that's fucking shit up (left/right pointers not working)

wtf is this bug:
```
>>> x=[n.get_root() for n in t.get_neighbors()]
>>> print(x[0])
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * incomplete
  * incomplete

>>> x=[n for n in t.get_neighbors()]
>>> print(x[2].get_root())
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * `AP: A'` 11216 -> parent `N': AP N'` 54128 (complete) +
    > leaf
    > `A': A` 59760 -> parent `AP: A'` 11216 (complete) +
      * leaf
      * leaf
  * incomplete
```

```
>>> print(t)
`AP: A'` 11216 -> parent `N': AP N'` 54128 (incomplete) +
  * leaf
  * incomplete
>>> print(t.get_root())
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * `AP: A'` 11216 -> parent `N': AP N'` 54128 (incomplete) +
    > leaf
    > incomplete
  * incomplete

>>> n=list(t.get_neighbors())
>>> print(n[0].get_root())
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * incomplete
  * incomplete
>>> n
[incomplete A': AdvP A' tree, incomplete A': A' Conj A' tree, complete A': A tree]
>>> print(n[1].get_root())
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * incomplete
  * incomplete
>>> print(n[2].get_root())
`N': AP N'` 54128 -> parent root 54128 (incomplete) +
  * `AP: A'` 11216 -> parent `N': AP N'` 54128 (complete) +
    > leaf
    > `A': A` 98992 -> parent `AP: A'` 11216 (complete) +
      * leaf
      * leaf
  * incomplete
```

the reason why the A' is working is probably bc it's complete, and the `is_complete` fn fixes parent pointers?
* holy shit that took way too long to debug and fix, in the future just pick the most obvious reason why smtg could be wrong and go with that

DONE:
* fixed a bug on `copy_tree`, rip lol
* fixed a bug in trules `T_T`
* fixed another bug in `get_neighbors` `T_T`
* just added copying to all neighbors, no data gets reused

holy shit even if I copy everything I still occasionally get that bug `T_T`

also -- apparently doing BFS is faster than DFS, at least for string `>>>>>>>>`
ehh, BFS to DFS is lowkey negligible difference, but I can test that more later.
* but also -- finding `+7` using tree search is like `0.0359s` (remainder of `>>>>`), while in graph search it's like `4.638s` (no remainder)
* doing some more tests -- I think this strategy is going to really work! fuck, maybe even without memoization! it's just that -- there's still this fucking bug in my code, lol

interestingly -- bug never shows up looking for `[[[`, or `]]]`, `+++`, or `>>>>`
* starts at `>>>>>`, speeds up at `>>>>>>>>` (I think it's gotta be a PP conj PP thing)

so that bug is still a problem, but also, observe:
* the path is equivalent to the tree I think, right ? I mean, I guess there's some ambiguity in if we did a left side rule or a right side rule. but I could just save one node per `search_node`, and build the tree from the paths
* this requires an additional O(path length) computation every time, but realistically it's probably magnitudes better in terms of memory. how much ram does this use?
    * it uses pretty much all of my CPU but it's only like 2% RAM after it's been running for a while, so that's probably not important.
* once we hit one bad path though all of our future trees/paths get fucked up, which sucks

* I thought at first that this only happened with Conj rules -- oh wait it totally is
* the problem is always a CONJ rule has a third child when it shouldn't I think
* oh my god -- are my third rules just not getting copied? are they getting reused??
    * that looks fine though. but yes, objectively if I remove Conj rules I don't ever get this bug
* holy shit I fucking solved it let's fucking GO!! it was a hash collision issue

DONE:
* fixed that *awful* bug holy shit

Later:
* I can go back to copying trees only in neighbors but it really doesn't matter

# 2025-03-08
been a minute!

TODO:
* make the tree fn to repeatedly find max overlaps
    * evaluate from there, probably need to make several adjustments
    * perhaps: negative costs on `>` / `<`?
* just to eneumerate things still left in this project:
    * should only have like max 500 chars in a bf program at each time
    * then need to start doing word replacements (exciting!)
    * probably a way to input trees (wrapped in parens?) and output programs, y'know, the reverse of this bijection

TODO:
* sometimes we end early but a better score is possible later. keep the program running for a little longer to see if we can find any better options?
    * yeah this is definitely important, sometimes we totally have a correct answer, sometimes we don't.


DONE:
* modified cost fn to get max overlap by cost
* modified negative weights to use > / < with negative weights if it's only >
* most immediate TODO is now to do a duration thing, or a memoization thing on `>` and `<` when we get single answers.... but we need a solution for `>` and `<` so our algorithm can actually terminate...

# 2025-03-10
problem: we should have a pretty short, simple way of encoding `<` -- `I verb (for your noun)` -- Pronoun, verb, prepositional phrase. however the algorithm does not find it, like, at all, and instead comes up with weird bullshit answers instead...
* oh, one thing is that we have equal positive weight to negative weight for `>`/`<` which could be bad?
* ok, this is bad, too, another problem is that whenever we have an ops path of `None`, we get an infinite score which means we'll never regard this neighbor until we regard *all* fucking neighbors, super bad. so I feel like no overlap should be neutral? or if it's negative it shouldn't be by a lot? let's try neutral first

I'm seeing this:
`hey 0 10.0 [']', '>'] <`
so somewhere there's a string with `]` in it that doesn't have inf score which is bad
* fixed

observation:
* we'll currently try literally all paths of len 6, before we try something like `<<<` just because its score is so high
* ^what score is that? `<<<` has a score of 5 `T_T` did I just miss it?
    * yeah but it's neighbor has a score of 6 which is why we haven't seen it yet

another observation:
* when we're doing this, we should *never* look at any rule containing `AdvP` smtg because that will just force us to use a `-` eventually...
* fixed by hardcoding it `(T_T)`

ok so I kind of babied the scores and it... works? at least just for this case, but I feel like now it's gotta be slow elsewhere...

weird observation: - FIXED! problem with writing global weights variables
* searching for just `+` first produces a good result, but searching for `>[` has a recursive call that looks for just `+`, and gives me shit or hangs...
* another example: `[>+`, when it recurses on `>+` instead of finding `>+`, it just finds only `>`, and then when it recurses on `+` it doesn't find shit...


TODO:
* again, from last time -- `>]` is either finding `>>>]>` (-6) or `]>` (-7), the latter is definitely better but isn't always returned


DONE:
* fixed some bugs?
* adjusted costs
* fixed another bug lets fucking go it works. like, tons of room for improvements but it fucking works hell yeah lessgo!!

next step:
* still, please, god, I need to figure out either how to change my costs or just make it so that we return the best answer
    * memoization? run this thing for a certain duration and pick best answer?
* word replacement / next stage of project goals :))

# 2025-03-16
Memoization program:
* in a new file, extend TreeMemo to a new class
* create an interface where I can insert a program. I get shown trees that match that program, and I can choose whether or not I want to memoize them
* if they get memoized, the trees get saved to dict (key is program, entries are sets containing the trees). save this to a file
* in TreeSearch, load up the memoized tree
* in `find_bf`, whenever a program comes in first check to see if it's in the table. if it is, use that, otherwise, just run the algorithm.
    * profit?

Word replacement:
* just first try a naive substitution and see what happens i guess
* how tf does this even work? First, I should probably do parens wrapping around leafs just to like, see what a tree *is*. -DONE
    * leafs in the same phrase get put in the same parens. so ig we do in order traversal
Rules:
* for the rule DP: NP, the noun must be pluralized
    * uhh, with some exceptions in prepositional phrases?
        i.e, `((D N) ((TV Pronoun) (P N)))` -> `Your heart soothes me with passion`
* pronouns have to follow subject/object
    * subject: myself, yourself
* conjugation
    * My noun verb*s* for your noun
    * YOU/I verb for the noun

* if we're doing a bunch of adjectives in the same noun phrase we can't use the same one twice b2b...

DONE:
* started doing memoization program, as in, wrote memoizer
* reorganized some code from tree search to graph search
* function to turn sentences into paren-separated leafs
* put memoizer in `find_bf` function...
