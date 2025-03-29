# problem node
Path (reverse order):
`NP: N'` (53520) || D': D NP (51984) || DP: D' (56784) || P': P DP (99856) || PP: P' (96976) || PP: PP Conj PP (93328) || PP: PP Conj PP (92176) ||

current tree
`NP: N'` 53520 -> parent `D': D NP` 51984 (incomplete) >
  * leaf
  * incomplete

current root
`PP: PP Conj PP` 92176 -> parent root 92176 (incomplete) >>>>
  * `PP: PP Conj PP` 93328 -> parent `PP: PP Conj PP` 92176 (incomplete) >>>>
    > `PP: P'` 96976 -> parent `PP: PP Conj PP` 93328 (incomplete) >>
      * leaf
      * `P': P DP` 99856 -> parent `PP: P'` 96976 (incomplete)
        > leaf
        > `DP: D'` 56784 -> parent `P': P DP` 99856 (incomplete)
          * leaf
          * `D': D NP` 51984 -> parent `DP: D'` 56784 (incomplete) >>
            > leaf
            > `NP: N'` 53520 -> parent `D': D NP` 51984 (incomplete) >
              * leaf
              * incomplete
    > leaf
    > incomplete
  * leaf
  * incomplete
['>', '>', '>', '>', '>', None, '>', '>', '>', '>', None, '>', '>', '>', '>', None] >>>>>>>>>
fscore -3.0 -10

`********************************************************************************`
Path (reverse order):
`N': N` (55440) || NP: N' (53520) || D': D NP (51984) || DP: D' (56784) || P': P DP (99856) || PP: P' (96976) || PP: PP Conj PP (93328) || PP: PP Conj PP (92176) ||

current tree
`N': N` 55440 -> parent `NP: N'` 11696 (complete) <
  * leaf
  * leaf

current root
`PP: PP Conj PP` 96240 -> parent root 96240 (complete) >>>>
  * `PP: PP Conj PP` 92176 -> parent `PP: PP Conj PP` 96240 (complete) >>>>
    > `PP: P'` 92752 -> parent `PP: PP Conj PP` 92176 (complete) >>
      * leaf
      * `P': P DP` 95824 -> parent `PP: P'` 92752 (complete)
        > leaf
        > `DP: D'` 95632 -> parent `P': P DP` 95824 (complete)
          * leaf
          * `D': D NP` 65968 -> parent `DP: D'` 95632 (complete) >>
            > leaf
            > `NP: N'` 67312 -> parent `D': D NP` 65968 (complete) >
              * leaf
              * `N': N` 69040 -> parent `NP: N'` 67312 (complete) <
                > leaf
                > leaf
    > leaf
    > `PP: P'` 70768 -> parent `PP: PP Conj PP` 92176 (complete) >>
      * leaf
      * `P': P DP` 05328 -> parent `PP: P'` 70768 (complete)
        > leaf
        > `DP: Pronoun` 44016 -> parent `P': P DP` 05328 (complete) <<<<
          * leaf
          * leaf
  * leaf
  * `PP: P'` 96816 -> parent `PP: PP Conj PP` 96240 (complete) >>
    > leaf
    > `P': P DP` 01616 -> parent `PP: P'` 96816 (complete)
      * leaf
      * `DP: D'` 12720 -> parent `P': P DP` 01616 (complete)
        > leaf
        > `D': D NP` 15984 -> parent `DP: D'` 12720 (complete) >>
          * leaf
          * `NP: N'` 11696 -> parent `D': D NP` 15984 (complete) >
            > leaf
            > `N': N` 55440 -> parent `NP: N'` 11696 (complete) <
              * leaf
              * leaf
['>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>', '>'] >>>>>>>>>


## way earlier node
* this has the same `PP Conj PP` 92176 root
* however -- erroroneus nodes have another `PP Conj PP` 93328 subtree
    * as an aside -- this is pretty inefficient as far as algorithms go. I shouldn't be searching from a PP Conj PP down (same path) and do literally the same thing with an additional `PP Conj PP` node
    * so ideally i would start with the `PP Conj PP`, then add the other `PP Conj PP` as a parent of that one -- it shouldn't be a possible child

Path (reverse order):
`N': N` (69040) || NP: N' (67312) || D': D NP (65968) || DP: D' (95632) || P': P DP (95824) || PP: P' (92752) || PP: PP Conj PP (92176) ||

current tree
`N': N` 69040 -> parent `NP: N'` 67312 (complete) <
  * leaf
  * leaf

current root
`PP: PP Conj PP` 92176 -> parent root 92176 (incomplete) >>>>
  * `PP: P'` 92752 -> parent `PP: PP Conj PP` 92176 (complete) >>
    > leaf
    > `P': P DP` 95824 -> parent `PP: P'` 92752 (complete)
      * leaf
      * `DP: D'` 95632 -> parent `P': P DP` 95824 (complete)
        > leaf
        > `D': D NP` 65968 -> parent `DP: D'` 95632 (complete) >>
          * leaf
          * `NP: N'` 67312 -> parent `D': D NP` 65968 (complete) >
            > leaf
            > `N': N` 69040 -> parent `NP: N'` 67312 (complete) <
              * leaf
              * leaf
  * leaf
  * incomplete

