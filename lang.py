'''
Overall goal of this program: take, as input, a bf function, and using the set syntax rules, construct a grammatical sentence tree. As an additional option, automatically fill in the words with words from a wordbank. The goal should be to construct as short of a mapping as possible.

* ok, couple of notes. what does "a grammatial sentence tree" look like? Is that a Python object? so then a collection of sentences is an array of these objects?
* "as short of a mapping as possible" should also note that some rules don't take up any space, or take up less space, as in they may have like 5 rules but only 2 actual words attached. so maybe each "node"/phrase has a certain weight to it, and I start out by manually weighting them with how many words are present. This is a good idea bc then I can modify those weights as the program goes on to, say, avoid repetitive sentences.

* this is a later problem, but when filling out with words -- I have some more niche grammar rules that aren't captured by PSR. for example, it's "You and I", not "I and you". Transitive/ditransitive verbs matter. Some verbs take instrument prepositions phrases, some words don't, etc. But again I'll come back to this later.

## "naive" idea
the first idea is to keep track of a "remainder" or "offset" from what the bf program expects the position to be, vs what it actually is. perhaps same thing with `+-`, too. the rules are such that inserting `+-][.,` is *always* optional. There is no sentence that requires the rules corresponding to these operations anywhere. However, nouns and verbs are always required and always associated with some degree of movement/shift.

so. Let's say I want to insert a "+" somewhere. That's an adjective rule, which requires a DP to be placed in. Assume (although it doesn't have to be) that we use the subject DP to insert it, so by the time we get to it it looks like `>>+` or something. No problem, we expect that, and we create another sentence that moves us two spaces *backwards*, before we go for `>>+`, then we end up ultimately in the right place.
* I guess, same thing with the fact that `+` is actually `+++`, if we want just one then we can insert one adjective, move around, correct, then do the same thing with adverbs, but it'll at least symbols-wise be *faster* to insert an adverb beforehand. So we "wind up" with a sentence of `<<`, then run into `>>--+++` to cancel out into just `+`.

## search idea
this feels like a *graph traversal* / *search algorithm*. We have a graph that have continuously enter and exit (S: DP VP). At each node each have edges, given by rules, to other nodes (states?), where each edge is associated with an operation for traversal, and probably, some other kind of cost, too.

This feels really fucking abstract but I think `><+-` can be visualized as some kind of multidimensional number system, actually...

## wtf is this graph
oh god, this thing is fucking infinite?
* no, not true, but there are loops in it

coming back again, and, I built it. fuck yeah.
implementation:
* we start at the node "S", whose left and right children are DP "choices" and VP "choices" respectively. A choice node represents a choice. Here, we can choose whatever we want to proceed down our graph, there are no restrictions on our movement. Other nodes have a left and right child (but, unfortunately, in the case of ditransitive verbs there are actually three; maybe implement this as "left, right, special?").
* I should have some object that represents this graph, which is fairly easy to construct given my rules. So then, 1), a function that converts a list of rules (given as strings and weights?) into the graph.
* once I have the graph, I should have an abstract method to traverse it. to do an "in order traversal" -- I mean, recursively you can just move down the left branch, then log/print/whatever the current branch, then go down the right branch, that's easy.
    * non-recursively, at all non-choice nodes always just go left. if we have have a node that has a right child, add it to a stack. once we get to a leaf/"head" pop off the stack and go back to that node, choose the right child. if our stack is empty we're done.

1) a function that converts a list of rules (and idk, rules are objects with strings and weights?) into the graph.

2) a function to "search" the graph
    * it's infinite so we have to use BFS ofc
    * instead of putting costs on the edges we can put costs on the nodes themselves, as long as a node isn't a head/leaf. or put them on edges, it doesn't matter
    * oh, nuance; when I'm actually running this thing, in-order doesn't force us to "commit" to our choices in certain cases. for example, consider using `and`. I don't have to look for the entire string all at once, I can look for part of it, find smtg, and then once I start looking for a new thing I can retroactively say, oh, you know, we want to do an "and" node here...
    * when can we break?
        * if we hit `[` or `]` when we didn't mean to, there's no going back, so just abort that
        * we *can't* break if, say, we hit `--` before we hit `+++`, bc these actually cancel out. but I guess our program should know that there is no `+`, there's only `--+++`
    * is a search more effective if we start at the symbol we want, and backtrack through the graph up to `S`? the goal is like, neutrality...

I laid out the tree (or at least part of it) instead of as an in-order binary tree, as a graph. and thankfully this still is finite, too, it just has loops in it.
observations:
* if there's a rule like `X': YP X'` (for example, N': AP N'), then we first go into the YP rule, and when we hit the head Y, then we hit the `X': YP X'` node, and we go back to up to the main `X'` choice node
* if there's a rule like `X': X' YP`, first we hit that, then we go into the YP tree
* a rule like `X': X' PP` means that everything that ends underneath any other `X'` rule has a node to `PP`
* I think complement rules, like `X': X YP`, which can only be passed through once
    * "the (book of (stories of war))"

* `X': X' YP` - for a rule like this, any time we reach the end of a path that is the child of an `X'` node / has an `X'` node in its history, we can *choose* to go to YP, *in addition to* any other next steps we could have taken
    * if we reach an `X` head that doesn't have a complement, or finish the complement, we can hit this rule and then go to `YP`, or we can go to whatever else would've come after -- so we have an additional edge.
* `X': YP X'` - for a rule like this, any time we're at a choice node for `X'`, we can immediately go into `YP`, and continue that tree. when we exit -- at the YP head -- we pass through this rule and go back to our choice node
* at a choice node for `X'`, we can go to all nodes `X': X' YP`, or to all `WP` for rules `X': WP X'` (at `WP` we have to leave the W head (?) through the previous rule)
* `XP: XP Conj XP` - whenever we're about to leave an `XP` expression, we have an edge back to the `XP` choice node
    * "exit points" are points in an XP phrase where we can leave the XP phrase in our graph. they're always heads. an `X': X` is always the exit node of an `XP` phrase. If a phrase has a complement YP (i.e `X': X YP`), then the `YP` exit point is the `XP` exit point.
    * if we pass an exit point, then the next exit point we see we can also exit at, to the same locations as before
    * at all exit points, we have both conjugation rules available to us, which just point back up the graph to their respective starts

## replacing heads with actual words
* need to keep track of if I'm in the adjunct or complement. for example, "book of poems" is a complement and works, but "book of poems of stories" doesn't
* "I long (for your affection) (in the morning) -> I long (in the morning) (for your affection)" implies that V can have a PP complement?

## misc
interstingly there are only 216 trigrams in my corpus. this is super small, I could totally calculate DP solutions for every trigram, and then just use those, plus maybe being a little smarter on stacks of `+-<>`, `-[-[-[...`, and `]]]`
* wait, wait, I only see 2675 *53*-grams, is that even right? this may be really easy to brute force then?
* DP: doesn't necessarily benefit from optimal substructures. as in, concatenating trigrams may produce a solution that is longer than just 6 of something in a row.

### A*
a heuristic is admissable if it never overestimates the cost of reaching the goal

### in order to graph
remember something about where we exit to, and what we're exiting from

start at the root, so we have S:DP VP
* we enter DP first bc it's on the left, and remember that we *exit* to VP
* every time we have multiple options for a rule we insert a "choice node". the edges out of a choice node represent us commiting to a rule
* if we have a rule like `X': X' YP`, we do not start on that. we remember that as an option, and at exit nodes whose paths have an `X'` rule in their history, we may choose to exit to YP and insert this
* in our in-order traversal, the nodes in our stack represent commitments. we have to do them later
* exit nodes: for a given path into our graph, say, `first -> [S: DP VP, NP: NP Conj NP, AP: AP Conj AP, A': A' Conj A']`, and in our stack, `-> [S: DP VP, N': AP N'

"The very"
stack: [S: DP VP, ??DP: DP Conj DP??, ??NP: NP Conj NP??, ??N': N' Conj N'??, ??N': N' PP??, N': AP N', ??AP: AP Conj AP??, ??A': A' Conj A'??, A': AdvP A', ??Adv': AdvP Adv'??]
* at choice nodes in our tree, in an in-order graph we don't know if we're going to *choose* to recurse -- on left-recrusive rules

* whenever a rule is left-recursive X': X' Y, we may *choose* to go to that rule *after* finishing the current scope
* whenever a rule is right-recursive X': Y X', then we have to make our choice to recurse on Y whenever X' becomes available. However, if we enter this, we have to commit, meaning that the exit node of Y has to point to X'

whenever we finish a promise (left-node), we need to add the rule that spawned this promise back in. how do we tell if we finished a promise?
observation: it looks like at heads of an X' / XP rule, we can apply left-recursive rules like conjugation
    * except, this doesn't work for DP. DP has a D head but it has a complement (right branch). we can only do this at nodes that have both a left/right leaf
    * at a node `X` that has both a left and right leaf, we can do left-recursive rules for `X'` and `XP`.
    * nodes that have a left leaf but not a right leaf are special, those are what define "scope" or smtg
    * "exit nodes" are nodes with a left and right leaf.
ok, stack of stacks (committed). every time we take a new commitment, either from our starting rule or from a right-recursive rule, we go to a new entry in our commitment stack. There, we append to this list all the things we pass. Once we get to an exit node (i.e, any node that has right/left leaves), we have a couple of options
    * we can do *any* left-recursive `(N: N R)` rule belonging to a node in our scope. this goes to that rule
    * we can *exit* by going to the *spawning rule*, which pops off the current list. from the spawning rule, we go to the *right* node...
^ scratch that, it's *all the same case*!

what happens when we reach an exit node in our commitment stack?
* remember it's a stack of stacks. we reach the final stack. we pop the exit node. if the previous rule as a left-recursive `(N: N R)` rule, we can choose to go to that or not. if we do, we add the recursive rule and go to the right child. we keep the stack as it is. otherwise we pop that off, and make the same series of choices.
* when the stack has size one, we do the same thing, we pop the spawning rule off, go to it, and then continue on the right side. at this point the stack on top should be empty!

---
Start at a rule
We *promise* the left node, which means our next options/edges are rules where the left node has its own *left leaf*, AND, if there is a *right-recursive* rule, then we have all of the leafs of that left rule as well

the outgoing neighbors of a node (N: L R):
1. all rules of the form (R: (Leaf) RR)
2. if the right-recursive rule (R: RL R) exists, then all rules of the form (RL: (Leaf) RLR)
    * if in this scenario, we "enter a new scope", i.e start another committed list in our stack
3. if the node is an *exit-node*, i.e L and R are both leafs, then
    * we can access all left-recursive `(X: X Y)` rules for nodes that are present in the current scope/stack/commitment/whatever. if we go to that rule, we pop `X` off of our stack, and produce all options for `Y`.

. We *commit* the right node, so we add it onto the stack to do later.
'''

