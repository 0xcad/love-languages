from collections import Counter

bf = '[],.><+-\n'
with open('corpus.txt') as f:
    s = f.read()

s = ''.join([x for x in s if x in bf])
#while s.count('\n\n'):
#    s = s.replace('\n\n', '\n')
s = s.replace('\n\n', '!')
s = s.replace('\n', '')
s = s.replace('!', '\n')
s = s.strip()
print(s)

d = {}

n = 3
max_repeats = 1000000
while max_repeats > 3:
    c = Counter(
        [''.join([s[i + j] for j in range(n)])
         for i in range(len(s) - n + 1)]
        )
    print(n, len(c), max(c.values()))
    max_repeats = max(c.values())
    n += 1
