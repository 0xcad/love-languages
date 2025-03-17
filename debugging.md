recursing on >>
 found >> in >>>>
hey complete SP: DP VP tree 54448 -> parent root 54448 (incomplete) >>>>
  * incomplete
  * incomplete `SP: DP VP` 51936 -> parent root 51936 (complete)
  * `DP: D'` 52640 -> parent `SP: DP VP` 51936 (complete)
    > leaf
    > `D': NP` 52464 -> parent `DP: D'` 52640 (complete) >>>
      * leaf
      * `NP: N'` 52288 -> parent `D': NP` 52464 (complete) >
        > leaf
        > `N': N` 52112 -> parent `NP: N'` 52288 (complete) <
          * leaf
          * leaf
  * `VP: V'` 51760 -> parent `SP: DP VP` 51936 (complete) >
    > leaf
    > `V': V` 52816 -> parent `VP: V'` 51760 (complete)
      * leaf
      * leaf ['>', '>', '>', '>'] ['>', '>', '>', '>']
  recursing on <<
  found << in <<<
hey complete SP: DP VP tree 84592 -> parent root 84592 (incomplete) <<<
  * incomplete
  * incomplete `SP: DP VP` 42912 -> parent root 42912 (complete)
  * `DP: Pronoun` 43088 -> parent `SP: DP VP` 42912 (complete) <<<<
    > leaf
    > leaf
  * `VP: V'` 42736 -> parent `SP: DP VP` 42912 (complete) >
    > leaf
    > `V': V` 43264 -> parent `VP: V'` 42736 (complete)
      * leaf
      * leaf ['<', '<', '<'] ['<', '<', '<']
   recursing on >
   found > in >
hey complete SP: DP VP tree 84272 -> parent root 84272 (incomplete) >
  * incomplete
  * incomplete `SP: DP VP` 98336 -> parent root 98336 (complete)
  * `DP: D'` 98160 -> parent `SP: DP VP` 98336 (complete)
    > leaf
    > `D': D NP` 97984 -> parent `DP: D'` 98160 (complete)
      * leaf
      * `NP: N'` 97808 -> parent `D': D NP` 97984 (complete) >
        > leaf
        > `N': N` 98864 -> parent `NP: N'` 97808 (complete) <
          * leaf
          * leaf
  * `VP: V'` 98688 -> parent `SP: DP VP` 98336 (complete) >
    > leaf
    > `V': V` 98512 -> parent `VP: V'` 98688 (complete)
      * leaf
      * leaf ['>'] ['>']
uh oh
want ['>', '>']
got ['>', '>', '>']
complete SP: DP VP tree 54448 -> parent root 54448 (incomplete) >>>
  * leaf
  * complete SP: DP VP tree 84592 -> parent complete SP: DP VP tree 54448 (incomplete) <<
    > leaf
    > complete SP: DP VP tree 84272 -> parent complete SP: DP VP tree 84592 (incomplete) >
      * leaf
      * leaf
[['>', '>', '>'], ['<', '<'], ['>']]
tree
`SP: DP VP` 51936 -> parent root 51936 (complete)
  * `DP: D'` 52640 -> parent `SP: DP VP` 51936 (complete)
    > leaf
    > `D': NP` 52464 -> parent `DP: D'` 52640 (complete) >>>
      * leaf
      * `NP: N'` 52288 -> parent `D': NP` 52464 (complete) >
        > leaf
        > `N': N` 52112 -> parent `NP: N'` 52288 (complete) <
          * leaf
          * leaf
  * `VP: V'` 51760 -> parent `SP: DP VP` 51936 (complete) >
    > leaf
    > `V': V` 52816 -> parent `VP: V'` 51760 (complete)
      * leaf
      * leaf ['>', '>', '>']
tree
`SP: DP VP` 42912 -> parent root 42912 (complete)
  * `DP: Pronoun` 43088 -> parent `SP: DP VP` 42912 (complete) <<<<
    > leaf
    > leaf
  * `VP: V'` 42736 -> parent `SP: DP VP` 42912 (complete) >
    > leaf
    > `V': V` 43264 -> parent `VP: V'` 42736 (complete)
      * leaf
      * leaf ['<', '<']
tree
`SP: DP VP` 98336 -> parent root 98336 (complete)
  * `DP: D'` 98160 -> parent `SP: DP VP` 98336 (complete)
    > leaf
    > `D': D NP` 97984 -> parent `DP: D'` 98160 (complete)
      * leaf
      * `NP: N'` 97808 -> parent `D': D NP` 97984 (complete) >
        > leaf
        > `N': N` 98864 -> parent `NP: N'` 97808 (complete) <
          * leaf
          * leaf
  * `VP: V'` 98688 -> parent `SP: DP VP` 98336 (complete) >
    > leaf
    > `V': V` 98512 -> parent `VP: V'` 98688 (complete)
      * leaf
      * leaf ['>'
