from common import combine_bf
from words import tree_to_leafs, tree_to_words
from rules import RuleNode
from trees import TreeNode, MemoTree
from astar import AStar
from math import inf
import random
import re

from collections import deque, defaultdict

class TreeSearchNode(TreeNode):
    def __init__(
        self, data, left=None, right=None, parent=None, third=None):#,word_node=None):
         super().__init__(data, left, right, parent, third)
         self.rule = self.data
         self.tags = {}
         #self.word_node = word_node

    @classmethod
    def _copy_node(cls, node):
        new = super()._copy_node(node)
        new.tags = node.tags.copy()
        return new

    def node_str(self):
        s = str(self.rule)
        return s + ' ' + (self.rule.ops if self.rule.ops else '')

    def get_neighbors(self, exclude_SP_SP=False):

        def highest_incomplete(node):
            '''
            yield neighbors from highest incomplete of node
            '''
            assert(not node.is_complete)

            # BFS for incomplete nodes
            is_incomplete = lambda n: n and not n.is_complete
            queue = deque([node])
            curr = None
            target_rule = None
            while target_rule is None:
                curr = queue.popleft()

                rule = curr.rule
                if curr.left is None:
                    target_rule = rule.l
                elif curr.right is None:
                    target_rule = rule.r
                elif curr.third is None:
                    target_rule = rule.third
                if target_rule:
                    break

                if is_incomplete(curr.left):
                    queue.append(curr.left)
                if is_incomplete(curr.right):
                    queue.append(curr.right)
                if is_incomplete(curr.third):
                    queue.append(curr.third)
            return curr, target_rule


        # starting nodes
        if self.rule is None:
            for r in RuleNode.rules.values():
                yield TreeSearchNode(r)
            return

        target_node = self

        # there is a current node otherwise
        # if we're calling `get_neighbors` then we've chosen the current node
        # so we have to "set it" into the tree
        #TreeNode._set_parent_ptrs(self)
        #TreeNode._set_child_ptrs(self)
        #if self.is_complete and self.parent and not self.parent.is_complete:
        #    self.parent.update_is_complete()

        #target_node = self
        while target_node.is_complete and target_node.parent:
            target_node = target_node.parent
        if not target_node.is_complete and target_node.rule.is_root:
            # the target node is incomplete at root
            # now search down the tree
            while None not in [target_node.left, target_node.right, target_node.third]:
                if target_node.left and not target_node.left.is_complete:
                    target_node = target_node.left
                elif target_node.right and not target_node.right.is_complete:
                    target_node = target_node.right
                else:
                    target_node = target_node.third

        # either have an incomplete node, or a node with no parent

        # add parents to a complete tree
        # do not set target_node parent pointer
        if target_node.is_complete:
            rule = target_node.rule
            lrules = RuleNode.nodes_by_left.get(rule.rule, set())
            rrules = RuleNode.nodes_by_right.get(rule.rule, set())#.difference(lrules)
            trules = RuleNode.nodes_by_third.get(rule.rule, set())#.difference(rrules)

            for l_parent in lrules:
                if exclude_SP_SP and l_parent.rule_str == "SP: SP SP":
                    continue
                copy_node = TreeSearchNode.copy_tree(target_node)
                parent = TreeSearchNode(l_parent, left=copy_node)
                copy_node.parent = parent
                copy_node.is_left_child = True
                assert(parent.left == copy_node)
                yield parent

            for r_parent in rrules:
                if exclude_SP_SP and r_parent.rule_str == "SP: SP SP":
                    continue
                copy_node = TreeSearchNode.copy_tree(target_node)
                parent = TreeSearchNode(r_parent, right=copy_node)
                copy_node.parent = parent
                copy_node.is_right_child = True
                assert(parent.right == copy_node)
                yield parent

            for t_parent in trules:
                copy_node = TreeSearchNode.copy_tree(target_node)
                parent = TreeSearchNode(t_parent, third=copy_node)
                copy_node.parent = parent
                copy_node.is_third_child = True
                #print(parent.third, copy_node)
                assert(parent.third == copy_node)
                yield parent
            #print('target node:', target_node.rule, str(id(target_node))[-5:])
            return

        # yield potential children from highest incomplete node
        # do not set target_node left/right/third pointers
        # BFS
        #target_node, target_rule = highest_incomplete(target_node.get_root())
        # DFS
        rule = target_node.rule
        target_rule = rule.l if target_node.left is None else (rule.r if target_node.right is None else rule.third)
        for rule in RuleNode.nodes[target_rule]:
            parent = TreeSearchNode.copy_tree(target_node) # TODO
            child = TreeSearchNode(rule, parent=parent)
            if target_node.left is None:
                child.is_left_child = True
                parent.left = child
            else:
                if target_node.right is None:
                    child.is_right_child = True
                    parent.right = child
                else:
                    child.is_third_child = True
                    parent.third = child
            #if child.is_complete and and not parent.is_complete:
            #    parent.update_is_complete()
            yield child

    @property
    def ops_path(self) -> list:
        '''
        Returns an array for the ops of the tree
        Override to not save ops path unless tree is complete
        and to insert "None" nodes
        '''
        if self._ops_path is not None:
            return self._ops_path

        def helper(node):
            if node is False:
                return []
            if node is None:
                return [None]
            left = helper(node.left)
            right = helper(node.right)
            third = helper(node.third)

            return combine_bf(left, node.rule.ops, right, third)
        ops_path = helper(self)
        if self.is_complete:
            self._ops_path = ops_path
        return ops_path

    def __hash__(self):
        def helper(node):
            if not node:
                return hash(node)
            return hash((helper(node.left), hash(node.data), helper(node.right), helper(node.third)))
        root = self.get_root_and_correct_parents()
        return helper(root)


