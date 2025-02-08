from rules import RuleNode
import pickle
import os
import itertools

from common import combine_bf

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
        self._ops_path = None
        self._cost = None

    @property
    def is_complete(self):
        if self._is_complete is not None:
            return self._is_complete
        self._is_complete = (
                (self.left is False or self.left and self.left.is_complete) and
                (self.right is False or self.right and self.right.is_complete) and
                (self.third is False or self.third and self.third.is_complete)
        )
        if self._is_complete and self.parent:
            self.parent.update_is_complete()
        return self._is_complete

    def update_is_complete(self):
        '''
        this node is now complete, so recalculate is_complete for the parent node
        '''
        self._is_complete = None
        self.is_complete

    @property
    def height(self):
        # TODO ?
        pass

    def __str__(self):
        def helper(node, depth=1):
            if node is None:
                return "incomplete"
            elif node is False:
                return "leaf"
            s = [f'{repr(node.data)} {str(id(node))[-5:]} -> parent {repr(node.parent.data) if node.parent else "root"} {str(id(node.parent))[-5:]} ({"" if node.is_complete else "in"}complete)']
            bullet = '*' if depth % 2 else '>'
            s.append(f'{" " * depth * 2}{bullet} {helper(node.left, depth +1)}')
            s.append(f'{" " * depth * 2}{bullet} {helper(node.right, depth +1)}')
            if node.third is not False:
                s.append(f'{" " * depth * 2}{bullet} {helper(node.third, depth +1)}')
            return '\n'.join(s)
        return helper(self)

    def __repr__(self):
        return f"{'' if self.is_complete else 'in' }complete {self.data} tree"

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
            TreeNode._set_parent_ptrs(c)
            c = c.parent
        return c

    @classmethod
    def insert_right(cls, parent, node):
        node.parent = parent
        if parent.right is False and parent.third is not False:
            # insert into third if right is a leaf...
            parent.third = node
            node.is_third_child = True
        elif parent.right is False and parent.third is False:
            raise Exception('inserting right subtree into leaf')
        else:
            parent.right = node
            node.is_right_child = True
        return node

    @classmethod
    def insert_left(cls, parent, node):
        if parent.left is False:
            print(parent.data, node.data)
            raise Exception('error; inserting left subtree into leaf')
        node.parent = parent
        parent.left = node
        node.is_left_child = True
        return node

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
        TreeNode._set_parent_ptrs(node) # left/right child status

        curr.is_left_child = True
        curr.is_right_child = None
        node.left = curr # insert curr as left child of node
        return node

    @classmethod
    def _set_parent_ptrs(cls, node):
        # ensure a node's parent pointers are correct
        if node.is_left_child:
            node.parent.left = node
        elif node.is_right_child:
            node.parent.right = node
        elif node.is_third_child:
            node.parent.third = node


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
    def memoize_tree(cls, memo, node):
        '''
        Starting at the node `node`, go up its ancestors while each one is complete
        memoize the subtree rooted at that node
        '''
        c = node
        while c and c.is_complete:
            if type(c.data) == RuleNode:
                key = c.data.rule
                c.ops_path
                memo[key] = memo.get(key, set()).union(set([c]))
            TreeNode._set_parent_ptrs(c)
            c = c.parent

        return memo

    @property
    def ops_path(self) -> list:
        '''
        Returns an array for the ops of the tree
        '''
        if self._ops_path is not None:
            return self._ops_path

        assert(type(self.data) == RuleNode)
        def helper(node):
            if not node:
                return []
            left = helper(node.left)
            right = helper(node.right)
            third = helper(node.third)

            return combine_bf(left, node.data.ops, right, third)
        self._ops_path = helper(self)
        return self._ops_path

    def get_data(self):
        '''
        in order generator for node data in list
        '''
        def helper(node):
            if not node:
                return None
            yield from helper(node.left)
            yield node.data
            yield from helper(node.right)
            yield from helper(node.third)
        return helper(self)

    def get_cost(self):
        '''
        Returns the word cost of all trees
        '''
        if self._cost is not None:
            return self._cost
        self._cost = sum(map(lambda data: data.get_cost(), self.get_data()))
        return self._cost

    def __eq__(self, other):
        def children_equal(t1, t2):
            return ((t1 is None and t2 is None) or
                    (t1 is False and t2 is False) or
                    t1 and t2 and t1.__eq__(t2))
        return (self.data == other.data and
                children_equal(self.left, other.left) and
                children_equal(self.right, other.right) and
                children_equal(self.third, other.third))

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if not self.is_complete:
            raise Exception('hashing incomplete tree...')
        return hash((hash(self.left), hash(self.data), hash(self.right)))


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
                    root = TreeNode(rule)
                    for child in TreeNode.construct_down_from_tree(root, max_height-1):
                        child_list.append(child)
        create_children(r_trees, node.right, node.data.r)
        create_children(l_trees, node.left, node.data.l)
        create_children(r_trees, node.third, node.data.third)
        l_trees = l_trees if l_trees else [None]
        r_trees = r_trees if r_trees else [None]

        # create all products of left/right trees
        for left, right in itertools.product(l_trees, r_trees):
            node = TreeNode._copy_node(node)
            if left:
                TreeNode.insert_left(node, left)
            if right:
                TreeNode.insert_right(node, right)
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
            for tree in TreeNode.construct_down_from_tree(node, max_height):
                yield tree
            return None
        '''
        The tree is complete
        Add a parent to it, and then recurse on that
        '''
        yield node

        for l_parent in RuleNode.nodes_by_left.get(rule.rule, set()):
            node = TreeNode.copy_subtree(node)
            parent = TreeNode(l_parent)
            TreeNode.insert_left(parent, node)
            yield from TreeNode.construct_from_tree(parent, max_height - 1)

        for r_parent in RuleNode.nodes_by_right.get(rule.rule, set()):
            node = TreeNode.copy_subtree(node)
            parent = TreeNode(r_parent)
            TreeNode.insert_right(parent, node)
            yield from TreeNode.construct_from_tree(parent, max_height - 1)

        for t_parent in RuleNode.nodes_by_third.get(rule.rule, set()):
            node = TreeNode.copy_subtree(node)
            parent = TreeNode(t_parent)
            TreeNode.insert_right(parent, node)
            yield from TreeNode.construct_from_tree(parent, max_height - 1)