rules = [
    #{'rule': "SP: AnyDP VP", 'ops': ""},
    {'rule': "SP: DP VP", 'ops': ""},

    # TODO: this will actually work, I should just also add an additional key/value for the actual rule string, and if something should be "counted" or not, i.e printed out in our tree
    #{'rule': "AnyDP: DP", 'ops': ""},
    #{'rule': "AnyDP: ProDP", 'ops': ""},
    #{'rule': "AnyDP: AnyDP Conj AnyDP", 'ops': ">>"},
    #{'rule': "ProDP: Pronoun", 'ops': "<<<<"},

    {'rule': "DP: DP Conj DP", 'ops': ">>"},
    {'rule': "DP: Pronoun", 'ops': "<<<<"},
    {'rule': "DP: D'", 'ops': ""},
    {'rule': "D': D NP", 'ops': ">>"},
    {'rule': "D': NP", 'ops': ">>>", "right": True},

    {'rule': "NP: N'", 'ops': ">"},
    {'rule': "NP: NP Conj NP", 'ops': "]"},
    {'rule': "N': AP N'", 'ops': "+"},
    {'rule': "N': N' PP", 'ops': ""},
    {'rule': "N': N PP", 'ops': ""},
    {'rule': "N': N", 'ops': "<"},

    # VP rules
    {'rule': "VP: V'", 'ops': ">"},
    {'rule': "VP: VP Conj VP", 'ops': "<<<<"},
    {'rule': "V': V' PP", 'ops': ""},
    {'rule': "V': V' AdvP", 'ops': ""},
    {'rule': "V': AdvP V'", 'ops': ""},
    {'rule': "V': TV DP", 'ops': ">"},
    {'rule': "V': DTV DP DP", 'ops': ">"},
    {'rule': "V': V", 'ops': ""},
    #{'rule': "V': V Comp SP", ops: "?"},

    # AdvP Rules
    {'rule': "AdvP: Adv'", 'ops': ""},
    {'rule': "AdvP: AdvP Conj AdvP", 'ops': ""},
    {'rule': "Adv': Adv' Conj Adv'", 'ops': "++"},
    {'rule': "Adv': AdvP Adv'", 'ops': "["},
    {'rule': "Adv': Adv", 'ops': "-"},

    # AP Rules
    {'rule': "AP: A'", 'ops': "+"},
    {'rule': "AP: AP Conj AP", 'ops': "------"}, #?
    {'rule': "A': A' Conj A'", 'ops': "--"},
    {'rule': "A': AdvP A'", 'ops': "-"},
    #{'rule': "A': A PP", 'ops': ""},
    {'rule': "A': A", 'ops': "+"},

    # PP Rules
    {'rule': "PP: P'", 'ops': ">>"},
    {'rule': "PP: PP Conj PP", 'ops': ">>>>"},
    #{'rule': "P': P' PP", 'ops': ""}, #TODO?
    {'rule': "P': P DP", 'ops': ""},
    #{'rule': "P': P", 'ops': ""}
]

