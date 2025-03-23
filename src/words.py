import random
from trees import TreeNode

# THIS FUNCTION IS AI GENERATED
def remove_extra_parens(s):
    def tokenize(s):
        tokens = []
        token = ''
        for char in s:
            if char in '()':
                if token:
                    tokens.append(token.strip())
                    token = ''
                tokens.append(char)
            elif char.isspace():
                if token:
                    tokens.append(token.strip())
                    token = ''
            else:
                token += char
        if token:
            tokens.append(token.strip())
        return tokens

    def parse(tokens):
        def helper(index):
            res = []
            while index < len(tokens):
                token = tokens[index]
                if token == '(':
                    inner, index = helper(index + 1)
                    res.append(inner)
                elif token == ')':
                    break
                else:
                    res.append(token)
                index += 1
            return res, index
        tree, _ = helper(0)
        return tree

    def rebuild(node):
        if isinstance(node, str):
            return node
        rebuilt = [rebuild(child) for child in node]
        if len(rebuilt) == 1:
            return rebuilt[0]
        else:
            return f"({' '.join(rebuilt)})"

    tokens = tokenize(s)
    parsed_tree = parse(tokens)
    result = rebuild(parsed_tree)
    return result
# END AI GENERATED FUNCTION


def tree_to_leafs(tree):
    '''
    Turn a tree into a paren wrapped string of leafs, in order traversal
    '''
    def helper(node):
        if node is False:
            return
        d = node.data
        is_word = bool(d.word_cost)

        L = d.l if (d.is_l_leaf and is_word) else helper(node.left)
        R = d.r if (d.is_r_leaf and is_word) else helper(node.right)
        T = helper(node.third)
        node = [L, R, T]
        node = [n for n in node if n]
        return '(' + ' '.join(node) + ')'

    return remove_extra_parens(helper(tree))
    #^ don't include last parens

FIRST = 1
SECOND = 2
THIRD = 3

words = {
    'Pronoun': [
        {'word': 'I', 'accusative': 'ME', 'anaphoric': 'MYSELF', 'person': FIRST},
        {'word': 'YOU', 'accusative': 'YOU', 'anaphoric': 'YOURSELF', 'person': SECOND},
    ],
    'D': ['YOUR', 'MY'], #the, a
    'N': {
        'uncountable': ['ADORATION', 'AFFECTION', 'AMBITION', 'APPETITE', 'ARDOUR', 'DESIRE', 'DEVOTION', 'EAGERNESS', 'ENCHANTMENT', 'ENTHUSIASM', 'EYES', 'FELLOW FEELING', 'FERVOUR', 'FONDNESS', 'HUNGER', 'INFATUATION', 'LIKING', 'LONGING', 'LOVE', 'LUST', 'PASSION', 'RAPTURE', 'SYMPATHY', 'TENDERNESS', 'THIRST', 'YEARNING'],
        'count': ['CHARM', {'word': "FANCY", 'plural':'FANCIES'}, "HEART",{'word': "WISH", 'plural': 'WISHES'}],
    },
    'PETNAME': ['DARLING', 'DEAR', 'HONEY', 'JEWEL', 'DUCK', 'MOPPET', 'SWEETHEART'],
    'Adv': ['AFFECTIONATELY', 'ANXIOUSLY', 'ARDENTLY', 'AVIDLY', 'BEAUTIFULLY', 'BREATHLESSLY', 'BURNINGLY', 'COVETOUSLY', 'CURIOUSLY', 'DEVOTEDLY', 'EAGERLY', 'FERVENTLY', 'FONDLY', 'IMPATIENTLY', 'KEENLY', 'LOVINGLY', 'PASSIONATELY', 'SEDUCTIVELY', 'TENDERLY', 'WINNINGLY', 'WISTFULLY'],
    'AdjAdv': ['VERY', 'INCREDIBLY', 'INTENSELY', 'BEAUTIFULLY', 'LOVINGLY', 'TOTALLY', 'FERVENTLY'],
    'A': ['ADORABLE', 'AFFECTIONATE', 'AMOROUS', 'ANXIOUS', 'ARDENT', 'AVID', 'BREATHLESS', 'BURNING', 'COVETOUS', 'CRAVING', 'CURIOUS', 'DARLING', 'DEAR', 'DEVOTED', 'EAGER', 'EROTIC', 'FERVENT', 'FOND', 'IMPATIENT', 'KEEN', 'LITTLE', 'LOVEABLE', 'LOVESICK', 'LOVING', 'PASSIONATE', 'PRECIOUS', 'SWEET', 'SYMPATHETIC', 'TENDER', 'UNSATISFIED', 'WISTFUL'],
    'V': ['CARESS', 'DANCE', 'DREAM', 'FLIRT', 'FLUTTER', 'GAZE', 'HUNGER', 'LEAP', 'MELT', 'OBSESS', 'PINE', 'SIGH', 'SWOON', 'YEARN'],
    # idea: reflexive verbs? We embrace, entangle, kiss, touch
    'TV': ['ADORE', 'CARE FOR', 'CLING TO', 'CRAVE', 'DESIRE', 'HOLD', 'HOPE FOR', 'HUNGER FOR', 'LONG FOR', 'LIKE', 'LOVE', 'LUST AFTER', 'PANT FOR', 'PINE FOR', 'PRIZE', 'SIGH FOR', 'SOOTHE', 'TEMPT', 'THIRST FOR', 'TREASURE', 'WANT', 'WISH FOR', 'YEARN FOR'],
    'DTV': ['GIVE', 'OFFER', 'PROMISE', 'OFFER'], #DEDICATE?
    'P': ['BEYOND', 'WITH', 'IN', 'LIKE', 'ON'], # TO, ON, AT, BEYOND, AFTER, LIKE
    'Conj': ['AND'],
    'QUERY': ['BUT WHY?', 'FOR WHAT?', 'CAN IT BE?', "DO I DREAM?"],
    'EXC': ['OH!', 'PLEASE!', 'LORD ABOVE!'],
}

