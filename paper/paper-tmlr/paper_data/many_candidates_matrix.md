# Many Candidates Matrix

## Methodology

We first **reduce the sample** to only Task:Test pairs that have **"many" candidates**, defined here as having **>= {threshold} filled candidate columns** in the methodology matrix (i.e., >= {threshold} distinct method columns with a PASS or FAIL entry).

We then classify every method column into one of three types: **Text**, **Image**, or **Code**. **Deep** is folded into **Text**. A Task:Test is considered to have a PASS for a type if **any method in that type** has status **PASS**.

The 3×3 matrix counts, for each row type R and column type C, how many Task:Test pairs have **at least one PASS in R** and **zero PASS in C**. A Task:Test can contribute to multiple cells if it satisfies multiple row/column conditions. The diagonal is marked NA by definition.

- Threshold (many candidates): >= 29 filled columns
- Task:Test count after filtering: 130

| | Text | Image | Code |
| --- | --- | --- | --- |
| Text | NA | 13 | 7 |
| Image | 17 | NA | 11 |
| Code | 18 | 18 | NA |

### Task:Test Lists by Cell

**Text PASS, Image NO PASS** (13):

0934a4d8:1, 35ab12c3:1, 446ef5d2:1, 4c7dc4dd:2, 64efde09:1, 71e489b6:2, a25697e4:2, a32d8b75:1, a32d8b75:2, aa4ec2a5:1, dfadab01:1, e3721c99:1, e3721c99:2

**Text PASS, Code NO PASS** (7):

1ae2feb7:3, 20a9e565:2, 78332cb0:1, 88bcf3b4:2, a32d8b75:1, a6f40cea:1, dfadab01:1

**Image PASS, Text NO PASS** (17):

142ca369:1, 20a9e565:1, 247ef758:2, 28a6681f:1, 2d0172a1:1, 2d0172a1:2, 3a25b0d8:2, 4c7dc4dd:1, 4e34c42c:1, 7666fa5d:1, 7b0280bc:1, 89565ca0:1, a47bf94d:1, b6f77b65:1, b6f77b65:2, d35bdbdc:1, fc7cae8d:1

**Image PASS, Code NO PASS** (11):

1ae2feb7:3, 20a9e565:1, 20a9e565:2, 2d0172a1:1, 4e34c42c:1, 78332cb0:1, 88bcf3b4:2, a6f40cea:1, b6f77b65:1, b6f77b65:2, d35bdbdc:1

**Code PASS, Text NO PASS** (18):

13e47133:1, 13e47133:2, 142ca369:1, 16b78196:1, 247ef758:2, 269e22fb:2, 271d71e2:1, 28a6681f:1, 2d0172a1:2, 3a25b0d8:2, 4c7dc4dd:1, 7666fa5d:1, 78332cb0:2, 7b0280bc:1, 7b80bb43:1, 89565ca0:1, a47bf94d:1, fc7cae8d:1

**Code PASS, Image NO PASS** (18):

0934a4d8:1, 13e47133:1, 13e47133:2, 16b78196:1, 269e22fb:2, 271d71e2:1, 35ab12c3:1, 446ef5d2:1, 4c7dc4dd:2, 64efde09:1, 71e489b6:2, 78332cb0:2, 7b80bb43:1, a25697e4:2, a32d8b75:2, aa4ec2a5:1, e3721c99:1, e3721c99:2


## Only-One-Category Presence

Counts of Task:Test problems (with >= threshold filled columns) that have **at least one PASS** in the given category and **zero PASS** in the other two.

| Category | Count |
| --- | --- |
| Text only | 2 |
| Image only | 6 |
| Code only | 7 |

### Task:Test Lists (Only-One-Category)

**Text only** (2):

a32d8b75:1, dfadab01:1

**Image only** (6):

20a9e565:1, 2d0172a1:1, 4e34c42c:1, b6f77b65:1, b6f77b65:2, d35bdbdc:1

**Code only** (7):

13e47133:1, 13e47133:2, 16b78196:1, 269e22fb:2, 271d71e2:1, 78332cb0:2, 7b80bb43:1

