none of the path did's are actually in the tree

Path (reverse order):
`N': N` (18128) || NP: N' (16592) || D': D NP (15056) || DP: D' (54960) || P': P DP (30768) || PP: P' (27888) || PP: PP Conj PP (24432) || PP: PP Conj PP (23280) ||

current tree
`N': N` 18128 -> parent `NP: N'` 16208 (complete) <
  * leaf
  * leaf

current root
`PP: PP Conj PP` 77648 -> parent root 77648 (complete) >>>>
  * `PP: PP Conj PP` 23280 -> parent `PP: PP Conj PP` 77648 (complete) >>>>
    > `PP: P'` 23856 -> parent `PP: PP Conj PP` 23280 (complete) >>
      * leaf
      * `P': P DP` 26736 -> parent `PP: P'` 23856 (complete)
        > leaf
        > `DP: D'` 90704 -> parent `P': P DP` 26736 (complete)
          * leaf
          * `D': D NP` 62608 -> parent `DP: D'` 90704 (complete) >>
            > leaf
            > `NP: N'` 63952 -> parent `D': D NP` 62608 (complete) >
              * leaf
              * `N': N` 65680 -> parent `NP: N'` 63952 (complete) <
                > leaf
                > leaf
    > leaf

all of this other shit is wrong

    > `PP: P'` 67408 -> parent `PP: PP Conj PP` 23280 (complete) >>
      * leaf
      * `P': P DP` 69328 -> parent `PP: P'` 67408 (complete)
        > leaf
        > `DP: Pronoun` 73232 -> parent `P': P DP` 69328 (complete) <<<<
          * leaf
          * leaf
  * leaf
  * `PP: P'` 78224 -> parent `PP: PP Conj PP` 77648 (complete) >>
    > leaf
    > `P': P DP` 83024 -> parent `PP: P'` 78224 (complete)
      * leaf
      * `DP: D'` 08816 -> parent `P': P DP` 83024 (complete)
        > leaf
        > `D': D NP` 12080 -> parent `DP: D'` 08816 (complete) >>
          * leaf
          * `NP: N'` 16208 -> parent `D': D NP` 12080 (complete) >
            > leaf
            > `N': N` 18128 -> parent `NP: N'` 16208 (complete) <
              * leaf
              * leaf

`********************************************************************************`
previous path

Path (reverse order):
`D': D NP` (15056) || DP: D' (54960) || P': P DP (30768) || PP: P' (27888) || PP: PP Conj PP (24432) || PP: PP Conj PP (23280) ||

current tree
`D': D NP` 15056 -> parent `DP: D'` 54960 (incomplete) >>
  * leaf
  * incomplete

current root
`PP: PP Conj PP` 23280 -> parent root 23280 (incomplete) >>>>
  * `PP: PP Conj PP` 24432 -> parent `PP: PP Conj PP` 23280 (incomplete) >>>>
    > `PP: P'` 27888 -> parent `PP: PP Conj PP` 24432 (incomplete) >>
      * leaf
      * `P': P DP` 30768 -> parent `PP: P'` 27888 (incomplete)
        > leaf
        > `DP: D'` 54960 -> parent `P': P DP` 30768 (incomplete)
          * leaf
          * `D': D NP` 15056 -> parent `DP: D'` 54960 (incomplete) >>
            > leaf
            > incomplete
    > leaf


    > incomplete
  * leaf
  * incomplete
['>', '>', '>', '>', None, '>', '>', '>', '>', None, '>', '>', '>', '>', None] >>>>>>>>>
fscore -2.0 -8

# another example
* the previous tree is all correct, and then has `incomplete` nodes
* the next tree has only one thing that overlaps, the previous root
* the structure of the rooted tree appears the be the same, but again, no `did`'s overlapping except for the root
    * then we just have bullshit everywhere else

