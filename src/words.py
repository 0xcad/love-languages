import random
from trees import TreeNode
from copy import deepcopy

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
    'D': [
        {'word': 'MY', 'possession': FIRST},
        {'word': "YOUR", 'possession': SECOND}
    ], #the, a
    'N': {
        'uncountable': ['ADORATION', 'AFFECTION', 'AMBITION', 'APPETITE', 'ARDOUR', 'DESIRE', 'DEVOTION', 'EAGERNESS', 'ENCHANTMENT', 'ENTHUSIASM', {'word': 'EYES', 'pluralize': True}, 'FERVOUR', 'FONDNESS', 'HUNGER', 'INFATUATION', 'LIKING', 'LONGING', 'LOVE', 'LUST', 'PASSION', 'RAPTURE', 'SYMPATHY', 'TENDERNESS', 'THIRST', 'YEARNING'],
        'count': ['BODY', 'CHARM', 'FANCY', 'FELLOW FEELING', "HEART", {'word': "WISH", 'plural': 'WISHES'}],
    },
    'PETNAME': ['DARLING', 'DEAR', 'HONEY', 'JEWEL', 'DUCK', 'MOPPET', 'SWEETHEART'],
    'Adv': ['AFFECTIONATELY', 'ANXIOUSLY', 'ARDENTLY', 'AVIDLY', 'BEAUTIFULLY', 'BREATHLESSLY', 'BURNINGLY', 'COVETOUSLY', 'CURIOUSLY', 'DEVOTEDLY', 'EAGERLY', 'FERVENTLY', 'FONDLY', 'IMPATIENTLY', 'KEENLY', 'LOVINGLY', 'PASSIONATELY', 'SEDUCTIVELY', 'TENDERLY', 'WINNINGLY', 'WISTFULLY'],
    'APAdv': ['VERY', 'INCREDIBLY', 'INTENSELY', 'BEAUTIFULLY', 'LOVINGLY', 'TOTALLY', 'FERVENTLY'],
    'A': ['ADORABLE', 'AFFECTIONATE', 'AMOROUS', 'ANXIOUS', 'ARDENT', 'AVID', 'BREATHLESS', 'BURNING', 'COVETOUS', 'CRAVING', 'CURIOUS', 'DARLING', 'DEAR', 'DEVOTED', 'EAGER', 'EROTIC', 'FERVENT', 'FOND', 'IMPATIENT', 'KEEN', 'LITTLE', 'LOVEABLE', 'LOVESICK', 'LOVING', 'PASSIONATE', 'PRECIOUS', 'SWEET', 'SYMPATHETIC', 'TENDER', 'UNSATISFIED', 'WISTFUL'],
    'V': ['CARESS', 'DANCE', 'DREAM', 'FLIRT', 'FLUTTER', 'GAZE', 'HUNGER', 'LEAP', 'MELT', 'OBSESS', 'PINE', 'SIGH', 'SWOON', 'YEARN'],
    # idea: reflexive verbs? We embrace, entangle, kiss, touch
    'TV': ['ADORE', 'CARE FOR', 'CLING TO', 'CRAVE', 'DESIRE', 'HOLD', 'HOPE FOR', 'HUNGER FOR', 'LONG FOR', 'LIKE', 'LOVE', 'LUST AFTER', 'PANT FOR', 'PINE FOR', 'PRIZE', 'SIGH FOR', 'SOOTHE', 'TEMPT', 'THIRST FOR', 'TREASURE', 'WANT', {'word': 'WISH FOR', THIRD: 'WISHES FOR'}, 'YEARN FOR'],
    'DTV': ['GIVE', 'OFFER', 'PROMISE', 'OFFER'], #DEDICATE?
    'P': ['BEYOND', 'WITH', 'IN', 'LIKE', 'ON'], # TO, ON, AT, BEYOND, AFTER, LIKE
    'Conj': ['AND'],
    'QUERY': ['BUT WHY?', 'FOR WHAT?', 'CAN IT BE?', "DO I DREAM?"],
    'EXC': ['OH!', 'PLEASE!', 'LORD ABOVE!'],
}

class Word(dict):
    def __init__(self, w, *args, **kwargs):
        if isinstance(w, dict):
            kwargs = {**kwargs, **w}

        super().__init__(*[], **kwargs)
        if self.get('word'):
            self.root = self['word']
        else:
            self.root = w
        self.word = w

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return self.word

    def __bool__(self):
        return bool(self.word) or super().__bool__()

    def __eq__(self, other):
        if isinstance(other, Word):
            return self.__dict__ == other.__dict__
        elif isinstance(other, str):
            return self.root.upper() == other.upper()
        return False

