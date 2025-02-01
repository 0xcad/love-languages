
rules = [
    #{'rule': "SP: AnyDP VP", 'ops': ""},
    {'rule': "SP: DP VP", 'ops': "", "root": True},

    # TODO: this will actually work, I should just also add an additional key/value for the actual rule string, and if something should be "counted" or not, i.e printed out in our tree
    #{'rule': "AnyDP: DP", 'ops': ""},
    #{'rule': "AnyDP: ProDP", 'ops': ""},
    #{'rule': "AnyDP: AnyDP Conj AnyDP", 'ops': ">>"},
    #{'rule': "ProDP: Pronoun", 'ops': "<<<<"},

    {'rule': "DP: DP Conj DP", 'ops': ">>", "word_cost": 2},
    {'rule': "DP: Pronoun", 'ops': "<<<<", "word_cost": 1},
    {'rule': "DP: D'", 'ops': ""},
    {'rule': "D': D NP", 'ops': ">>", "word_cost": 1},
    {'rule': "D': NP", 'ops': ">>>", "right": True},

    {'rule': "NP: N'", 'ops': ">"},
    {'rule': "NP: NP Conj NP", 'ops': "]"},
    {'rule': "N': AP N'", 'ops': "+"},
    {'rule': "N': N' PP", 'ops': ""},
    #{'rule': "N': N PP", 'ops': ""},
    {'rule': "N': N", 'ops': "<", "word_cost": 1},

    # VP rules
    {'rule': "VP: V'", 'ops': ">"},
    {'rule': "VP: VP Conj VP", 'ops': "<<<<", "word_cost": 2},
    {'rule': "V': V' PP", 'ops': ""},
    {'rule': "V': V' AdvP", 'ops': ""},
    {'rule': "V': AdvP V'", 'ops': ""},
    {'rule': "V': TV DP", 'ops': ">", "word_cost": 1},
    {'rule': "V': DTV DP DP", 'ops': ">"},
    {'rule': "V': V", 'ops': "", "word_cost": 1},
    #{'rule': "V': V Comp SP", ops: "?"},

    # AdvP Rules
    {'rule': "AdvP: Adv'", 'ops': ""},
    {'rule': "AdvP: AdvP Conj AdvP", 'ops': "", "word_cost": 2},
    {'rule': "Adv': Adv' Conj Adv'", 'ops': "++", "word_cost": 2},
    {'rule': "Adv': AdvP Adv'", 'ops': "["},
    {'rule': "Adv': Adv", 'ops': "-", "word_cost": 1},

    # AP Rules
    {'rule': "AP: A'", 'ops': "+"},
    {'rule': "AP: AP Conj AP", 'ops': "------"}, # TODO? do I want this?
    {'rule': "A': A' Conj A'", 'ops': "--"},
    {'rule': "A': AdvP A'", 'ops': "-"},
    #{'rule': "A': A PP", 'ops': ""},
    {'rule': "A': A", 'ops': "+", "word_cost": 1},

    # PP Rules
    {'rule': "PP: P'", 'ops': ">>"},
    {'rule': "PP: PP Conj PP", 'ops': ">>>>", "word_cost": 2},
    #{'rule': "P': P' PP", 'ops': ""}, #TODO?
    {'rule': "P': P DP", 'ops': "", "word_cost": 1},
    #{'rule': "P': P", 'ops': ""}
]

import random
import copy

is_head = lambda X: X is None or not (X.endswith("'") or (len(X) > 1 and X.endswith("P")))
class RuleNode:
    '''
    A class wrapper for rule dictionaries
    A recursive, binary tree representing all given X-bar
    rules/ key: rule strings / values: RuleNode objects
    nodes/ key: string X     / values: a set containing all RuleNodes X: W Y
    '''
    rules = {}
    nodes = {}
    root = None

    def __new__(cls, value):
        key = value.get('rule')
        if key in cls.rules:
            return cls.rules[key]
        instance = super().__new__(cls)
        cls.rules[key] = instance
        return instance

    @classmethod
    def construct_from_rules(cls, rule_array):
        for rule_dict in rules:
            node = RuleNode(rule_dict)
            cls.nodes[node.rule] = cls.nodes.get(node.rule, set()).union(set([node]))
            if node.is_root:
                cls.root = node

    def __init__(self, rule_dict : dict):
        '''
        Given a dictionary in the form
        {'rule': `rule`, 'ops': `ops`} construct a node for the rule
        '''
        self.rule_str = rule_dict['rule']
        self.ops = rule_dict['ops']
        self.word_cost = rule_dict.get('word_cost', 0)
        self.is_root = rule_dict.get('root', False)

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


        self.is_l_leaf = is_head(self.l)
        self.is_r_leaf = is_head(self.r)
        self.is_right_recursive = rule == self.r
        self.is_left_recursive = rule == self.l

        self.rule = rule
        #print(rule, ':', self.l, self.r, self.third, '\t', self.l_leaf, self.r_leaf)

    def __str__(self):
        return f"{self.rule}: " + ' '.join([x for x in [self.l, self.r, self.third] if x])

    def __repr__(self):
        return f'`{self.__str__()}`'

    def __eq__(self, other):
        return other and other.rule_str == self.rule_str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.rule_str)


