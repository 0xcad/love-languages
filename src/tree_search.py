from common import combine_bf
from rules import RuleNode
from trees import TreeNode, MemoTree
from astar import AStar
from math import inf

from collections import deque
import pylcs

class TreeSearchNode(TreeNode):

    def __init__(self, data, left=None, right=None, parent=None, third=None):
         super().__init__(data, left, right, parent, third)
         self.rule = self.data

    @classmethod
    def _copy_node(cls, node):
        new = super()._copy_node(node)
        #new._d_id = node._d_id
        return new

    def assert_correct(self, dids=None):
        root = super().assert_correct()
        if not dids:
            return
        dids = set(dids)
        def correct_dids(node):
            if not node:
                return
            try:
                assert(node.d_id() in dids)
            except Exception as e:
                raise Exception(node.rule, node.d_id(), dids)
            dids.remove(node.d_id())
            correct_dids(node.left)
            correct_dids(node.right)
            correct_dids(node.third)

        def helper(node):
            correct_dids(node)
            assert(len(dids) == 0)
        try:
            helper(root)
            return root
        except Exception as e:
            print('ERROR')
            print(root)
            raise Exception(e)

    def node_str(self):
         s = super().node_str()
         return s + ' ' + (self.rule.ops if self.rule.ops else '')

    def get_neighbors(self, memo=None):

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


        # either have an incomplete node, or a node with no parent

        # add parents to a complete tree
        # do not set target_node parent pointer
        if target_node.is_complete:
            rule = target_node.rule
            lrules = RuleNode.nodes_by_left.get(rule.rule, set())
            rrules = RuleNode.nodes_by_right.get(rule.rule, set())#.difference(lrules)
            trules = RuleNode.nodes_by_third.get(rule.rule, set())#.difference(rrules)
            for l_parent in lrules:
                copy_node = TreeSearchNode.copy_tree(target_node)
                parent = TreeSearchNode(l_parent, left=copy_node)
                copy_node.parent = parent
                copy_node.is_left_child = True
                assert(parent.left == copy_node)
                yield parent

            for r_parent in rrules:
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
        #return [0] * n, best_cost
        return [], best_cost

    # Extract the substring from s.
    start = best_i - best_length
    mask = [1 if start <= i and i < best_i else 0 for i in range(n)]
    #print('hey', mask, start, best_i, best_length)
    #return s[start:best_i], best_cost
    return mask, best_cost


def heuristic(ops_path, goal, pweights, nweights):
    substring_mask, score = highest_cost_common_substring(ops_path, goal, pweights)
    score *= -1
    #^ the negative (good) score due to the overlap

    # this means that there is no match
    if score == inf:
        return score, substring_mask

    # if we have a perfect match then thats' pretty good
    if len(substring_mask) == len(goal):
        return min(-100, score), substring_mask

    # now get the cost from the parts of ops_path that aren't in goal
    for i, mult in enumerate(substring_mask):
        if mult == 0:
            score += nweights.get(ops_path[i], 0) * 2

    return score, substring_mask


