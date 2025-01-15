# Phrase Structure Rules (PSR) Language

# Goal
create a turing complete programming language based on syntax structures for the English language. ideally this would respect the tree structure, but I might not be able to go as far with this.

So that's like sentence -> DP VP, VP -> V, VP -> V V, DP -> D NP, stuff like that

## idea
I think the most direct way I could take this, would be to take a language like Brainfuck or a Brainfuck Minimalization, and map the instructions to things like DP, VP, AP, etc. Then, I'd create some basic functions that allow for actual programming that are syntactically correct.

So code is created by hand, is then ran through the linter that I build (which checks to make sure it's syntactially correct), and then is converted to Brainfuck and compiled. I'd probably represnt the code itself as strings like "D N V D A N", and then substitute it for words that are syntaxically grammatical. So that string can become "The dog eats the angry orange", or "the house destroys the purple hippo".

### continuation
I think it would be *really cool* to have another program, that, when given a valid PSR string, would fill out the words to make it read as a grammatical love letter. This is of course inspired by the [Strachey love letter algorithm](https://en.wikipedia.org/wiki/Strachey_love_letter_algorithm), one of the first examples of computer art / perhaps the first example of electronic literature, and "a queer critique of heteronormative expressions of love"

how cool would it be to have a love letter or something that's also a program? and I think it would also continue Strachey's critiques, where the purpose isn't even love at all but just running a file
