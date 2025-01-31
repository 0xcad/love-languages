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