class TreeFinder(AStar):
    _pweights = {
        "[": 12,
        "]": 12,
        "+": 6,
        "-": 6,
        #">": 2,
        #"<": 2,
    }
    _nweights = {
        "[": inf,
        "]": inf,
        "+": 3,
        "-": 3,
        #">": 1,
        #"<": 1,
    }
    _duration = 0.2
    _best_cost = inf
    _best_tree = None

    def astar(self, start, goal, reversePath = False):
        allArr = True
        for c in goal:
            if c not in [None, '>', '<']:
                allArr = False
        if allArr:
            self._nweights[">"] = 1
            self._nweights["<"] = 1
            self._nweights["+"] = inf
            self._nweights["-"] = inf

        self.start_time = time.time()
        self.duration = 0.5
        return super(TreeFinder, self).astar( start, goal, reversePath)

    def _print_path(self, current):
        path_len = 1
        dids = [current.data.d_id()]
        came_from = current.came_from
        print("Path (reverse order):")
        print(repr(current.data.rule), f'({str(id(current.data))[-5:]})', end=' || ')
        c = current.came_from
        while c and c.data:
            print(f'{c.data.rule} ({str(c.data.d_id())[-5:]})', end=" || ")
            if c.data:
                dids.append(c.data.d_id())
            path_len += 1
            c = c.came_from
        print('')
        return path_len, dids

    def path_heuristic_cost_estimate(self, current, goal):
        score, substring_mask = self.heuristic_cost_estimate(current.data, goal)
        '''root = current.data.get_root_and_correct_parents() if current.data else None
        if root and root.is_complete and root.rule == RuleNode.root:
            print('hey', score + current.gscore, root.ops_path, goal)
            print(root)
            _ = input('')'''
        return score


    def heuristic_cost_estimate(self, current, goal):
        '''
        score is positive weighted for everything in the overlap,
        negatively weighted for everything not in overlap
        find overlap of max cost
        '''
        if current is None:
            return inf, []

        ops_path = current.get_root().ops_path

        score, substring_mask = heuristic(ops_path, goal, self._pweights, self._nweights)
        return score, substring_mask

    def distance_between(self, n1, n2):
        #return 1 + 5 * n2.rule.word_cost
        return 1

    def path_neighbors(self, search_node):
        if not search_node.data:
            return self.neighbors(None)

        search_node.data = TreeSearchNode.copy_tree(search_node.data)
        current = search_node.data
        neighbors = self.neighbors(current)

        return neighbors

    def neighbors(self, current):
        if current is None:
            #for r in RuleNode.rules.values():
            #    yield TreeSearchNode(r)
            return [TreeSearchNode(r) for r in RuleNode.rules.values()]
        #yield from current.get_neighbors()
        return list(current.get_neighbors())

    def is_goal_reached(self, current, goal):
        if current is None:
            return False
        root = current.get_root_and_correct_parents()
        #return False
        # TODO, duration thing, but that may be in astar
        return root.is_complete and root.rule == RuleNode.root


def find_bf(bf):
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
    inv = [inv_d[c] for c in bf]
    return inv

def find_bf(bf, depth=0):
    if not bf:
        return False
    print(' ' * depth, 'recursing on', bf)

    '''
    Repeatedly find bf programs and stitch them together
    to a final solution
    '''
    tf = TreeFinder()
    path = list(tf.astar(None, bf))
    root = path[-1].get_root_and_correct_parents()
    score, mask = tf.heuristic_cost_estimate(root, bf)
    '''
    We're guranteed to get a contiguous string of 1's in our mask
    Find the portion of root.ops_path that ends up in bf -- call this `prog_overlap`
    Get l_remainder and r_remainder around prog_overlap
    split bf around `prog_overlap`, l_bf, r_bf
    recurse on l_bf + l_remainder_inverse, r_remainder_inverse + r_bf
    '''
    # find overlapping portion of program
    bf = [c for c in bf]
    prog = root.ops_path
    start = mask.index(1)
    end = len(mask) - 1 - mask[::-1].index(1)
    prog_overlap = prog[start:end+1]
    print(' ' * depth, 'found', prog_overlap, 'in', prog)
    l_remainder = invert_bf(prog[:start] if start > 0 else None)
    r_remainder = invert_bf(prog[end+1:] if end < len(prog) - 1 else None)

    #print("hey!", prog, bf)
    #print(prog_overlap, l_remainder, r_remainder)
    # split bf around prog_overlap
    start = next(i for i in range(len(bf) - len(prog_overlap) + 1) if bf[i:i+len(prog_overlap)] == prog_overlap)
    l_bf = bf[:start] if start > 0 else []
    r_bf = bf[end+1:] if end < len(bf) else []

    print('bf', bf)
    print('left', l_bf)
    print('l_reaminder', l_remainder)
    print('prog_overlap', prog_overlap)
    print('right_remainder', r_remainder)
    print('right', r_bf)
    #_ = input('')

    #print("hey!")
    #print(l_bf, r_bf)
    # recurse
    del tf
    node = TreeNode(prog_overlap)
    #left = find_bf(combine_bf(l_bf, l_remainder), depth+1)
    #right = find_bf(combine_bf(r_remainder, r_bf), depth+1)

    #TreeNode.insert_left(node, left)
    #TreeNode.insert_right(node, right)
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

        neighbors = list(curr.get_neighbors())
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


if __name__ == '__main__':
    #choice_search()
    import time
    '''avg_time = 0
    trials = 100
    for i in range(trials):
        stime = time.time()
        #find_bf(">>>>>>>>>")
        find_bf("+++++++")
        avg_time += time.time()-stime
        print(i, ' ' * 20, '\r', end='')
    print(avg_time / trials)'''
    stime = time.time()
    #find_bf("++++++++++[>+>+++>+++++++")
    find_bf("<")
    #find_bf(">>>>>>>>")
    print(time.time()-stime)
