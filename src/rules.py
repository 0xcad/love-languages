import os
import pickle

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

    {'rule': "DTVDP: DP DP", 'ops': ""},
    {'rule': "V': DTV DTVDP", 'ops': ">"},

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

is_leaf = lambda X: X is None or not (X.endswith("'") or (len(X) > 1 and X.endswith("P")))
class RuleNode:
    '''
    A class wrapper for rule dictionaries
    A recursive, binary tree representing all given X-bar
    rules/ key: rule strings / values: RuleNode objects
    nodes/ key: string X     / values: a set containing all RuleNodes X: W Y
    '''
    rules = {}
    nodes = {}
    nodes_by_left = {} # key is W / values: a set containing all RuleNodes X: W Y
    nodes_by_right = {}# key is Y / values: a set containing all RuleNodes X: W Y
    nodes_by_third = {}# key is Z / values: a set containing all RuleNodes X: W Y Z
    root = None
    _default_fname = 'rules.pkl'

    def __new__(cls, value={}):
        key = value.get('rule')
        if key in cls.rules:
            return cls.rules[key]
        instance = super().__new__(cls)
        if key:
            cls.rules[key] = instance
        return instance

    @classmethod
    def construct_from_rules(cls, rule_array=[]):
        for rule_dict in rule_array:
            node = RuleNode(rule_dict)
        for node in cls.rules.values():
            cls.nodes[node.rule] = cls.nodes.get(node.rule, set()).union(set([node]))
            if node.is_root:
                cls.root = node

            if not node.is_l_leaf:
                cls.nodes_by_left[node.l] = cls.nodes_by_left.get(node.l, set()).union(set([node]))
            if not node.is_r_leaf:
                cls.nodes_by_right[node.r] = cls.nodes_by_right.get(node.r, set()).union(set([node]))
            if node.third:
                cls.nodes_by_third[node.third] = cls.nodes_by_third.get(node.third, set()).union(set([node]))

    @classmethod
    def load_from_file(cls, fname=None):
        fname = fname if fname else cls._default_fname
        if not os.path.exists(fname):
            RuleNode.construct_from_rules(rules)
            with open(fname, "wb") as file:
                pickle.dump(RuleNode.rules, file)
        else:
            with open(fname, "rb") as file:
                RuleNode.rules = pickle.load(file)
            RuleNode.construct_from_rules()

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


        self.is_l_leaf = is_leaf(self.l)
        self.is_r_leaf = is_leaf(self.r)
        self.is_right_recursive = rule == self.r
        self.is_left_recursive = rule == self.l

        self.rule = rule
        #print(rule, ':', self.l, self.r, self.third, '\t', self.l_leaf, self.r_leaf)

    def get_cost(self):
        return self.word_cost

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

#RuleNode.load_from_file()
RuleNode.construct_from_rules(rules)
