from common import combine_bf
from rules import RuleNode
from trees import TreeNode, MemoTree
from astar import AStar
from math import inf
import copy

class TreeNode(TreeNode):
    @classmethod
    def find_right_recursive(cls, tree):
        '''
        Return the next ancestor that has a left node
        '''
        if tree.left:
            return tree

        c = tree
        while c and c.parent is not None:
            TreeNode._set_parent_ptrs(c)
            if c.is_left_child:
                return c.parent
            c = c.parent
        raise Exception("find right recursive failed")

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
            TreeNode._set_parent_ptrs(curr)
            curr = curr.parent
        if curr is None:
            print('looking for', target_rule)
            print('inserting rule', node.data)
            print(tree.get_root_and_correct_parents())
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
        TreeNode._set_parent_ptrs(node) # left/right child status

        curr.is_left_child = True
        curr.is_right_child = None
        node.left = curr # insert curr as left child of node
        return node

    def get_rightmost_node(self):
        curr = self
        while curr.left or curr.right or curr.third:
            if curr.right or curr.third:
                curr = curr.third if curr.third else curr.right
            else:
                curr = curr.left
        return curr

    @classmethod
    def memoize_tree(cls, memo, node):
        '''
        Starting at the node `node`, go up its ancestors while each one is complete
        memoize the subtree rooted at that node
        '''
        c = node
        while c and c.is_complete:
            if type(c.data) == RuleNode:
                key = c.data.rule
                h = c.__hash__()
                if h not in memo.get(key, set()):
                    c.ops_path # compute the ops path before memoization

                    copy = cls(c.data) # the tree should have no parents
                    copy.left = c.left
                    copy.right = c.right
                    copy.third = c.third
                    memo[key] = memo.get(key, set()).union(set([copy]))
            cls._set_parent_ptrs(c)
            c = c.parent

        return memo

    @classmethod
    def construct_down_from_tree(cls, node, max_height):
        '''
        Return all possible complete subtrees starting from node, of height
        less than max_height
        '''
        if max_height <= 0:
            return None

        if node.is_complete:
            yield node

        r_trees = []
        l_trees = []
        # get all possible right/left subtrees
        def create_children(child_list, child_tree, target_rule):
            if child_tree is None:
                for rule in RuleNode.nodes.get(target_rule, set()):
                    root = cls(rule)
                    for child in cls.construct_down_from_tree(root, max_height-1):
                        child_list.append(child)
        create_children(r_trees, node.right, node.data.r)
        create_children(l_trees, node.left, node.data.l)
        create_children(r_trees, node.third, node.data.third)
        l_trees = l_trees if l_trees else [None]
        r_trees = r_trees if r_trees else [None]

        # create all products of left/right trees
        for left, right in itertools.product(l_trees, r_trees):
            node = cls._copy_node(node)
            if left:
                cls.insert_left(node, left)
            if right:
                cls.insert_right(node, right)
            if node.is_complete:
                yield node

    @classmethod
    def construct_from_tree(cls, node, max_height):
        '''
        Return all possible trees starting from node, of height
        less than max_height
        '''
        if max_height <= 0:
            return None

        rule = node.data
        '''
        The tree is not complete
        Find out if it needs a left or right child
        '''
        if not node.is_complete:
            for tree in cls.construct_down_from_tree(node, max_height):
                yield tree
            return None
        '''
        The tree is complete
        Add a parent to it, and then recurse on that
        '''
        assert(not node.parent)
        assert(not node.is_left_child and not node.is_right_child and not node.is_third_child)
        yield node

        for l_parent in RuleNode.nodes_by_left.get(rule.rule, set()):
            lnode = cls.copy_subtree(node)
            parent = cls(l_parent)
            cls.insert_left(parent, lnode)
            yield from cls.construct_from_tree(parent, max_height - 1)

        for r_parent in RuleNode.nodes_by_right.get(rule.rule, set()):
            rnode = cls.copy_subtree(node)
            parent = cls(r_parent)
            cls.insert_right(parent, rnode)
            yield from cls.construct_from_tree(parent, max_height - 1)

        for t_parent in RuleNode.nodes_by_third.get(rule.rule, set()):
            tnode = cls.copy_subtree(node)
            parent = cls(t_parent)
            cls.insert_right(parent, tnode)
            yield from cls.construct_from_tree(parent, max_height - 1)