class WordBank:
    def __init__(self):
        global words
        self.words = words.copy()

        nouns = []
        for prop, words in self.words['N'].items():
            for word in words:
                if type(word) != dict:
                    word = {'word': word}
                word[prop] = True
                nouns.append(word)
        self.nouns = nouns

        verbs = {}
        for key in ['V', 'TV', 'DTV']:
            key_arr = []
            for word in self.words[key]:
                if type(word) != dict:
                    word = {'word': word}
                key_arr.append(word)
            verbs[key] = key_arr
        self.verbs = verbs

    def _select(self, word_list, replacement):
        word_i = random.randrange(len(word_list))
        word_d = word_list[word_i] if replacement else word_list.pop(word_i)
        return word_d

    def fill_word(self, leaf, tags, replacement=True):
        if leaf == 'N':
            return self.fill_noun(tags, replacement)
        elif leaf == 'Pronoun':
            return self.fill_pronoun(tags, replacement)
        elif leaf in ['V', 'TV', 'DTV']:
            return self.fill_verb(leaf, tags, replacement)

        return random.choice(self.words[leaf])

    def fill_noun(self, tags, replacement):
        word_d = self._select(self.nouns, replacement)

        word = word_d['word']
        # PLURALIZE NOUN
        if tags.get("pluralize") and word_d.get('count'):
            word = word_d.get('plural', word + 'S')
        return word

    def fill_pronoun(self, tags, replacement):
        word_d = self._select(self.words['Pronoun'], replacement)

        word = word_d['word']
        if tags.get('accusative'):
            if tags.get('person') == word_d['person']:
                word = word_d['anaphoric']
            else:
                word = word_d['accusative']
        return word

    def fill_verb(self, leaf, tags, replacement):
        verbs = self.verbs[leaf]

        # TODO: do I need to do any filtering here based on tags?
        word_d = self._select(verbs, replacement)


        word = word_d['word']
        # CONJUGATE VERB
        print('hey', tags, word)
        if tags.get('person') == THIRD and not tags.get('pluralize'):
            parts = word.split(' FOR')
            if len(parts) >= 1:
                word = parts[0]

            if word.endswith('S'):
                word += 'ES'
            else:
                word += 'S'

            word = (word + ' ' + ' '.join(parts[1:])).strip()
        return word