#r = RuleNode.rules
#pet_name_tree = TreeSearchNode(r['SP: DP VP'])
pet_name_tree = '''* SP: DP VP
  * DP: Pronoun
  * VP: V'
    * Leaf
    * V': TV DP
      * Leaf
      * DP: D'
        * Leaf
        * D': D NP
          * Leaf
          * NP: N'
            * Leaf
            * N': AP N'
              * None
              * None'''
#                * Leaf
#                * Leaf'''

pet_name_root = TreeSearchNode.str_to_tree(pet_name_tree)
pet_name_root.tags['pet_name'] = True

def highest_cost_common_substring(s, t, cost):
    '''
    Return max cost common substring in s and t

    dp[i][j] will store a tuple (curr_cost, length)
    for a string ending at s[i] t[j]
    '''
    n, m = len(s), len(t)
    dp = [[(-inf, 0) for _ in range(m + 1)] for _ in range(n + 1)]
    best_cost = -inf
    best_i = 0
    best_length = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                c = cost.get(s[i - 1], 1)
                # Option 1: start a new common substring with s[i-1]
                option1 = (c, 1)
                # Option 2: extend the common substring ending at s[i-2] and t[j-2]
                # (only if extending gives a higher cost than starting over)
                prev_cost, prev_len = dp[i - 1][j - 1]
                option2 = (prev_cost + c, prev_len + 1) if prev_cost + c > c else option1
                dp[i][j] = option2

                # Update best result if needed.
                if dp[i][j][0] > best_cost:
                    best_cost = dp[i][j][0]
                    best_i = i
                    best_length = dp[i][j][1]
            else:
                dp[i][j] = (-inf, 0)

    if best_cost == -inf:
        return 0, [0] * n
    #^we just return 0 now for best cost if no overlap, my implementation

    # Extract the substring from s.
    start = best_i - best_length
    mask = [1 if start <= i and i < best_i else 0 for i in range(n)]
    return best_cost, mask


def heuristic(ops_path, goal, pweights, nweights):
    score, substring_mask = highest_cost_common_substring(ops_path, goal, pweights)
    score *= -1
    #^ the negative (good) score due to the overlap

    # now get the cost from the parts of ops_path that aren't in goal
    if score != inf:
        for i, mult in enumerate(substring_mask):
            if mult == 0:
                score += nweights.get(ops_path[i], 0)

    return score, substring_mask

