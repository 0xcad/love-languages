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

        # there is a current node otherwise
        TreeNode._set_parent_ptrs(self)
        TreeNode._set_child_ptrs(self)
        if self.is_complete and self.parent:
            self.parent.update_is_complete()

        target_node = self
        while target_node.is_complete and target_node.parent:
            target_node = target_node.parent

        # either have an incomplete node, or a node with no parent

        # add parents to a complete tree
        # do not set target_node parent pointer
        if target_node.is_complete:
            rule = target_node.rule
            for l_parent in RuleNode.nodes_by_left.get(rule.rule, set()):
                parent = TreeSearchNode(l_parent, left=target_node)
                yield parent

            for r_parent in RuleNode.nodes_by_right.get(rule.rule, set()):
                parent = TreeSearchNode(r_parent, right=target_node)
                yield parent

            for t_parent in RuleNode.nodes_by_third.get(rule.rule, set()):
                parent = TreeSearchNode(t_parent, third=target_node)
                yield parent
            assert(target_node.parent is None)
            return

        # yield potential children from highest incomplete node
        # do not set target_node left/right/third pointers
        target_node, target_rule = highest_incomplete(target_node)
        for rule in RuleNode.nodes[target_rule]:

            #parent = TreeSearchNode.copy_tree(target_node) # TODO
            child = TreeSearchNode(rule, parent=target_node)
            if target_node.left is None:
                child.is_left_child = True
            else:
                if target_node.right is None:
                    child.is_right_child = True
                else:
                    child.is_third_child = True
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
        import time
        return hash(time.time()) # TODO this is so stupid lol
        return hash((hash(self.left), hash(self.data), hash(self.right)))



class TreeFinder(AStar):
    #def path_heuristic_cost_estimate(self, current, goal):
    #    pass

    def heuristic_cost_estimate(self, current, goal):
        '''
        huge TODO of course, this is just stupid shit...
        score is positive weighted for everything in the overlap,

        negatively weighted for everything not in overlap
        '''
        if current:
            #print(current.get_root())
            print(current.get_root().ops_path, ' ' * 20, end='\r')
            #_ = input('')

        if current is None:
            return inf

        ops_path = current.get_root().ops_path
        overlap = lcs(ops_path, goal)
        pweights = {
            "[": 10,
            "]": 10,
            "+": 3,
            "-": 3,
        }
        nweights = {
            "[": inf,
            "]": inf,
            "+": 1,
            "-": 1,
        }
        score = 0
        for i in range(len(ops_path)):
            c = ops_path[i]
            if overlap and i == overlap[0]:
                score -= pweights.get(c, 1)
                overlap.popleft()
            else:
                score += nweights.get(c, 0)

        print(current.get_root_and_correct_parents())
        print(ops_path)
        print(score)
        _ = input('')
        return score


    def distance_between(self, n1, n2):
        return 1 + 5 * n2.rule.word_cost

    #def path_neighbors(self, search_node):
    #    pass
    def neighbors(self, current):
        if current is None:
            for r in RuleNode.rules.values():
                yield TreeSearchNode(r)
            return
            #return [TreeSearchNode(r) for r in RuleNode.rules.values()]
        yield from current.get_neighbors()

    #def path_is_goal_reached(self, current, goal):
    #    pass
    def is_goal_reached(self, current, goal):
        if current is None:
            return False
        return current.get_root().is_complete


def find_bf(bf):
    path = TreeFinder().astar(None, bf)

def choice_search():
    curr = None
    path = []
    neighbors = [TreeSearchNode(r) for r in RuleNode.rules.values()]

    while neighbors:
        print('-' * 80)
        # present choices
        s = [
                f'{i + 1}. {n.rule.rule_str} {n.ops_path}'
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
        print('Current tree')
        print(curr)
        print('-' * 10)
        print('Current root')
        print(root)
        print('Current path')
        print(root.ops_path)


if __name__ == '__main__':
    #choice_search()
    find_bf(">>>>>>>>>")
