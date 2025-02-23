from common import combine_bf
from rules import RuleNode
from trees import TreeNode, MemoTree
from astar import AStar
from math import inf

from collections import deque
import pylcs

# TODO: wildcard matching, etc, whatever
def lcs(s1, s2):
    s1 = ''.join([c if c else '*' for c in s1])
    s2 = ''.join([c if c else '*' for c in s2])
    res = pylcs.lcs_string_idx(s1, s2)
    #return [s2[i] for i in res if i != -1]
    return deque([i for i in res if i != -1])

class TreeSearchNode(TreeNode):

    def __init__(self, data, left=None, right=None, parent=None, third=None):
         super().__init__(data, left, right, parent, third)
         self.rule = self.data
         #self._d_id = None

    '''def d_id(self, arg=None):
        arg = self if arg is None else arg
        if arg is None:
            return id(None)

        if arg._d_id:
            return arg._d_id
        arg._d_id = id(arg)#str(id(self))[-5:]
        return arg._d_id'''

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
        '''
        If data is None: Return all rules -> all trees
        Else:
            If the node is not complete, return all incomplete nodes sorted by depth (BFS?)
            If node is complete, return possible parents

        Find the *highest* / least deep incomplete node, return neighbors of that
        '''
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
        return id(self)
        def helper(node):
            if not node:
                return hash(node)
            return hash((helper(node.left), hash(node.data), helper(node.right), helper(node.third)))
        root = self.get_root_and_correct_parents()
        return helper(root)


def heuristic(ops_path, goal):
    overlap = lcs(goal, ops_path)
    pweights = {
        "[": 12,
        "]": 12,
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
        #">": 1,
        #"<": 1,
    }
    score = 0
    '''
    overlap is an array of length of the overlap
    consisting of indices of 'ops_path' that are overlapping...
    '''
    for i in range(len(ops_path)):
        c = ops_path[i]
        if overlap and i == overlap[0]:
            score -= pweights.get(c, 1) * 2
            overlap.popleft()
        else:
            score += nweights.get(c, 0) * 2

    return score


class TreeFinder(AStar):
    #def path_heuristic_cost_estimate(self, current, goal):
    #    pass
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

        score = self.heuristic_cost_estimate(current.data, goal)
        return score


    def heuristic_cost_estimate(self, current, goal):
        '''
        huge TODO of course, this is just stupid shit...
        score is positive weighted for everything in the overlap,

        negatively weighted for everything not in overlap
        '''
        if current is None:
            return inf

        ops_path = current.get_root().ops_path
        return heuristic(ops_path, goal)

    def distance_between(self, n1, n2):
        #return 1 + 5 * n2.rule.word_cost
        return 1

    def path_neighbors(self, search_node):
        if not search_node.data:
            return self.neighbors(None)

        search_node.data = TreeSearchNode.copy_tree(search_node.data)
        current = search_node.data


        '''path_len, dids = self._print_path(search_node)
        print('')
        print('current tree')
        print(current)
        root = current.get_root_and_correct_parents()
        print('\ncurrent root')
        print(root)
        print(root.ops_path, self._goal)
        print('fscore', search_node.fscore, self.heuristic_cost_estimate(root, self._goal)

        current.get_root_and_correct_parents().assert_correct()#.assert_correct(dids)
        assert(len(list(root.get_data())) == path_len)
        print("*" * 80)'''
        root = current.get_root()
        root.assert_correct()
        path_len, dids = self._print_path(search_node)
        print(root)
        print("*" * 80)
        #try:
        assert(len(list(root.get_data())) == path_len)
        #except Exception as e:
        #    print(root)
        #    _ = input('')
        neighbors = self.neighbors(current)

        return neighbors

    def neighbors(self, current):
        if current is None:
            #for r in RuleNode.rules.values():
            #    yield TreeSearchNode(r)
            return [TreeSearchNode(r) for r in RuleNode.rules.values()]
        #yield from current.get_neighbors()
        return list(current.get_neighbors())

    #def path_is_goal_reached(self, current, goal):
    #    pass
    def is_goal_reached(self, current, goal):
        if current is None:
            return False
        root = current.get_root_and_correct_parents()
        return root.is_complete and root.rule == RuleNode.root


def find_bf(bf):
    path = TreeFinder().astar(None, bf)
    print('path')
    path = list(path)
    root = path[-1].get_root_and_correct_parents()
    print(root)
    print(root.ops_path, bf)
    print(TreeFinder().heuristic_cost_estimate(root, bf))

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
    find_bf(">>>>>>>>")
    print(time.time()-stime)