pweights = {
    "[": 12,
    "]": 8,
    "+": 6,
    "-": 6,
    #">": 2,
    #"<": 2,
}
nweights = {
    "[": inf,
    "]": inf,
    "+": 3,
    "-": 3,
    ">": 1,
    "<": 1,
}

class TreeFinder(AStar):

    def __init__(self):
        self._pweights = pweights.copy()
        self._nweights = nweights.copy()

    def astar(self, start, goal, reversePath = False, flag=False):
        self._allArr = True
        for c in goal:
            if c not in [None, '>', '<']:
                self._allArr = False
        if self._allArr:
            self._nweights[">"] = 2
            self._nweights["<"] = 2
            self._nweights["+"] = inf
            self._nweights["-"] = inf
            self._pweights["<"] = 6
            self._pweights[">"] = 6

        #self.start_time = time.time()
        return super(TreeFinder, self).astar(start, goal, reversePath, flag)

    def path_heuristic_cost_estimate(self, current, goal, flag=False):
        score, substring_mask = self.heuristic_cost_estimate(current.data, goal, flag)
        root = current.data.get_root() if current.data else None

        if root and root.is_complete and root.rule.is_root:
            # if the tree is finished but there's no overlap
            if 1 not in substring_mask:
                return inf
            if flag and not (substring_mask == [1] * len(goal)):
                score += 2


        '''if root and root.is_complete and root.rule.is_root:# and substring_mask == [1] * len(goal):
            print('hey', score, score + current.gscore, root.ops_path, goal)
            print(root)
            print(root.get_leafs())
            _ = input('')'''
        '''print('hey', score, score + current.gscore, root.ops_path, goal)
        print(root)
        print(root.ops_path)
        _ = input('')'''

        '''
        TODO: hack, literally hard-coded in, not great...
        But prevent >/< goals from finding rules with AdvP / AP
        '''
        if self._allArr and current.data:
            rule_str = current.data.rule.rule_str
            if 'AP' in rule_str or 'AdvP' in rule_str:
                return inf

        return score


    def heuristic_cost_estimate(self, current, goal, flag=False):
        '''
        score is positive weighted for everything in the overlap,
        negatively weighted for everything not in overlap
        find overlap of max cost
        '''
        if current is None:
            return inf, []

        ops_path = current.get_root().ops_path

        score, substring_mask = heuristic(ops_path, goal, self._pweights, self._nweights)
        # if we have > 3 None's in our string, penalize the shit out of that
        if ops_path.count(None) >= 3:
            score += 20

        return score, substring_mask

    def distance_between(self, n1, n2):
        #return 1 + 5 * n2.rule.word_cost
        return 0.2 + 1 * n2.rule.word_cost

    def path_neighbors(self, search_node):
        if not search_node.data:
            return self.neighbors(None)

        search_node.data = TreeSearchNode.copy_tree(search_node.data)
        current = search_node.data
        neighbors = self.neighbors(current)

        '''print('hey', search_node.fscore, search_node.fscore + search_node.gscore)
        root = search_node.data.get_root()
        print(root)
        print(root.ops_path)
        _ = input('')'''

        return neighbors

    def neighbors(self, current):
        if current is None:
            #for r in RuleNode.rules.values():
            #    yield TreeSearchNode(r)
            return [TreeSearchNode(r) for r in RuleNode.rules.values()]
        #yield from current.get_neighbors()
        return list(current.get_neighbors(exclude_SP_SP=True))

    def is_goal_reached(self, current, goal):
        if current is None:
            return False
        root = current.get_root_and_correct_parents()
        #goal = [c for c in goal]
        #return root.is_complete and root.rule == RuleNode.root and root.ops_path == goal
        #return False
        return root.is_complete and root.rule.is_root

class MemoTreeFinder(TreeFinder):
    def is_goal_reached(self, current, goal):
        if current is None:
            return False
        root = current.get_root()
        ret = root.is_complete and root.rule.is_root and root.ops_path == list(goal)
        if ret:
            print(root)
            print(tree_to_leafs(root))
            if input('save tree? (y/n) ') == 'y':
                return True
        return False

