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
        self._is_complete = bool(
                (self.left is False or self.left and self.left.is_complete) and
                (self.right is False or self.right and self.right.is_complete) and
                (self.third is False or self.third and self.third.is_complete)
        )
        #TreeNode._set_parent_ptrs(self)
        if self.is_complete and self.parent and not self.parent.is_complete:
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

    def d_id(self, arg=None):
        arg = self if arg is None else arg
        return id(arg)

    def node_str(self):
        s = f'{repr(self.data)} {str(self.d_id())[-5:]} -> parent {repr(self.parent.data) if self.parent else "root"} {str(self.d_id(self.parent))[-5:]} ({"" if self.is_complete else "in"}complete)'
        if self.data and type(self.data) != RuleNode:
            s += ' ' + ''.join(self.data.ops_path)
        return s# + ''.join(self.data.ops_path)

    def __str__(self):
        def helper(node, depth=1):
            if node is None:
                return "incomplete"
            elif node is False:
                return "leaf"
            s = [node.node_str()]
            #s[0] += f' {node.is_left_child} {node.is_right_child} {node.is_third_child}'
            bullet = '*' if depth % 2 else '>'
            s.append(f'{" " * depth * 2}{bullet} {helper(node.left, depth +1)}')
            s.append(f'{" " * depth * 2}{bullet} {helper(node.right, depth +1)}')
            if node.third is not False:
                s.append(f'{" " * depth * 2}{bullet} {helper(node.third, depth +1)}')
            return '\n'.join(s)
        return helper(self)

    def __repr__(self):
        return f"{'' if self.is_complete else 'in' }complete {self.data} tree"


    def assert_correct(self):
        '''
        Makes sure that the tree is correct
        '''
        get_rule = lambda node: node if not node else node.data.rule
        def helper(node):
            if not node:
                return True

            # is left/right/third child is correct
            assert(bool(node.is_left_child) + bool(node.is_right_child) + bool(node.is_third_child) <= 1)
            if node.is_left_child:
                assert(node.parent and node.parent.left == node)
            if node.is_right_child:
                assert(node.parent and node.parent.right == node)
            if node.is_third_child:
                assert(node.parent and node.parent.third == node)

            # the rules are correct
            assert((not node.left or get_rule(node.left) == node.data.l) and (not node.right or get_rule(node.right) == node.data.r))
            assert(not node.third or get_rule(node.third) == node.data.third)

            # node completeness correct
            if not node.is_complete:
                assert((node.left and not node.left.is_complete) or
                       (node.right and not  node.right.is_complete) or
                       (node.third and not node.third.is_complete) or
                       node.left is None or node.right is None or node.third is None)
            else:
                assert (not((node.left and not node.left.is_complete) or
                       (node.right and not  node.right.is_complete) or
                       (node.third and not node.third.is_complete) or
                       node.left is None or node.right is None or node.third is None))
            if node.parent and not node.is_complete:
                assert(not node.parent.is_complete)

            # the bf is correct
            if node.is_complete:
                bf = []
                for r in node.get_data():
                    bf = combine_bf(bf, r.ops)
                condensed = combine_bf(*[list(r.ops) for r in node.get_data()])
                assert(bf == node.ops_path == condensed)

            helper(node.left)
            helper(node.right)
            helper(node.third)

        try:
            root = self.get_root_and_correct_parents()
            helper(root)
            return root
        except Exception as e:
            print('ERROR')
            print(self.get_root_and_correct_parents())
            raise Exception(e)

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
        if node is False:
            parent.right = False
            return
        if node is None:
            parent.right = None
            return

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
        if node is False:
            parent.left = False
            return
        if node is None:
            parent.left = None
            return

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
        new = cls(node.data)
        new.is_left_child = node.is_left_child
        new.is_right_child = node.is_right_child
        new.is_third_child = node.is_third_child
        new.parent = node.parent
        #new._is_complete = node._is_complete
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
            else:
                new_parent.right = curr
            if not curr.is_left_child:
                new_sibling = cls.copy_subtree(parent.left)
                new_parent.left = new_sibling
                if new_sibling: new_sibling.parent = new_parent
            else:
                new_parent.left = curr
            if not curr.is_third_child:
                new_sibling = cls.copy_subtree(parent.third)
                new_parent.third = new_sibling
                if new_sibling: new_sibling.parent = new_parent
            else:
                new_parent.third = curr

            curr.parent = new_parent
            curr = new_parent
            parent = new_parent.parent
        return new

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
    def _set_child_ptrs(cls, node):
        # ensure a node's children
        if node.left:
            node.left.parent = node
            node.left.is_left_child = True
        if node.right:
            node.right.parent = node
            node.right.is_right_child = True
        if node.third:
            node.third.parent = node
            node.third.is_third_child = True

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

    def get_nodes(self):
        '''
        in order generator for node nodes in list
        '''
        def helper(node):
            if not node:
                return None
            yield from helper(node.left)
            yield node
            yield from helper(node.right)
            yield from helper(node.third)
        return helper(self)

    def get_data(self):
        '''
        in order generator for node data in list
        '''
        for node in self.get_nodes():
            if node.data:
                yield node.data

    def get_cost(self):
        '''
        Returns the word cost of all trees
        '''
        if self._cost is not None:
            return self._cost
        self._cost = sum(map(lambda data: data.get_cost(), self.get_data()))
        return self._cost

    def get_leafs(self):
        '''
        Prints the word leafs of the tree
        '''
        return [d.get_leaf() for d in self.get_data() if d.word_cost >= 1]


    @classmethod
    def str_to_tree(cls, s):
        def get_depth(line):
            return len(line.split("* ")[0]) // 2
        lines = s.strip().splitlines()
        root = None
        stack = []
        for i, line in enumerate(lines):
            ws, r = line.split("* ")
            depth = len(ws) // 2
            node = None
            if r == "Leaf":
                node = False
            elif r != "None":
                node = cls(RuleNode.rules[r])
            is_left = i > 0 and get_depth(lines[i-1]) == depth-1

            if not stack:
                root = node
                stack.append((depth, node))
            else:
                # find parent node
                while stack and stack[-1][0] >= depth:
                    stack.pop()
                if stack:
                    parent_node = stack[-1][1]
                    if is_left:
                        cls.insert_left(parent_node, node)
                    else:
                        cls.insert_right(parent_node, node)
                stack.append((depth, node))
        return root

    def __eq__(self, other):
        def children_equal(t1, t2):
            return ((t1 is None and t2 is None) or
                    (t1 is False and t2 is False) or
                    t1 and t2 and t1.__eq__(t2))
        return (type(self) == type(other) and
                self.data == other.data and
                children_equal(self.left, other.left) and
                children_equal(self.right, other.right) and
                children_equal(self.third, other.third))

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if not self.is_complete:
            raise Exception('hashing incomplete tree...')
        return hash((hash(self.left), hash(self.data), hash(self.right), hash(self.third)))


class MemoTree:
    '''
    Constructs all memoized trees
    '''
    _default_fname = 'trees.pkl'
    table = {}
    # ^dictionary linking phrases (keys) to trees (sets)

    def __init__(self, cls=TreeNode):
        self.cls = cls

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

    def initialize(self):
        pass


if __name__ == '__main__':
    M = MemoTree()
    M.load_from_file()
    count = 0
    for key, trees in M.table.items():
        for tree in trees:
            tree.assert_correct()
            print(tree)
            print(tree.ops_path)
            print('')
            count += 1
    print(count)