so we see this part of the subtree

## another earlier node
this one is identical to erroneous node, it just has the new `N': N` node at the end of it
* so wtf is happening? we go to insert a node, and then it's parent gets set to the node from some other tree that we saw? causing the paths to be incorrect?
* we insert a node at the incorrect parent (a copied parent that gets reused somehow?) which totally fucks up our tree when we do `get_root` and correct pointers...

Path (reverse order):
`NP: N'` (11696) || D': D NP (15984) || DP: D' (12720) || P': P DP (01616) || PP: P' (96816) || PP: PP Conj PP (96240) || DP: Pronoun (44016) || P': P DP (05328) || PP: P' (70768) || N': N (69040) || NP: N' (67312) || D': D NP (65968) || DP: D' (95632) || P': P DP (95824) || PP: P' (92752) || PP: PP Conj PP (92176) ||

current tree
`NP: N'` 11696 -> parent `D': D NP` 15984 (incomplete) >
  * leaf
  * incomplete

current root
`PP: PP Conj PP` 96240 -> parent root 96240 (incomplete) >>>>
  * `PP: PP Conj PP` 92176 -> parent `PP: PP Conj PP` 96240 (complete) >>>>
    > `PP: P'` 92752 -> parent `PP: PP Conj PP` 92176 (complete) >>
      * leaf
      * `P': P DP` 95824 -> parent `PP: P'` 92752 (complete)
        > leaf
        > `DP: D'` 95632 -> parent `P': P DP` 95824 (complete)
          * leaf
          * `D': D NP` 65968 -> parent `DP: D'` 95632 (complete) >>
            > leaf
            > `NP: N'` 67312 -> parent `D': D NP` 65968 (complete) >
              * leaf
              * `N': N` 69040 -> parent `NP: N'` 67312 (complete) <
                > leaf
                > leaf
    > leaf
    > `PP: P'` 70768 -> parent `PP: PP Conj PP` 92176 (complete) >>
      * leaf
      * `P': P DP` 05328 -> parent `PP: P'` 70768 (complete)
        > leaf
        > `DP: Pronoun` 44016 -> parent `P': P DP` 05328 (complete) <<<<
          * leaf
          * leaf
  * leaf
  * `PP: P'` 96816 -> parent `PP: PP Conj PP` 96240 (incomplete) >>
    > leaf
    > `P': P DP` 01616 -> parent `PP: P'` 96816 (incomplete)
      * leaf
      * `DP: D'` 12720 -> parent `P': P DP` 01616 (incomplete)
        > leaf
        > `D': D NP` 15984 -> parent `DP: D'` 12720 (incomplete) >>
          * leaf
          * `NP: N'` 11696 -> parent `D': D NP` 15984 (incomplete) >
            > leaf
            > incomplete

# wait a second!!
Path (reverse order):
`V': V` (71824) || VP: V' (77808) || SP: DP VP (77232) || N': N (85168) || NP: N' (46960) || D': NP (45232) || DP: D' (43504) || DP: DP Conj DP (41584) || DP: D' (39472) || N': N (41904) || NP: N' (94672) || D': NP (94096) ||

current tree
`V': V` 71824 -> parent `VP: V'` 77808 (complete)
  * leaf
  * leaf

current root
`SP: DP VP` 77232 -> parent root 77232 (complete)
  * `DP: DP Conj DP` 41584 -> parent `SP: DP VP` 77232 (complete) >>
    > `DP: D'` 39472 -> parent `DP: DP Conj DP` 41584 (complete)
      * leaf
      * `D': NP` 94096 -> parent `DP: D'` 39472 (complete) >>>
        > leaf
        > `NP: N'` 94672 -> parent `D': NP` 94096 (complete) >
          * leaf
          * `N': N` 41904 -> parent `NP: N'` 94672 (complete) <
            > leaf
            > leaf
    > leaf
    > `DP: D'` 43504 -> parent `DP: DP Conj DP` 41584 (complete)
      * leaf
      * `D': NP` 45232 -> parent `DP: D'` 43504 (complete) >>>
        > leaf
        > `NP: N'` 46960 -> parent `D': NP` 45232 (complete) >
          * leaf
          * `N': N` 85168 -> parent `NP: N'` 46960 (complete) <
            > leaf
            > leaf
  * `VP: V'` 77808 -> parent `SP: DP VP` 77232 (complete) >
    > leaf
    > `V': V` 71824 -> parent `VP: V'` 77808 (complete)
      * leaf
      * leaf
['>', '>', '>', '>', '>', '>', '>', '>', '>'] >>>>>>>>>
fscore -6.0 -18

this node exists!! why didn't we terminate! this is literally perfect, this is exactly 9 `>`, the entire sentence, it looks so good. why didn't we terminate here?