# create all of our rules
RuleNode.construct_from_rules(rules)

ROOT_NODE = RuleNode.root

class GraphNode:
    '''
    Produces a graph of an in-order traversal of the recursive binary tree `tree`

    Every graph node has
    1. What rule / tree node is it
    2. Choice node (left recursive / start) or not
    '''
    _cache = {}
    _tree = RuleNode

    def __new__(cls, commitments, node, **kwargs):
        h = cls._hash(commitments, node, kwargs)
        if h in cls._cache:
            return cls._cache[h]

        instance = super().__new__(cls)
        cls._cache[h] = instance
        instance.hash = h
        return instance

    def __init__(self,
            commitments : list[list], # stack of stacks
            node : RuleNode,
            is_choice : bool = False,
            force_recurse_right : bool = False,
        ):
        self.commitments = commitments
        self.node = node

        self.neighbors = None

        self.is_choice = is_choice
        # choice nodes don't produce rules when we pass through them

        self.ops = self.node.ops if not is_choice else None
        self.ops_path = [c for c in self.ops] if self.ops else []

        self.force_recurse_right = force_recurse_right
        self.is_terminal = False
        self.is_exit = self.node.is_l_leaf and self.node.is_r_leaf

    def _add_neighbor(self, neighbors, g):
        neighbors.append(g)

    def copy_commitments(self):
        return copy.deepcopy(self.commitments, memo={id(node): node for row in self.commitments for node in row})

    def get_neighbors(self):
        '''
        the outgoing neighbors of a node (N: L R), where NR is "neighbor rule" (L or R):
        1. all rules of the form (NR: (Leaf) NR_R)
        2. if the right-recursive rule (NR: NR_L NR) exists, then all rules of the form (NR: (Leaf) NR_R) (enter a new choice node)
            * if in this scenario, we "enter a new scope", i.e start another committed list in our stack
        3. if the node is an *exit-node*, i.e L and R are both leafs, then
            * we can access all left-recursive `(X: X Y)` rules for nodes that are present in the current scope/stack/commitment/whatever.
            * if we go to that rule, we pop `X` off of our stack, and produce all options for `Y`.
        '''
        if self.neighbors:
            return self.neighbors

        neighbors = []

        target_rule = None
        if not(self.force_recurse_right) and not self.node.is_l_leaf:
            target_rule = self.node.l
        elif not self.node.is_r_leaf:
            target_rule = self.node.r
        elif self.node.third:
            target_rule = self.node.third

        if target_rule is not None:
            target_rule_nodes = self._tree.nodes[target_rule]
            # ^ all tree nodes that correspond to this rule

            for n in target_rule_nodes:
                # add all rules of form (NeighborRule: (Leaf) NR_R)
                if n.is_l_leaf:
                    #commitments = copy.deepcopy(self.commitments)
                    commitments = self.copy_commitments()
                    commitments[-1] += [n]
                    g = GraphNode(commitments, n)
                    self._add_neighbor(neighbors, g)

                # add all right-recursive choice node rules of form (NR: NR_L NR)
                if n.is_right_recursive:
                    # start a new commitment, with a choice node
                    g = GraphNode(self.commitments + [[n]], n, is_choice = True)
                    self._add_neighbor(neighbors, g)

        # exit node
        if self.is_exit:
            scope = self.commitments[-1]
            for i, n in enumerate(scope):

                g = None
                # allow us to terminate the graph if we want to / restart
                if n is None:
                    self.is_terminal = True # TODO?
                    g = GraphNode([[ROOT_NODE]], ROOT_NODE, is_choice=True)
                    self._add_neighbor(neighbors, g)
                    continue
                # exit a current scope to some other one
                elif i == 0:
                    #commitments = copy.deepcopy(self.commitments)
                    commitments = self.copy_commitments()
                    commitments.pop()
                    if len(commitments) == 0:
                        commitments = [[None]]
                    g = GraphNode(commitments, n, force_recurse_right=True)
                    self._add_neighbor(neighbors, g)

                # get all left recursive rules in scope
                n_rules = self._tree.nodes[n.rule]
                for n_rule in n_rules:
                    if not n_rule.is_left_recursive:
                        continue
                    #commitments = copy.deepcopy(self.commitments)
                    commitments = self.copy_commitments()
                    commitments[-1] = commitments[-1][:i+1]
                    g = GraphNode(commitments, n_rule, force_recurse_right=True)
                    self._add_neighbor(neighbors, g)

        self.neighbors = neighbors
        return neighbors

    def __str__(self):
        s = str(self.node) + '\n' + str(self.commitments) + '\n'
        if self.is_choice:
            return 'choice node: ' + s
        return s

    def __repr__(self):
        if self.is_choice:
            return 'choice node: ' + repr(self.node)
        return repr(self.node)

    def __eq__(self, other):
        return (other and
                self.node == other.node and
                self.commitments == other.commitments and
                self.is_choice == other.is_choice and
                self.force_recurse_right == other.force_recurse_right)

    def __ne__(self, other):
        return not self.__eq__(other)

    def _hash(commitments, node, kwargs):
        return hash((node, str(commitments), kwargs.get("is_choice", False), kwargs.get("force_recurse_right", False)))

    def __hash__(self):
        return self.hash
        #return hash((self.node, str(self.commitments), self.is_choice, self.force_recurse_right))

