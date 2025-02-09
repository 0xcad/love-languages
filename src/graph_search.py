from common import combine_bf
from rules import RuleNode
from trees import TreeNode, MemoTree
from astar import AStar
from math import inf
import copy

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
        '''
        Generate the tree
        '''
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

        '''
        if the node is an exit node:
            * convert the node and what came before it into a tree
            * but stop, as soon as the tree becomes incomplete
            * then memoize the tree and its phrases
        actually:
            * just memoize current tree
        TODO: make this more memory efficient by only creating trees in this case
        '''
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
        print(curr, ' ' * 20, '\r', end='')
        return h

    def distance_between(self, n1, n2):
        if n2.tree:
            return n2.tree.get_cost()
        elif n2.gn:
            return 0.1 + 0.9 * n2.gn.node.word_cost

    def path_neighbors(self, search_node):
        node = search_node.data
        for n in node.get_neighbors(M):
        #for n in node.get_neighbors():
            yield n

    def path_is_goal_reached(self, current, goal):
        gn = current.data.gn
        is_reached = current.data.ops_path == goal
        if is_reached:
            if gn and not current.data.tree:
                gn.get_neighbors()
                is_reached &= current.data.gn.is_terminal
            elif current.data.tree:
                is_reached &= current.cache.get_root().is_complete
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
    paths = find_bf('>+>')
    print(time.time()-stime)
    #paths = find_bf('++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++.>+.+++++++..+++.<<++.>+++++++++++++++.>.+++.------.--------.<<+.<.')
    #paths = find_bf('.+[.+]')
    for p in paths:
        for n in p:
            print(repr(n.gn), end=' ')
    print('')




if __name__ == '__main__':
    main()