def tree_to_words(tree):
    '''
    Turn a tree into words
    '''
    if tree.data.rule_str == 'SP: SP SP':
        return tree_to_words(tree.left) + '. ' + tree_to_words(tree.right)
    leafs = tree.get_leafs()
    #print(leafs)
    #print(tree)
    sentence = []
    for l in leafs:
        try:
            sentence.append(random.choice(words[l]))
        except:
            raise Exception(l)
    return ' '.join(sentence)


class TreeWordNode(TreeNode):
    WB = WordBank()

    def __init__(
        self, data, left=None, right=None, parent=None, third=None, word=None
        ):
         super().__init__(data, left, right, parent, third)
         self.rule = self.data
         self.tags = {}
         self.word = word

    def node_str(self):
        s = f'{self.rule} {str(self.tags)}'
        if self.word:
            s += ' ' + str(self.word)
        return s

    @classmethod
    def cast_tree(cls, tree):
        if not tree:
            return tree


        root = cls(tree.data)
        left = cls.cast_tree(tree.left)
        right = cls.cast_tree(tree.right)
        third = cls.cast_tree(tree.third)

        cls.insert_left(root, left)
        cls.insert_right(root, right)
        root.third = third
        if third:
            third.parent = root
            root.is_third_child = True

        return root

    def add_tag(self, tag, value=True, replace=True):
        if tag in self.tags and not replace:
            return
        self.tags[tag] = value

    def add_tag_ancestors(self, tag, value=True, replace=True):
        '''
        add tag to all ancestors, going up until ancestor has that tag
        '''
        # TODO: caching
        self.add_tag(tag, value, replace)
        if self.parent:
            self.parent.add_tag_ancestors(tag, value, replace=False)

    def get_tags_ancestors(self):
        '''
        get tags for ancestors, such that closer nodes' values override further
        ones away
        '''
        #TODO: caching
        if not self.parent:
            return self.tags
        p_tags = self.parent.get_tags_ancestors()
        return {**p_tags, **self.tags}

    def fill_words(self):
        '''
        Recursively go down tree and fill in words according to constraints
        '''

        '''
        NODE RULES
        '''
        #DP RULES
        if self.rule in ["D': NP", "D': D NP"]:
            self.add_tag_ancestors('person', THIRD)
            if self.rule == "D': NP":
                self.add_tag_ancestors('pluralize')
        elif (self.rule.rule == "DP" and self.parent and
              self.parent.rule in ['DTVDP: DP DP', "V': TV DP"]):
            self.add_tag('accusative')

        '''
        LEAF
        '''
        if self.rule.word_cost > 0:
            d = self.rule
            leaf = self.rule.get_leaf()

            tags = self.get_tags_ancestors()
            word = self.WB.fill_word(leaf, tags)
            '''
            TODO: word should probably be its own class
            and on equality, if compared to a string it should lower the string
            and check if the word strings are equal
            '''

            if leaf == 'Pronoun':
                if word == 'I':
                    self.add_tag_ancestors('person', FIRST)
                elif word == 'YOU':
                    self.add_tag_ancestors('person', SECOND)

            self.word = word #TODO

        '''
        RECURSE
        '''
        if self.third:
            # do this first bc we care about last value for rules
            self.third.fill_words()
        if self.left:
            self.left.fill_words()
        if self.right:
            self.right.fill_words()

def tree_to_words(tree):
    '''
    Turn a tree into words
    '''
    '''stack = []
    curr = tree
    while curr or len(stack) > 0:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()

        print('hey!', curr.data)
        curr = curr.right'''

    '''stack = [tree]
    curr = None
    while len(stack) > 0:
        curr = stack.pop()

        print('hey', curr.data)
        if curr.right:
            stack.append(curr.right)
        if curr.left:
            stack.append(curr.left)'''

    tree = TreeWordNode.cast_tree(tree)

    rule = tree.data
    if rule != "SP: DP VP":
        return

    tree.left.fill_words()
    tree.right.fill_words()
    print(tree)
    return ' '.join([n.word for n in tree.get_nodes() if n.word])