'''
everytime we see XP or X' we interpret that as a choice node
so I think a graph is a dictionary; keys are either XP or X' and represent the "choice nodes", and values are a list/set of the actual nodes attached to them.
'''
import random

is_head = lambda X: X and not (X.endswith("'") or (len(X) > 1 and X.endswith("P")))
class Node:
    def __init__(self, rule_dict):
        self.rule_str = rule_dict['rule']
        self.ops = rule_dict['ops']
        self.l = None
        self.r = None
        self.third = None

        # rule is either XP or X', children is what it connects to
        rule, children = self.rule_str.split(":")
        children = children.strip().split(" ")
        # XP phrase
        if len(children) == 1 and (rule.endswith("P") or rule_dict.get('right')):
            self.r = children[0]
        # X' phrase
        else:
            self.l = children[0]
            if len(children) > 1:
                self.r = children[1]
                self.third = children[2] if len(children) > 2 else None


        self.l_head = is_head(self.l)
        self.r_head = is_head(self.r)

        self.rule = rule
        #self.words = bool(self.l_head) + bool(self.r_head) # TODO wrong
        print(rule, ':', self.l, self.r, self.third, '\t', self.l_head, self.r_head)

        # TODO later
        self.frequency_cost_multiplier = 1

    def get_rand_weight(self):
        weight = 5
        if "Conj" in self.rule_str:
            weight -= 4
        elif self.l_head or self.r_head:
            weight += 5 * 2.5
        return weight

    def __str__(self):
        return f"{self.rule}: " + ' '.join([x for x in [self.l, self.r, self.third] if x])

    def __repr__(self):
        return self.__str__()