Path (reverse order):
`N': N` (50192) || NP: N' (48272) || D': NP (46352) || DP: D' (44816) || P': P DP (00880) || PP: P' (43184) || PP: PP Conj PP (41104) || PP: PP Conj PP (36880) || PP: PP Conj PP (35728) ||

current tree
`N': N` 50192 -> parent `NP: N'` 48272 (complete) <
  * leaf
  * leaf

current root
`PP: PP Conj PP` 35728 -> parent root 35728 (incomplete) >>>>
  * `PP: PP Conj PP` 36880 -> parent `PP: PP Conj PP` 35728 (incomplete) >>>>
    > `PP: PP Conj PP` 41104 -> parent `PP: PP Conj PP` 36880 (incomplete) >>>>
      * `PP: P'` 43184 -> parent `PP: PP Conj PP` 41104 (complete) >>
        > leaf
        > `P': P DP` 00880 -> parent `PP: P'` 43184 (complete)
          * leaf
          * `DP: D'` 44816 -> parent `P': P DP` 00880 (complete)
            > leaf
            > `D': NP` 46352 -> parent `DP: D'` 44816 (complete) >>>
              * leaf
              * `NP: N'` 48272 -> parent `D': NP` 46352 (complete) >
                > leaf
                > `N': N` 50192 -> parent `NP: N'` 48272 (complete) <
                  * leaf
                  * leaf
      * leaf
      * incomplete
    > leaf
    > incomplete
  * leaf
  * incomplete
['>', '>', '>', '>', '>', '>', '>', '>', '>', None, '>', '>', '>', '>', None, '>', '>', '>', '>', None] >>>>>>>>>
fscore -9.0 -18
`********************************************************************************`
Path (reverse order):
`PP: P'` (51920) || N': N (50192) || NP: N' (48272) || D': NP (46352) || DP: D' (44816) || P': P DP (00880) || PP: P' (43184) || PP: PP Conj PP (41104) || PP: PP Conj PP (36880) || PP: PP Conj PP (35728) ||

current tree
`PP: P'` 51920 -> parent `PP: PP Conj PP` 52976 (incomplete) >>
  * leaf
  * incomplete

current root
`PP: PP Conj PP` 52976 -> parent root 52976 (incomplete) >>>>
  * `PP: PP Conj PP` 36464 -> parent `PP: PP Conj PP` 52976 (complete) >>>>
    > `PP: PP Conj PP` 35728 -> parent `PP: PP Conj PP` 36464 (complete) >>>>
      * `PP: P'` 36304 -> parent `PP: PP Conj PP` 35728 (complete) >>
        > leaf
        > `P': P DP` 39184 -> parent `PP: P'` 36304 (complete)
          * leaf
          * `DP: D'` 43216 -> parent `P': P DP` 39184 (complete)
            > leaf
            > `D': NP` 44368 -> parent `DP: D'` 43216 (complete) >>>
              * leaf
              * `NP: N'` 45712 -> parent `D': NP` 44368 (complete) >
                > leaf
                > `N': N` 47440 -> parent `NP: N'` 45712 (complete) <
                  * leaf
                  * leaf
      * leaf
      * `PP: P'` 93328 -> parent `PP: PP Conj PP` 35728 (complete) >>
        > leaf
        > `P': P DP` 96592 -> parent `PP: P'` 93328 (complete)
          * leaf
          * `DP: Pronoun` 31856 -> parent `P': P DP` 96592 (complete) <<<<
            > leaf
            > leaf
    > leaf
    > `PP: P'` 37040 -> parent `PP: PP Conj PP` 36464 (complete) >>
      * leaf
      * `P': P DP` 74672 -> parent `PP: P'` 37040 (complete)
        > leaf
        > `DP: Pronoun` 82736 -> parent `P': P DP` 74672 (complete) <<<<
          * leaf
          * leaf
  * leaf
  * `PP: P'` 51920 -> parent `PP: PP Conj PP` 52976 (incomplete) >>
    > leaf
    > incomplete