class WordBank:
    _words = words # original, never changes

    def init_nouns(self):
        nouns = []
        for prop, noun_words in self._words['N'].items():
            for word in noun_words:
                if type(word) != dict:
                    word = {'word': word}
                word[prop] = True
                nouns.append(word)
        self._words['N'] = nouns

    def init_verbs(self):
        for key in ['V', 'TV', 'DTV']:
            key_arr = []
            for word in self._words[key]:
                if type(word) != dict:
                    word = {'word': word}
                key_arr.append(word)
            self._words[key] = key_arr

    def refresh(self, depth = 0):
        '''
        Clears replacement map entries and sets words to original values

        Only refresh if we're at the original depth we were at when we
        made the changes. So we call refresh every time but the changes
        are in the scope of all nodes with greater depth
        '''
        if depth == 0:
            self.replacement_map = {}
            self.words = self._words.copy()
        for leaf, (value, d) in list(self.replacement_map.items()):
            if d == depth:
                del self.replacement_map[leaf]
                self.words[leaf] = self._words[leaf]

    def __init__(self):
        self.init_nouns()
        self.init_verbs()

        self.refresh()

    def add_replacement_map(self, leaf, value=None, depth=0):
        '''
        Whenever we fill a word in the `leaf` category, do not replace
        those entries (i.e, destructively modify the words)

        Do this at a certain depth to set scope of these changes for all
        nodes with greater depth (children)
        '''
        if self.replacement_map.get(leaf, [False])[0] == value:
            return # do nothing
        self.replacement_map[leaf] = (value, depth)
        self.words[leaf] = deepcopy(self._words[leaf])

        # map leaf -> value as well
        if value is not None:
            self.words[leaf] = deepcopy(self.words[value])


    def _select(self, leaf, word_list=None):
        if word_list is None:
            word_list = self.words[leaf]
        replacement = leaf not in self.replacement_map

        if len(word_list) == 0:
            self.words[leaf] = deepcopy(self._words[leaf])
            word_list = self.words[leaf]

        word_i = random.randrange(len(word_list))
        word_d = word_list[word_i] if replacement else word_list.pop(word_i)

        return word_d

    def fill_word(self, leaf, tags, node):
        if leaf == 'N':
            return self.fill_noun(tags, node)
        elif leaf == 'Pronoun':
            return self.fill_pronoun(tags, node)
        elif leaf in ['V', 'TV', 'DTV']:
            return self.fill_verb(leaf, tags, node)
        elif leaf == "D":
            return self.fill_determiner(tags, node)

        word_d = self._select(leaf)
        return Word(word_d)

    def fill_noun(self, tags, node):
        word_d = self._select('N')
        if tags.get('pet_name'):
            word_d = {'word': self._select("PETNAME")}

        word = word_d['word']
        # PLURALIZE NOUN
        if tags.get("pluralize") and word_d.get('count'):
            if word_d.get('plural'):
                word = word_d['plural']
            else:
                if word.endswith('Y'):
                    word = word[:-1] + "IES"
                else:
                    word += "S"
        # if we pick a plural noun (like "EYES") pluralize verb
        if word_d.get('pluralize'):
            node.add_tag_ancestors('pluralize')

        # subject shouldn't be counted as plural if it's a mass noun
        elif (tags.get('subject') and word_d.get('uncountable') and
            tags.get('pluralize') and "N': N' PP" not in node.get_scope()):
            node.add_tag_ancestors('pluralize', None, True)

        return Word(word, *word_d)

    def fill_pronoun(self, tags, node):
        # Alternate between I and YOU
        pronouns = self.words['Pronoun'].copy()
        prev = tags.get('possession', tags.get('person', None))
        if prev is None:
            # start with first person with 80% probability
            prev = SECOND if random.random() <= 0.8 else FIRST
        if tags.get("pet_name"):
            prev = FIRST if random.random() <= 0.8 else SECOND
        pronouns = [d for d in pronouns if d['person'] != prev]

        word_d = self._select('Pronoun', pronouns)

        # Pronoun agreement
        word = word_d['word']
        if tags.get('accusative'):
            if tags.get('person') == word_d['person']:
                word = word_d['anaphoric']
            else:
                word = word_d['accusative']

        if word_d.get('person'):
            node.add_tag_ancestors('person', word_d['person'])

        return Word(word, *word_d)

    def fill_determiner(self, tags, node):
        determiners = self.words['D']
        # Alternate between YOUR and MY
        if 'subject' not in tags:
            prev = tags.get('possession', tags.get('person', random.choice([FIRST, SECOND])))
            determiners = [d for d in determiners.copy() if d['possession'] != prev]

        word_d = self._select('D', determiners)
        node.add_tag_ancestors('possession', word_d['possession'])
        return Word(word_d['word'], **word_d)

    def fill_verb(self, leaf, tags, node):
        # TODO: do I need to do any filtering here based on tags?
        word_d = self._select(leaf)
        if tags.get('pet_name'):
            word_d = {'word': 'AM', FIRST: 'AM', SECOND: "ARE"}


        word = word_d['word']
        # CONJUGATE VERB
        if tags.get('person') == THIRD and not tags.get('pluralize'):
            if word_d.get(THIRD):
                word = word_d.get(THIRD)
            else:
                parts = word.split(' ')
                if len(parts) >= 1:
                    word = parts[0]
                if word.endswith('S'):
                    word += 'ES'
                else:
                    word += 'S'

                word = (word + ' ' + ' '.join(parts[1:])).strip()

        else:
            word = word_d.get(tags.get('person', 'word'), word)
        return Word(word, *word_d)



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
        self, data, left=None, right=None, parent=None, third=None, word=None, tags={}
        ):
         super().__init__(data, left, right, parent, third)
         self.rule = self.data
         self.tags = tags
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

        root = cls(tree.data, tags=getattr(tree, 'tags', {}))
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

    def get_scope(self):
        curr = self
        scope = [curr]
        while curr.parent:
            curr = curr.parent
            scope.append(curr)
        return scope

    def add_tag(self, tag, value=True, replace=True):
        if tag in self.tags and not replace:
            return
        self.tags[tag] = value

    def add_tag_ancestors(self, tag, value=True, replace=False):
        '''
        add tag to all ancestors, going up until ancestor has that tag
        '''
        # TODO: caching
        self.add_tag(tag, value, replace)
        if self.parent:
            self.parent.add_tag_ancestors(tag, value, replace)

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

    def fill_words(self, depth=0):
        '''
        Recursively go down tree and fill in words according to constraints
        '''
        WB = self.WB

        '''
        NODE RULES
        '''
        # DP RULES
        if self.rule == "D': NP":
            self.add_tag_ancestors('pluralize')
        elif self.rule == "DP: DP Conj DP":
            WB.add_replacement_map('Pronoun', depth=depth)
            WB.add_replacement_map('N', depth=depth)
        # NP RULES
        elif self.rule == "NP: N'":
            WB.add_replacement_map('A', depth=depth)
        # AdvP/AP RULES
        elif self.rule == "AP: A'":
            WB.add_replacement_map('Adv', 'APAdv', depth=depth)
        elif self.parent and self.parent.rule == "Adv': AdvP Adv" and self.rule.rule == "AdvP":
            WB.add_replacement_map("Adv", "APAdv", depth=depth)
        # VP RULES
        elif self.rule.rule == "VP":
            self.add_tag('accusative')

        '''
        LEAF
        '''
        if self.rule.word_cost > 0:
            d = self.rule
            leaf = self.rule.get_leaf()

            tags = self.get_tags_ancestors()
            word = WB.fill_word(leaf, tags, self)

            self.word = word #TODO

        '''
        RECURSE
        '''
        if self.third:
            # do this first bc we care about last value for rules
            self.third.fill_words(depth+1)
        if self.left:
            self.left.fill_words(depth+1)
        if self.right:
            self.right.fill_words(depth+1)

        WB.refresh(depth)

def tree_to_words(tree):
    '''
    Turn a tree into words
    '''

    tree = TreeWordNode.cast_tree(tree)

    rule = tree.data
    if rule.rule_str == 'SP: SP SP':
        return tree_to_words(tree.left) + '. ' + tree_to_words(tree.right)
    elif rule != "SP: DP VP":
        leafs = tree.get_leafs()
        return ' '.join([random.choice(words[l]) for l in leafs])

    subject = tree.left
    while subject.rule not in ["DP: Pronoun", "D': NP", "D': D NP"]:
        subject = subject.third if subject.third else subject.right
    subject.add_tag("subject")
    if subject.rule != "DP: Pronoun":
        subject.add_tag_ancestors('person', THIRD)

    tree.left.fill_words()
    tree.right.fill_words()
    #print(tree)
    return ' '.join([str(n.word) for n in tree.get_nodes() if n.word])