class Graph:
    def __init__(self, rule_array):
        self.add_nodes(rule_array)

    def add_nodes(self, rule_array):
        '''
        initializes a dictionary of nodes
        the keys are "choice nodes", strings; the values are the nodes
        '''
        self.nodes = {}
        for rule_dict in rule_array:
            node = Node(rule_dict)
            self.nodes[node.rule] = self.nodes.get(node.rule, set()).union(set([node]))

    def random_traverse(self):
        root = 'SP'
        visited = {}
        def helper(root, head=False, depth=0):
            if root is None:
                return
            if head:
                #print(root)
                #input(' ' * depth + '**' + root)
                #print(' ' * depth + '**' + root)
                print(root, end=' ')
                return

            nodes = list(self.nodes[root])

            #weights = [1 / visited.get(n.rule_str, 1) for n in nodes]
            #node = random.choices(nodes, weights=weights)[0]

            weights = [n.get_rand_weight() for n in nodes]
            node = random.choices(nodes, weights=weights)[0]
            if depth > 12:
                for n in nodes:
                    if n.l_head and not n.r:
                        node = n
                        break
            visited[node.rule_str] = visited.get(node.rule_str, 1) + 1

            '''if 'Conj' in node.rule_str:
                if random.random() < 0.85:
                    node = random.choice(list(self.nodes[root]))'''
            helper(node.l, node.l_head, depth + 1)
            #print(node)
            #input(' ' * depth + str(node))
            #print(' ' * depth + str(node))
            helper(node.r, node.r_head, depth + 1)
            helper(node.third, depth=depth+1)

        helper(root)



G = Graph(rules)
#G.random_traverse()