class TreeSearchMemoTree(MemoTree):
    _default_fname = 'ts_trees.pkl'
    table = defaultdict(set)

    def add_entry(self, tree):
        copy = TreeSearchNode(tree.data) # the tree should have no parents
        copy.left = tree.left
        copy.right = tree.right
        copy.third = tree.third

        assert(copy.is_complete)
        copy.assert_correct()

        bf = ''.join(copy.ops_path)
        self.table[bf].add(copy)

    def initialize(self):
        '''
        Program to add entries to memoized tree
        '''
        user_in = None
        while user_in != "quit":
            if user_in:
                print('looking for', user_in)
                tf = MemoTreeFinder()
                path = list(tf.astar(None, user_in))
                root = path[-1].get_root()
                self.add_entry(root)
            user_in = input('Enter bf program to add to tree or `quit`: ')

    def update(self):
        print(self)
        self.initialize()
        save = input("save? (y/n)")
        if save == "y":
            self.save_to_file()
            print(self)

    def delete(self):
        user_in = None
        split_pattern = r'\s*,\s*|\s+'

        while True:
            print(self)
            user_in = input('Enter key to modify in tree or `quit`: ')
            if user_in == 'quit':
                break
            entry = self.table[user_in]
            names = [(self.tree_to_str(t), t) for t in list(entry)]
            for idx, name in enumerate(names, 1):
                print(f"{idx}. {name[0]}")
            indices = input("\nIndices to delete: ")
            indices = [int(i)-1 for i in re.split(split_pattern, indices)]

            for i in indices:
                tree = names[i][1]
                entry.remove(tree)
            print('removed entries')
        print(self)
        save = input("save? (y/n)")
        if save == "y":
            self.save_to_file()


    def tree_to_str(self, tree):
        return tree_to_leafs(tree)

    def __str__(self):
        s = []
        for key, value in self.table.items():
            s.append(key)
            for tree in value:
                s.append("  * " + self.tree_to_str(tree))
        return '\n'.join(s)


def find_bf_once(bf):
    path = TreeFinder().astar(None, bf)
    print('path')
    path = list(path)
    root = path[-1].get_root_and_correct_parents()
    print(root)
    print(root.ops_path, bf)
    print(TreeFinder().heuristic_cost_estimate(root, bf))


def invert_bf(bf):
    if bf is None:
        return []
    inv_d = {
        "+": "-",
        "-": "+",
        ">": "<",
        "<": ">",
    }
    inv = [inv_d[c] for c in reversed(bf)]
    return inv

def find_bf(bf, memo = None, depth=0):
    """
    Recursively finds and stitches together bf segments
    into a final solution tree.
    """
    if not bf:
        return False

    bf_str = ''.join(bf) if type(bf) == list else bf
    #print(' ' * depth, 'recursing on', bf_str)

    '''
    Choose from memo tree with percentage weighted on the cost of the tree
    '''
    if memo and bf_str in memo.table:
        choices = list(memo.table[bf_str])
        weights = [1/ t.get_cost() for t in choices]
        root = random.choices(choices, weights=weights, k=1)[0]
        node = TreeNode(root, third=False)
        return node

    # greedily find best program
    tf = TreeFinder()
    path = None
    if "+++" in bf_str and random.random() < 0.99995:
        # 50% chance to use "You are my <adjectives> <petname>" type tree...
        # so now, also do "skip none" heuristic
        path = list(tf.astar(pet_name_root, bf, flag=True))
        #TODO: iron this out
    else:
        path = list(tf.astar(None, bf))
    root = path[-1].get_root()
    score, mask = tf.heuristic_cost_estimate(root, bf)
    del tf

    '''
    We're guranteed to get a contiguous string of 1's in our mask
    Find the portion of root.ops_path that ends up in bf -- call this `prog_overlap`
    Get l_remainder and r_remainder around prog_overlap
    split bf around `prog_overlap`, l_bf, r_bf
    recurse on l_bf + l_remainder_inverse, r_remainder_inverse + r_bf
    '''
    prog = root.ops_path

    start_idx = mask.index(1)
    end_idx = len(mask) - 1 - mask[::-1].index(1)

    prog_overlap = prog[start_idx:end_idx + 1]

    #print(' ' * depth, 'found', ''.join(prog_overlap), 'in', ''.join(prog))

    l_remainder = invert_bf(prog[:start_idx] or None)
    r_remainder = invert_bf(prog[end_idx + 1:] or None)


    # Find where prog_overlap matches inside bf, get l_bf and r_bf
    bf = list(bf) if type(bf) == str else bf
    overlap_start = next(
        i for i in range(len(bf) - len(prog_overlap) + 1)
        if bf[i:i + len(prog_overlap)] == prog_overlap
    )
    overlap_end = overlap_start + len(prog_overlap)
    l_bf = bf[:overlap_start]
    r_bf = bf[overlap_end:]


    # recurse
    node = TreeNode(root, third=False)
    left = find_bf(combine_bf(l_bf, l_remainder), memo, depth+1)
    right = find_bf(combine_bf(r_remainder, r_bf), memo, depth+1)

    TreeNode.insert_left(node, left)
    TreeNode.insert_right(node, right)

    ops_path_tree = combine_bf(*[tree.ops_path for tree in node.get_data()])
    #print(bf, ops_path_tree)
    assert(bf == ops_path_tree)

    return node


