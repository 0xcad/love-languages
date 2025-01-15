'''
A program that encodes our rules and constructs syntactically valid sentences with them

Start at a TP and apply the only rule we have. At each other level, randomly apply rules to build up our phrases. At the end fill out the heads with words from a word bank.


god wouldn't it be great if there was some markov-based, simulated annealing way i could stuff the encodings into my rules? we give it a bf string to try and fit itself around. it starts with a random encoding, tries to fit it to a string. we assign it points based on how many times it fails to produce valid sentences. like in MH if we want to pick a new encoding, we randomly change a rule, proceed from there.
'''