class MemoTree(MemoTree):
    # 25 trees of height 6
    # crazy number of trees of length 7 and 8; or an infinite loop
    def initialize(self, max_height=6, fname=None):
        '''
        Construct and memoize all complete trees of height n
        '''
        RuleNode.load_from_file()
        for rule in RuleNode.rules.values():
            if rule.is_r_leaf and rule.is_l_leaf:
                rule_tree = self.cls(rule)
                for tree in self.cls.construct_from_tree(rule_tree, max_height):
                    if tree:
                        tree.assert_correct()
                        self.cls.memoize_tree(self.table, tree)
        return self.table

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

        self.target_rule = None

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
        self.target_rule = target_rule

        if target_rule is not None:
            target_rule_nodes = self._tree.nodes[target_rule]
            # ^ all tree nodes that correspond to this rule

            for n in target_rule_nodes:
                # add all rules of form (TargetRule: (Leaf) TR_R)
                if n.is_l_leaf:
                    #commitments = copy.deepcopy(self.commitments)
                    commitments = self.copy_commitments()
                    commitments[-1] += [n]
                    g = GraphNode(commitments, n)
                    self._add_neighbor(neighbors, g)


                # add all right-recursive choice node rules of form (TR: TR_L TR)
                # scratch that, I think this is just an else case
                #if n.is_right_recursive:
                elif not n.is_left_recursive:
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
                    g = GraphNode([[RuleNode.root]], RuleNode.root, is_choice=True)
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
                    continue

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
        if self.force_recurse_right:
            return 'FRR: ' + repr(self.node)
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

class GraphSearchNode:
    '''
    A wrapper for graph nodes and ops_path
    Does not hash, or no equality...
    '''
    def __init__(self, ops_path, gn=None, tree=None):
        self.gn = gn
        self.tree = tree
        self.ops_path = ops_path

    def add_ops(self, ops):
        '''
        Merge ops with our own ops_path
        '''
        if ops:
            self.ops_path = combine_bf(self.ops_path, ops)
        return self.ops_path

    def get_neighbors(self, memo=None):
        def graph_node_neighbors(gn):
            neighbors = gn.get_neighbors()
            for n in neighbors:
                g = GraphSearchNode(self.ops_path.copy(), n)
                g.add_ops(n.ops)
                yield g

        if self.gn and not self.tree:
            yield from graph_node_neighbors(self.gn)

            if memo:
                target_rule = self.gn.target_rule
                for t in memo.table.get(target_rule, []):
                    t = TreeNode.copy_tree(t)
                    g = GraphSearchNode(self.ops_path.copy(), self.gn, tree=t)
                    g.add_ops(t.ops_path)
                    yield g
        elif self.tree:
            '''
            Recreate the exit graph node and return the neighbors of that
            if the tree is a left child:
                * the parent gn is a choice node
                * it has a spawning node, the self.gn that spawned it, commitments go under that
            if the tree is a right child:
                * commitments just get extended onto to self.gn commitments[-1]
            '''
            # the tree is a left child
            #if self.gn.is_choice:

            commitments = self.gn.copy_commitments()
            new_seen = []
            curr = self.tree
            # get to the right exit node, while recreating commitments
            while curr and (curr.right or curr.left or curr.third):
                if curr.right or curr.third:
                    new_seen.append(curr.data)
                    curr = curr.third if curr.third else curr.right
                elif curr.left:
                    commitments[-1].extend(new_seen)
                    new_seen = []
                    commitments.append([curr]) # new spawning node
                    curr = curr.left
            commitments[-1].extend(new_seen)

            exit_node = GraphNode(commitments, curr.data)
            yield from graph_node_neighbors(exit_node)


root = GraphNode([[RuleNode.root]], RuleNode.root, is_choice = True)

M = MemoTree()
M.load_from_file()