class TreeNode:
    def __init__(self, data, left=None, right=None, parent=None, third=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

        self.third = third

        self.is_right_child = None
        self.is_left_child = None
        self.is_third_child = None

        if type(data) == RuleNode:
            if data.is_l_leaf:
                self.left = False
            if data.is_r_leaf:
                self.right = False
            if not data.third:
                self.third = False

        self._is_complete = None

    @property
    def is_complete(self):
        if self._is_complete is not None:
            return self._is_complete
        self._is_complete = (
                (self.left is False or self.left and self.left.is_complete) and
                (self.right is False or self.right and self.right_is_complete)
        )
        if self._is_complete:
            self.parent.update_is_complete()
        return self._is_complete

    def update_is_complete(self):
        '''
        this node is now complete, so recalculate is_complete for the parent node
        '''
        self._is_complete = None
        self.is_complete()

    @property
    def height(self):
        # TODO ?
        pass

    def __hash__(self):
        if not self.is_complete:
            raise Exception('hashing incomplete tree...')
        return hash((hash(self.left), hash(self.data), hash(self.right)))

    def __str__(self):
        def helper(node, depth=1):
            if node is None:
                return "incomplete"
            elif node is False:
                return "leaf"
            s = [f'{repr(node.data)} {str(id(node))[-5:]} -> parent {repr(node.parent.data) if node.parent else "root"} {str(id(node.parent))[-5:]}']
            bullet = '*' if depth % 2 else '>'
            s.append(f'{" " * depth * 2}{bullet} {helper(node.left, depth +1)}')
            s.append(f'{" " * depth * 2}{bullet} {helper(node.right, depth +1)}')
            return '\n'.join(s)
        return helper(self)

    def get_root(self):
        if not self.parent:
            return self
        c = self
        while c and c.parent is not None:
            c = c.parent
        return c

    def get_root_and_correct_parents(self):
        if not self.parent:
            return self
        c = self
        while c and c.parent is not None:
            if c.is_left_child:
                c.parent.left = c
            elif c.is_right_child:
                c.parent.right = c
            elif c.is_third_child:
                c.parent.third = c
            c = c.parent
        return c

    @classmethod
    def _copy_node(cls, node):
        '''
        Helper function to copy just the individual data of a single node
        Includes the parent
        '''
        new = TreeNode(node.data)
        new.is_left_child = node.is_left_child
        new.is_right_child = node.is_right_child
        new.is_third_child = node.is_third_child
        new.parent = node.parent
        return new

    @classmethod
    def copy_subtree(cls, tree):
        '''
        the parent of the resulting tree is the uncopied parent of the original
        '''
        if not tree:
            return tree
        # copy children
        left = cls.copy_subtree(tree.left)
        right = cls.copy_subtree(tree.right)
        third = cls.copy_subtree(tree.third)
        new = cls._copy_node(tree) # copy node
        if left:
            left.parent = new
        if right:
            right.parent = new
        if third:
            third.parent = new
        new.left = left
        new.right = right
        new.third = third # assign copied children to node
        return new

    @classmethod
    def copy_tree(cls, tree):
        '''
        Copy the subtree *and* copy up to the root, as well. Return a pointer just to the copy of `tree` though
        '''
        if not tree:
            return tree
        new = cls.copy_subtree(tree)

        curr = new
        parent = new.parent
        while parent:
            # if new is the right subtree, copy the left subtree
            # if new is the left subtree, copy the right subtree
            new_parent = cls._copy_node(parent)

            # copy whatever we didn't copy before
            if not curr.is_right_child:
                new_sibling = cls.copy_subtree(parent.right)
                new_parent.right = new_sibling
                if new_sibling: new_sibling.parent = new_parent
            if not curr.is_left_child:
                new_sibling = cls.copy_subtree(parent.left)
                new_parent.left = new_sibling
                if new_sibling: new_sibling.parent = new_parent
            if not curr.is_third_child:
                new_sibling = cls.copy_subtree(parent.third)
                new_parent.third = new_sibling
                if new_sibling: new_sibling.parent = new_parent

            curr.parent = new_parent
            curr = new_parent
            parent = new_parent.parent
        return new

    @classmethod
    def insert_left_recursive_node(cls, tree, node, copy=True):
        '''
        Climb up the tree until the current node's rule is the left rule of what we want to insert...
        THERE IS AMBIGUITY HERE. This algorithm assumes, possibly incorrectly, that the first place to insert
        a rule is the one we want.
        '''
        if not (tree and node):
            raise Exception('invalid insertion...')
        target_rule = node.data.l
        curr = tree
        while curr and curr.data.rule != target_rule:
            curr = curr.parent
        if curr is None:
            raise Exception('invalid insertion, left rule not in tree...')

        if copy:
            #curr = cls.copy_subtree(curr)
            # ^ this would've been elegant but it doesn't work
            curr = cls.copy_tree(curr)
        # we make a copy so we don't fuck with the tree if we need to backtrack

        # insert the node at curr
        node.parent = curr.parent
        curr.parent = node # change the parents
        node.is_left_child = curr.is_left_child
        node.is_right_child = curr.is_right_child
        if node.is_left_child:
            node.parent.left = node
        elif node.is_right_child:
            node.parent.right = node # left/right child status

        curr.is_left_child = True
        curr.is_right_child = None
        node.left = curr # insert curr as left child of node
        return node

    @classmethod
    def find_right_recursive(cls, tree):
        '''
        Return the next ancestor that has a left node
        '''
        if tree.left:
            return tree

        c = tree
        while c and c.parent is not None:
            if c.is_left_child:
                c.parent.left = c
                return c.parent
            elif c.is_right_child:
                c.parent.right = c
            elif c.is_third_child:
                c.parent.third = c
            c = c.parent
        raise Exception("find right recursive failed")

class GraphSearchNode:
    '''
    A wrapper for graph nodes and ops_path
    Does not hash, or no equality...
    '''
    def __init__(self, gn, ops_path):
        self.gn = gn
        self.ops_path = ops_path

    def add_ops(self, ops):
        '''
        Merge ops with our own ops_path
        '''
        if ops:
            ops = [c for c in ops]
            while (ops and self.ops_path and
                   ((ops[0] == '>' and self.ops_path[-1] == '<') or
                   (ops[0] == '<' and self.ops_path[-1] == '>') or
                   (ops[0] == '+' and self.ops_path[-1] == '-') or
                   (ops[0] == '-' and self.ops_path[-1] == '+')
                   )):
                del ops[0]
                self.ops_path.pop()
            self.ops_path.extend(ops)
        return self.ops_path


root = GraphNode([[ROOT_NODE]], ROOT_NODE, is_choice = True)

from astar import AStar
from math import inf
class GraphFinder(AStar):

    def path_heuristic_cost_estimate(self, current, goal):
        gn = current.data.gn
        current_rule = gn.node

        came_from = current.came_from
        if came_from is None or (gn.is_choice and current_rule == RuleNode.root):
            print('restarting')
            current.cache = None
        else:
            current.cache = TreeNode.copy_tree(came_from.cache)

        parent_tree = current.cache
        '''
        Generate the tree
        '''
        current_node = parent_tree

        #print('current', id(current))
        #print('came_from', id(came_from))

        #if current.data.is_exit:
        #    print('this is an exit node!')

        print("Path (reverse order):")
        c = came_from
        i = 0
        print(repr(gn), end=' || ')
        while c and i < 10:
            print(repr(c.data.gn), end=" || ")
            c = c.came_from
            i += 1
        print('')

        #print(current.data.commitments)
        '''
        if the node is an exit node:
            * convert the node and what came before it into a tree
            * but stop, as soon as the tree becomes incomplete
            * then memoize the tree and its phrases
        '''
        if parent_tree is None:
            current_node = TreeNode(current_rule)
        elif came_from:
            if gn.force_recurse_right:
                if not current_rule.is_left_recursive:
                    pass
                else: # climb up tree to where I can insert the copied node
                    #parent_tree = TreeNode.copy_tree(parent_tree)
                    current_node = TreeNode.insert_left_recursive_node(parent_tree, TreeNode(current_rule))
            elif came_from.data.gn.is_choice: # insert to the left
                current_node = TreeNode(current_rule, parent=parent_tree)
                parent_tree.left = current_node
                current_node.is_left_child = True
            elif came_from.data.gn.force_recurse_right: # insert to the right of prev area...
                p = TreeNode.find_right_recursive(parent_tree)
                current_node = TreeNode(current_rule, parent=p)
                p.right = current_node
                current_node.is_right_child = True
            else: # insert to the right
                current_node = TreeNode(current_rule, parent=parent_tree)
                parent_tree.right = current_node
                current_node.is_right_child = True

        print('root')
        print(current_node.get_root_and_correct_parents())
        print('current tree')
        print(current_node)
        current.cache = current_node
        print('')

        #_ = input("")

        ## NOW, DO HEURISTIC
        return self.heuristic_cost_estimate(current.data.ops_path, goal)

    def heuristic_cost_estimate(self, curr, goal):
        '''
        The number of operations we need to add to the current program
        to the goal program

        Measure the two programs up to the point of deviance
        anything after in `curr` must be undone, do those operations in *reverse*
        then add the remainder goal operations

        increase the cost if we see undo/inverse operations that aren't all unique
        the cost has to be infinity if we see [ or ] wherever it doesn't belong

        TODO: I think a problem with this is that I have a lot of ops where I have to add wrong ones to it first in order for it to be correct...
        '''

        i = 0
        min_len = min(len(curr), len(goal))
        while i < min_len and curr[i] == goal[i]:
            i += 1
        # so now curr[i] != goal[i], or we ran out of space
        undo_ops = curr[i:] # need to undo these operations

        h = len(undo_ops)

        prev_o = undo_ops[0] if len(undo_ops) > 1 else None
        for o in undo_ops:
            if o == '[' or o == ']':
                return inf
            if o != prev_o:
                h += 0.2 # TODO: tweak these values, idk

        h += len(goal[i:])
        print(curr, ' ' * 20, '\r', end='')
        return h

    def distance_between(self, n1, n2):
        return 0.1 + 0.9 * n2.gn.node.word_cost

    def neighbors(self, node):
        neighbors = node.gn.get_neighbors()
        for n in neighbors:
            g = GraphSearchNode(n, node.ops_path.copy())
            g.add_ops(n.ops)
            yield g

    def path_is_goal_reached(self, current, goal):
        current.data.gn.get_neighbors()
        is_reached = current.data.ops_path == goal and current.data.gn.is_terminal
        if is_reached:
            print(current.cache.get_root())
        return is_reached

import re
def find_bf(bf):
    '''
    Separate a bf string into the following paths:
    * `.` as its own symbol
    * `,` as its own symbol
    '''
    bf_strings = [list(s) for s in re.split(r'([.,])', bf) if s]
    print(bf_strings)

    paths = []
    for s in bf_strings:
        if s == [',']:
            paths.append(',')
        elif s == ['.']:
            paths.append('.')
        else:
            #print('goal:', s)
            path = GraphFinder().astar(GraphSearchNode(root, []), s)
            paths.append(path)
    return paths


def choice_search():
    curr = root
    path = []
    while curr.get_neighbors():
        if not curr.is_choice:
            path.append(curr)
        s = [
                f'{i + 1}. {"choice:" if n.is_choice else ""} {n.node.rule_str}\n  Commitments: {n.commitments}'
             for i, n in enumerate(curr.neighbors)
            ]
        print('\n'.join(s))
        print("Current path:", " ".join([f'({n.node.rule_str})' for n in path]))
        print(curr.ops_path, curr.is_exit)
        i = int(input("Choice: ").strip())
        curr = curr.neighbors[i-1]
        print('')

def main():

    paths = find_bf('++++++')
    #paths = find_bf('++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++.>+.+++++++..+++.<<++.>+++++++++++++++.>.+++.------.--------.<<+.<.')
    #paths = find_bf('.+[.+]')
    for p in paths:
        for n in p:
            print(repr(n.gn), end=' ')
    print('')


    #choice_search()


if __name__ == '__main__':
    main()

