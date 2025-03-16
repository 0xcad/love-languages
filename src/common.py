import random

def combine_bf(*args) -> list:
    def helper(ops_path, ops) -> list:
        if ops:
            ops = [c for c in ops]
            while (ops and ops_path and
                   ((ops[0] == '>' and ops_path[-1] == '<') or
                   (ops[0] == '<' and ops_path[-1] == '>') or
                   (ops[0] == '+' and ops_path[-1] == '-') or
                   (ops[0] == '-' and ops_path[-1] == '+')# or
                   #(ops[0] == None and ops_path[-1] == None)
                   )):
                del ops[0]
                #if ops_path[-1] is not None:
                #    ops_path.pop()
                ops_path.pop()
            ops_path.extend(ops)
        return ops_path
    ops_path = args[0]
    for i in range(1, len(args)):
        ops = [c for c in args[i]]
        ops_path = helper(ops_path, ops)

    return ops_path

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

words = {
    'Pronoun': ['I', 'YOU'],
    'D': ['YOUR', 'MY'], #the, a
    'N': ['ADORATION', 'AFFECTION', 'AMBITION', 'APPETITE', 'ARDOUR', 'CHARM', 'DESIRE', 'DEVOTION', 'EAGERNESS', 'ENCHANTMENT', 'ENTHUSIASM', 'FANCY', 'FELLOW FEELING', 'FERVOUR', 'FONDNESS', 'HEART', 'HUNGER', 'INFATUATION', 'LIKING', 'LONGING', 'LOVE', 'LUST', 'PASSION', 'RAPTURE', 'SYMPATHY', 'TENDERNESS', 'THIRST', 'WISH', 'YEARNING'],
    'Adv': ['AFFECTIONATELY', 'ANXIOUSLY', 'ARDENTLY', 'AVIDLY', 'BEAUTIFULLY', 'BREATHLESSLY', 'BURNINGLY', 'COVETOUSLY', 'CURIOUSLY', 'DEVOTEDLY', 'EAGERLY', 'FERVENTLY', 'FONDLY', 'IMPATIENTLY', 'KEENLY', 'LOVINGLY', 'PASSIONATELY', 'SEDUCTIVELY', 'TENDERLY', 'WINNINGLY', 'WISTFULLY'],
    'A': ['ADORABLE', 'AFFECTIONATE', 'AMOROUS', 'ANXIOUS', 'ARDENT', 'AVID', 'BREATHLESS', 'BURNING', 'COVETOUS', 'CRAVING', 'CURIOUS', 'DARLING', 'DEAR', 'DEVOTED', 'EAGER', 'EROTIC', 'FERVENT', 'FOND', 'IMPATIENT', 'KEEN', 'LITTLE', 'LOVEABLE', 'LOVESICK', 'LOVING', 'PASSIONATE', 'PRECIOUS', 'SWEET', 'SYMPATHETIC', 'TENDER', 'UNSATISFIED', 'WISTFUL'],
    'V': ['ADORE', 'ATTRACT', 'CARE', 'CHERISH', 'CLING', 'DESIRE','HOLD', 'HOPE', 'HUNGER', 'LIKE', 'LOVE', 'OBSESS', 'SIGH', 'TEMPT', 'WANT', 'WISH', 'WOO', 'YEARN'],
    'DTV': ['GIVE', 'OFFER', 'PROMISE', 'OFFER'], #DEDICATE?
    'TV': ['ADORE', 'CARE FOR', 'CLING TO', 'DESIRE', 'HOLD DEAR', 'HOPE FOR', 'HUNGER FOR', 'LONG FOR', 'LOVE', 'LUST AFTER', 'PANT FOR', 'PINE FOR', 'PRIZE', 'SIGHT FOR', 'TEMPT', 'THIRST FOR', 'TREASURE', 'WANT', 'WISH', 'YEARN FOR'],
    'P': ['WITH', 'IN', 'TO'],
    'Conj': ['AND'],
    'QUERY': ['WHAT?', 'BUT WHY?', 'FOR WHAT?'],
    'EXC': ['OH!', 'PLEASE!'],
}
def tree_to_words(tree):
    '''
    Turn a tree into words
    '''
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
