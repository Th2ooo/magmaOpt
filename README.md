 
# Shape optimization on magmatic reservoirs shared repo


Folder guide :

- `biblio` : some relevant articles for us to read (including examples from Geophysical Research Letters)
- `magmaOpt` : the source code based on so-tuto, exlcluding result file and data because of size
- `paper` : tex folder of the article including
    - the bibliography in bib format ```refs.bib```
    - the main text ```main.tex```
    - the supplementary material ``sup_mat.tex``
    

Feel free to clone and then push/pull your changes to the paper


---

Guidelines for the paper :
    - website : https://agupubs.onlinelibrary.wiley.com/journal/19448007
    - main text should be below 12 publication units (PU) with 1 unit = 500 words or a figure
    - currently $\approx 11$ PU in the draft

---

Next meeting: Wenesday 4th, 2:30 PM french time
Link (will remain the same): https://framatalk.org/6l3z2ynuib

---

# TODO list (unordered) :


## Article

- Comments [FS]
- Section 2 [CD]
    - See if changes to fig. 1 with BC
    - Explanation on adjoint state ?
    - Explanation of 2D representation of level-set
    - Talk about termination criteria [TP]

- Section 3 [TP]
    - Improve figure 3 (no $\tau$ in main text but in supplementary)
    - Re run tests with CORRECT derivative formula :'-(
    - Describe behavior of algorithm

    - In subsection 2, rework figure 2 (scale of shape, extent, beautiful plots)
    - Compare with the results of previous inversion from sigmundsson2024 and conclude

- see if rework needed on Introduction
- Rework Discussion and Conclusion


## Code [TP]

- Change J' expression
- Create a "run" object to centralize informations about one run with appropriate methods to explore the run
- Clean the code to make it readable and clear
- Official repo:
    - as fork of sotuto
    - with installation instructions
    - with an example
- Improve plots

- Change boundary condition on sides (explore this) ?