class GraphFinder(AStar):

    def _print_path(self, current):
        came_from = current.came_from
        gn = current.data.gn
        print("Path (reverse order):")
        c = current.came_from
        print(repr(gn), end=' || ')
        while c:
            if c.data.tree:
                print(repr(c.data.tree), end=" || ")
            else:
                print(repr(c.data.gn), end=" || ")
            c = c.came_from
        print('')

    def path_heuristic_cost_estimate(self, current, goal):
        came_from = current.came_from

        tree = current.data.tree
        if tree:
            # if a tree is an option it must be either the left
            # or right subtree of the node that we previously came from
            parent_tree = TreeNode.copy_tree(came_from.cache)

            if came_from.data.gn.is_choice: # left subtree
                TreeNode.insert_left(parent_tree, tree)
            else: # right subtree
                TreeNode.insert_right(parent_tree, tree)

            current.cache = parent_tree.get_rightmost_node()

            #current.cache.get_root_and_correct_parents().assert_correct() #TODO
            return self.heuristic_cost_estimate(current.data.ops_path, goal)

        gn = current.data.gn
        current_rule = gn.node

        if came_from is None or (gn.is_choice and current_rule == RuleNode.root):
            current.cache = None
        else:
            current.cache = TreeNode.copy_tree(came_from.cache)

        parent_tree = current.cache
        # Generate the tree
        current_node = TreeNode(current_rule)

        if parent_tree is None:
            pass
        elif came_from:
            if gn.force_recurse_right:
                if not current_rule.is_left_recursive:
                    # climb up the current tree to get the FRR node
                    # but don't insert anything
                    curr = parent_tree
                    while curr and not (curr and curr.data == gn.node and curr.left):
                        TreeNode._set_parent_ptrs(curr)
                        curr = curr.parent

                    current_node = curr
                else: # climb up tree to where I can insert the copied node
                    current_node = TreeNode.insert_left_recursive_node(parent_tree, current_node)
            elif came_from.data.gn.is_choice: # insert to the left
                TreeNode.insert_left(parent_tree, current_node)
            elif came_from.data.gn.force_recurse_right: # insert to the right of prev area...
                p = TreeNode.find_right_recursive(parent_tree)
                TreeNode.insert_right(p, current_node)
            else: # insert to the right
                TreeNode.insert_right(parent_tree, current_node)
        else:
            current_node = parent_tree

        current.cache = current_node

        #if the node is an exit node:
        #    * convert the node and what came before it into a tree
        #    * but stop, as soon as the tree becomes incomplete
        #    * then memoize the tree and its phrases
        #actually:
        #    * just memoize current tree
        #TODO: make this more memory efficient by only creating trees in this case
        if gn.is_exit:
            TreeNode.memoize_tree(M.table, current_node)
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
        #print(curr, ' ' * 20, '\r', end='')
        return h

    def distance_between(self, n1, n2):
        if n2.tree:
            return n2.tree.get_cost()
        elif n2.gn:
            return 0.1 + 0.9 * n2.gn.node.word_cost

    def path_neighbors(self, search_node):
        node = search_node.data
        # TODO: this is where I toggle memoization
        #for n in node.get_neighbors(M):
        for n in node.get_neighbors():
            yield n

    def path_is_goal_reached(self, current, goal):
        gn = current.data.gn
        is_reached = current.data.ops_path == goal
        if is_reached:
            if gn and not current.data.tree:
                gn.get_neighbors()
                is_reached &= current.data.gn.is_terminal
            elif current.data.tree:
                is_reached &= gn.is_exit and current.cache.get_root().is_complete
            #if is_reached:
                #print(current.cache.get_root())
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
            path = GraphFinder().astar(GraphSearchNode([], root), s)
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
    #choice_search()

    import time
    stime = time.time()
    #paths = find_bf('>+>+++>+++++++>++++++++++<<<<-')
    #paths = find_bf('>>>>>>>>')
    paths = find_bf('+++++++++')
    print(time.time()-stime)
    #paths = find_bf('++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++.>+.+++++++..+++.<<++.>+++++++++++++++.>.+++.------.--------.<<+.<.')
    #paths = find_bf('.+[.+]')
    for p in paths:
        for n in p:
            if n.tree:
                print('(', end='')
                for tn in n.tree.get_data():
                    print(repr(tn), end=" || ")
                print(')', end='')
            elif not n.gn.is_choice:
                print(repr(n.gn.node), end=" || ")
    print('')




if __name__ == '__main__':
    main()

