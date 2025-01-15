nouns = ['dog', 'cat', 'person']
verbs = ['walks', 'jumps', 'swims']
adjectives = ['pretty', 'nice', 'sweet']

def brainfuckStringToPSR(s):
    s = s.replace('+', ' noun ')
    s = s.replace('[', ' verb ')
    s = s.replace(']', ' adj ')
    s = s.replace('>', ' tense ')
    s = s.replace('<', ' comp ')
    s = s.replace('.', ' prep ')
    s = s.replace('-', ' det ')
    return s

def brainfuckStringToPSR(s):
    s = s.replace('+', ' noun ')
    s = s.replace('[', ' verb ')
    s = s.replace(']', ' adj ')
    s = s.replace('>', ' tense ')
    s = s.replace('<', ' comp ')
    s = s.replace('.', ' prep ')
s = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'