def choice_search():
    curr = None
    path = []
    neighbors = [TreeSearchNode(r) for r in RuleNode.rules.values()]


    while neighbors:
        print('-' * 80)
        # present choices
        s = [
                f'{i + 1}. {n.rule.rule_str} {n.get_root().ops_path}'
             for i, n in enumerate(neighbors)
            ]
        print('\n'.join(s))
        i = int(input("Choice: ").strip())

        # made the choice
        curr = neighbors[i-1]
        TreeNode._set_parent_ptrs(curr)
        print('')

        neighbors = list(curr.get_neighbors(exclude_SP_SP=True))
        path.append(curr)
        #root = curr.get_root_and_correct_parents()
        root = curr.get_root()
        root.assert_correct()
        print('Current tree')
        print(curr)
        print('-' * 10)
        print('Current root')
        print(root)
        print('Current path')
        print(root.ops_path)

    M = TreeSearchMemoTree()
    M.load_from_file()
    print(tree_to_leafs(root))
    save = input('add to memo table? (y/n)')
    if save == 'y':
        M.add_entry(root)
        M.save_to_file()
        print(M)

def main():
    M = TreeSearchMemoTree()
    M.load_from_file()
    #M.update()

    #choice_search()

    import time
    '''avg_time = 0
    trials = 100
    for i in range(trials):
        stime = time.time()
        #find_bf(">>>>>>>>>")
        find_bf_once("[[[[[")
        avg_time += time.time()-stime
        print(i, ' ' * 20, '\r', end='')
    print(avg_time / trials)'''

    stime = time.time()
    #find_bf("++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++")
    #find_bf("++++[>+++++<-]>[<+++++>-]+<+[>[>+>+<<-]++>>[<<+>>-]>>>[-]++>[-]+>>>+[[-]++++++>>>]<<<[[<++++++++<++>>-]+<<[>----<-]<]<<[>>>>>[>>>[-]+++++++++<[>-<-]+++++++++>[-[<->-]+[<<<]]<[>+<-]>]<<-]<<-]")
    sentence_tree = find_bf("++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++.>+.+++++++..+++.<<++.>+++++++++++++++.>.+++.------.--------.<<+.<.", memo = M)
    #sentence_tree = find_bf("++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++", memo=M)
    #sentence_tree = find_bf(">>", memo=M)
    #find_bf_once("[")
    #find_bf("<")
    #find_bf(">>>>>>>>")
    print(time.time()-stime)
    print(sentence_tree)

    print('tree to leafs', [tree_to_leafs(tree) for tree in sentence_tree.get_data()])
    #print(tree_to_words(sentence_tree.data))
    print('. '.join([tree_to_words(tree) for tree in sentence_tree.get_data()]))
    print(''.join(combine_bf(*[tree.ops_path for tree in sentence_tree.get_data()])))

if __name__ == '__main__':
    main()