class MemoTree:
    '''
    Constructs all memoized trees
    '''
    table = {}
    # ^dictionary linking phrases (keys) to trees (sets)
    _default_fname = 'trees.pkl'

    def __init__(self):
        pass

    def save_to_file(self, fname=None):
        fname = fname if fname else self._default_fname
        with open(fname, "wb") as file:
            pickle.dump(self.table, file)

    def load_from_file(self, fname=None):
        fname = fname if fname else self._default_fname
        if not os.path.exists(fname):
            self.initialize()
            self.save_to_file(fname)
        with open(fname, "rb") as file:
            self.table = pickle.load(file)

    # 25 trees of height 6
    # crazy number of trees of length 7 and 8; or an infinite loop
    def initialize(self, max_height=6, fname=None):
        '''
        Construct and memoize all complete trees of height n
        '''
        RuleNode.load_from_file()
        for rule in RuleNode.rules.values():
            if rule.is_r_leaf and rule.is_l_leaf:
                rule_tree = TreeNode(rule)
                for tree in TreeNode.construct_from_tree(rule_tree, max_height):
                    if tree:
                        TreeNode.memoize_tree(self.table, tree)
        return self.table

if __name__ == '__main__':
    M = MemoTree()
    M.load_from_file()
    count = 0
    for key, trees in M.table.items():
        for tree in trees:
            print(tree)
            print(tree.ops_path)
            print('')
            count += 1
    print(count)
