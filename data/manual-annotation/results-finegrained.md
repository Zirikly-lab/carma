######################################################################
POOLED (ALL CONDITIONS)
######################################################################
Total rows: 240
  saad: 240 valid, 0 invalid {}
  nour: 235 valid, 5 invalid {'': 5}
  qwen: 229 valid, 11 invalid {'NA': 10, 'PARSE_FAIL': 1}
  jais: 227 valid, 13 invalid {'NA': 11, 'PARSE_FAIL': 2}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=235)
  % agree : 89.8%
  Cohen κ : 0.701

saad vs Qwen  (n=229)
  % agree : 76.4%
  Cohen κ : 0.167

saad vs Jais  (n=227)
  % agree : 74.9%
  Cohen κ : 0.171

Nour vs Qwen  (n=224)
  % agree : 79.0%
  Cohen κ : 0.138

Nour vs Jais  (n=224)
  % agree : 77.7%
  Cohen κ : 0.176

Qwen vs Jais  (n=218)
  % agree : 83.0%
  Cohen κ : 0.231

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP         178         190    172        90.526316       96.629213 93.478261
   FP          57          45     39        86.666667       68.421053 76.470588

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP         178         204    164        80.392157       92.134831 85.863874
   FP          51          25     11        44.000000       21.568627 28.947368

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP         175         196    157        80.102041       89.714286 84.636119
   FP          52          31     13        41.935484       25.000000 31.325301

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP         186         199    169        84.924623       90.860215 87.792208
   FP          38          25      8        32.000000       21.052632 25.396825

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP         183         193    163        84.455959       89.071038 86.702128
   FP          41          31     11        35.483871       26.829268 30.555556

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP         193         188    172        91.489362       89.119171 90.288714
   FP          25          30      9        30.000000       36.000000 32.727273

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP      172        6
saad=FP       18       39

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP      164       14
saad=FP       40       11

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP      157       18
saad=FP       39       13

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP      169       17
Nour=FP       30        8

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP      163       20
Nour=FP       30       11

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP      172       21
Qwen=FP       16        9

============================================================
ALL FOUR AGREE (n=215): 140 rows = 65.1%

Label breakdown where all four agree:
saad
TP    135
FP      5
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    FP    TP    TP      17
TP    TP    TP    FP      14
FP    TP    TP    TP      12
TP    TP    FP    TP      11
FP    FP    TP    FP       5
TP    FP    TP    TP       5
      TP    FP    FP       3
FP    FP    FP    TP       3
      TP    FP    TP       2
            TP    FP       2
            FP    FP       1
Name: count, dtype: int64

######################################################################
CONDITION: adhd  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 19 valid, 1 invalid {'': 1}
  qwen: 18 valid, 2 invalid {'NA': 2}
  jais: 19 valid, 1 invalid {'NA': 1}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=19)
  % agree : 89.5%
  Cohen κ : 0.689

saad vs Qwen  (n=18)
  % agree : 88.9%
  Cohen κ : 0.455

saad vs Jais  (n=19)
  % agree : 73.7%
  Cohen κ : 0.128

Nour vs Qwen  (n=17)
  % agree : 88.2%
  Cohen κ : -0.062

Nour vs Jais  (n=18)
  % agree : 77.8%
  Cohen κ : 0.200

Qwen vs Jais  (n=17)
  % agree : 76.5%
  Cohen κ : -0.097

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          14          16     14             87.5           100.0 93.333333
   FP           5           3      3            100.0            60.0 75.000000

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)    F1
   TP          15          17     15        88.235294      100.000000 93.75
   FP           3           1      1       100.000000       33.333333 50.00

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          15          16     13        81.250000       86.666667 83.870968
   FP           4           3      1        33.333333       25.000000 28.571429

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)    F1
   TP          16          16     15            93.75           93.75 93.75
   FP           1           1      0             0.00            0.00   NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          15          15     13        86.666667       86.666667 86.666667
   FP           3           3      1        33.333333       33.333333 33.333333

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          16          14     13        92.857143           81.25 86.666667
   FP           1           3      0         0.000000            0.00       NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       14        0
saad=FP        2        3

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       15        0
saad=FP        2        1

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       13        2
saad=FP        3        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       15        1
Nour=FP        1        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       13        2
Nour=FP        2        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       13        3
Qwen=FP        1        0

============================================================
ALL FOUR AGREE (n=16): 12 rows = 75.0%

Label breakdown where all four agree:
saad
TP    12
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    TP    FP      2
FP    FP    TP    FP      1
      TP    FP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: anxiety  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 18 valid, 2 invalid {'': 2}
  qwen: 20 valid, 0 invalid {}
  jais: 19 valid, 1 invalid {'PARSE_FAIL': 1}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=18)
  % agree : 88.9%
  Cohen κ : 0.438

saad vs Qwen  (n=20)
  % agree : 90.0%
  Cohen κ : 0.000

saad vs Jais  (n=19)
  % agree : 73.7%
  Cohen κ : 0.159

Nour vs Qwen  (n=18)
  % agree : 88.9%
  Cohen κ : 0.000

Nour vs Jais  (n=17)
  % agree : 70.6%
  Cohen κ : 0.141

Qwen vs Jais  (n=19)
  % agree : 73.7%
  Cohen κ : 0.000

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)    F1
   TP          16          16     15            93.75           93.75 93.75
   FP           2           2      1            50.00           50.00 50.00

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          18          20     18             90.0           100.0 94.736842
   FP           2           0      0              NaN             0.0       NaN

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          17          14     13        92.857143       76.470588 83.870968
   FP           2           5      1        20.000000       50.000000 28.571429

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          16          18     16        88.888889           100.0 94.117647
   FP           2           0      0              NaN             0.0       NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          15          12     11        91.666667       73.333333 81.481481
   FP           2           5      1        20.000000       50.000000 28.571429

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          19          14     14            100.0       73.684211 84.848485
   FP           0           5      0              0.0             NaN       NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       15        1
saad=FP        1        1

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       18        0
saad=FP        2        0

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       13        4
saad=FP        1        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       16        0
Nour=FP        2        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       11        4
Nour=FP        1        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       14        5
Qwen=FP        0        0

============================================================
ALL FOUR AGREE (n=17): 10 rows = 58.8%

Label breakdown where all four agree:
saad
TP    10
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    TP    FP      4
      FP    TP    TP      1
FP    FP    TP    FP      1
      TP    TP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: bipolar  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 20 valid, 0 invalid {}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 95.0%
  Cohen κ : 0.875

saad vs Qwen  (n=20)
  % agree : 70.0%
  Cohen κ : 0.211

saad vs Jais  (n=20)
  % agree : 80.0%
  Cohen κ : 0.474

Nour vs Qwen  (n=20)
  % agree : 75.0%
  Cohen κ : 0.286

Nour vs Jais  (n=20)
  % agree : 85.0%
  Cohen κ : 0.571

Qwen vs Jais  (n=20)
  % agree : 80.0%
  Cohen κ : 0.375

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          14          15     14        93.333333      100.000000 96.551724
   FP           6           5      5       100.000000       83.333333 90.909091

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)   F1
   TP          14          16     12             75.0       85.714286 80.0
   FP           6           4      2             50.0       33.333333 40.0

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          14          16     13            81.25       92.857143 86.666667
   FP           6           4      3            75.00       50.000000 60.000000

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          15          16     13            81.25       86.666667 83.870968
   FP           5           4      2            50.00       40.000000 44.444444

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          15          16     14             87.5       93.333333 90.322581
   FP           5           4      3             75.0       60.000000 66.666667

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)   F1
   TP          16          16     14             87.5            87.5 87.5
   FP           4           4      2             50.0            50.0 50.0

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       14        0
saad=FP        1        5

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       12        2
saad=FP        4        2

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       13        1
saad=FP        3        3

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       13        2
Nour=FP        3        2

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       14        1
Nour=FP        2        3

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       14        2
Qwen=FP        2        2

============================================================
ALL FOUR AGREE (n=20): 13 rows = 65.0%

Label breakdown where all four agree:
saad
TP    11
FP     2
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    FP    TP      2
FP    FP    TP    TP      2
                  FP      1
TP    TP    TP    FP      1
FP    TP    TP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: bpd  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 19 valid, 1 invalid {'': 1}
  qwen: 20 valid, 0 invalid {}
  jais: 18 valid, 2 invalid {'NA': 2}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=19)
  % agree : 94.7%
  Cohen κ : 0.855

saad vs Qwen  (n=20)
  % agree : 80.0%
  Cohen κ : 0.273

saad vs Jais  (n=18)
  % agree : 72.2%
  Cohen κ : 0.118

Nour vs Qwen  (n=19)
  % agree : 84.2%
  Cohen κ : 0.345

Nour vs Jais  (n=18)
  % agree : 77.8%
  Cohen κ : 0.200

Qwen vs Jais  (n=18)
  % agree : 88.9%
  Cohen κ : 0.455

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          14          15     14        93.333333           100.0 96.551724
   FP           5           4      4       100.000000            80.0 88.888889

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          15          19     15        78.947368           100.0 88.235294
   FP           5           1      1       100.000000            20.0 33.333333

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          14          15     12        80.000000       85.714286 82.758621
   FP           4           3      1        33.333333       25.000000 28.571429

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          15          18     15        83.333333           100.0 90.909091
   FP           4           1      1       100.000000            25.0 40.000000

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          15          15     13        86.666667       86.666667 86.666667
   FP           3           3      1        33.333333       33.333333 33.333333

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)    F1
   TP          17          15     15       100.000000       88.235294 93.75
   FP           1           3      1        33.333333      100.000000 50.00

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       14        0
saad=FP        1        4

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       15        0
saad=FP        4        1

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       12        2
saad=FP        3        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       15        0
Nour=FP        3        1

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       13        2
Nour=FP        2        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       15        2
Qwen=FP        0        1

============================================================
ALL FOUR AGREE (n=18): 13 rows = 72.2%

Label breakdown where all four agree:
saad
TP    12
FP     1
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    FP    TP    TP      2
TP    TP    TP    FP      2
FP    TP    TP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: depression  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 20 valid, 0 invalid {}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 85.0%
  Cohen κ : 0.625

saad vs Qwen  (n=20)
  % agree : 75.0%
  Cohen κ : 0.000

saad vs Jais  (n=20)
  % agree : 75.0%
  Cohen κ : 0.000

Nour vs Qwen  (n=20)
  % agree : 70.0%
  Cohen κ : 0.000

Nour vs Jais  (n=20)
  % agree : 70.0%
  Cohen κ : 0.000

Qwen vs Jais  (n=20)
  % agree : 100.0%
  Cohen κ : nan

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          15          14     13        92.857143       86.666667 89.655172
   FP           5           6      4        66.666667       80.000000 72.727273

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          15          20     15             75.0           100.0 85.714286
   FP           5           0      0              NaN             0.0       NaN

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          15          20     15             75.0           100.0 85.714286
   FP           5           0      0              NaN             0.0       NaN

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          14          20     14             70.0           100.0 82.352941
   FP           6           0      0              NaN             0.0       NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          14          20     14             70.0           100.0 82.352941
   FP           6           0      0              NaN             0.0       NaN

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)    F1
   TP          20          20     20            100.0           100.0 100.0
   FP           0           0      0              NaN             NaN   NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       13        2
saad=FP        1        4

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       15        0
saad=FP        5        0

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       15        0
saad=FP        5        0

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       14        0
Nour=FP        6        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       14        0
Nour=FP        6        0

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       20        0
Qwen=FP        0        0

============================================================
ALL FOUR AGREE (n=20): 13 rows = 65.0%

Label breakdown where all four agree:
saad
TP    13
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    FP    TP    TP      4
TP    FP    TP    TP      2
FP    TP    TP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: eating_disorder  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 19 valid, 1 invalid {'NA': 1}
  jais: 18 valid, 2 invalid {'NA': 2}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 90.0%
  Cohen κ : 0.733

saad vs Qwen  (n=19)
  % agree : 68.4%
  Cohen κ : -0.096

saad vs Jais  (n=18)
  % agree : 77.8%
  Cohen κ : -0.091

Nour vs Qwen  (n=19)
  % agree : 68.4%
  Cohen κ : -0.096

Nour vs Jais  (n=18)
  % agree : 77.8%
  Cohen κ : -0.091

Qwen vs Jais  (n=17)
  % agree : 88.2%
  Cohen κ : -0.062

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          15          15     14        93.333333       93.333333 93.333333
   FP           5           5      4        80.000000       80.000000 80.000000

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)    F1
   TP          14          18     13        72.222222       92.857143 81.25
   FP           5           1      0         0.000000        0.000000   NaN

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)   F1
   TP          15          17     14        82.352941       93.333333 87.5
   FP           3           1      0         0.000000        0.000000  NaN

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)    F1
   TP          14          18     13        72.222222       92.857143 81.25
   FP           5           1      0         0.000000        0.000000   NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)   F1
   TP          15          17     14        82.352941       93.333333 87.5
   FP           3           1      0         0.000000        0.000000  NaN

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)    F1
   TP          16          16     15            93.75           93.75 93.75
   FP           1           1      0             0.00            0.00   NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       14        1
saad=FP        1        4

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       13        1
saad=FP        5        0

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       14        1
saad=FP        3        0

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       13        1
Nour=FP        5        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       14        1
Nour=FP        3        0

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       15        1
Qwen=FP        1        0

============================================================
ALL FOUR AGREE (n=17): 11 rows = 64.7%

Label breakdown where all four agree:
saad
TP    11
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    FP    TP    TP      2
      TP    TP    TP      1
TP    FP    TP    TP      1
      TP    TP    FP      1
            FP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: ocd  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 19 valid, 1 invalid {'NA': 1}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 85.0%
  Cohen κ : -0.071

saad vs Qwen  (n=19)
  % agree : 68.4%
  Cohen κ : -0.163

saad vs Jais  (n=20)
  % agree : 75.0%
  Cohen κ : 0.167

Nour vs Qwen  (n=19)
  % agree : 78.9%
  Cohen κ : 0.000

Nour vs Jais  (n=20)
  % agree : 80.0%
  Cohen κ : 0.273

Qwen vs Jais  (n=19)
  % agree : 78.9%
  Cohen κ : 0.367

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          18          19     17        89.473684       94.444444 91.891892
   FP           2           1      0         0.000000        0.000000       NaN

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)    F1
   TP          17          15     13        86.666667       76.470588 81.25
   FP           2           4      0         0.000000        0.000000   NaN

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          18          15     14        93.333333       77.777778 84.848485
   FP           2           5      1        20.000000       50.000000 28.571429

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          19          15     15            100.0       78.947368 88.235294
   FP           0           4      0              0.0             NaN       NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          19          15     15            100.0       78.947368 88.235294
   FP           1           5      1             20.0      100.000000 33.333333

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          15          15     13        86.666667       86.666667 86.666667
   FP           4           4      2        50.000000       50.000000 50.000000

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       17        1
saad=FP        2        0

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       13        4
saad=FP        2        0

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       14        4
saad=FP        1        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       15        4
Nour=FP        0        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       15        4
Nour=FP        0        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       13        2
Qwen=FP        2        2

============================================================
ALL FOUR AGREE (n=19): 12 rows = 63.2%

Label breakdown where all four agree:
saad
TP    12
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    FP    FP      2
                  TP      2
FP    TP    TP    FP      1
                  TP      1
TP    TP    TP    FP      1
Name: count, dtype: int64

######################################################################
CONDITION: panic  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 20 valid, 0 invalid {}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 70.0%
  Cohen κ : 0.241

saad vs Qwen  (n=20)
  % agree : 75.0%
  Cohen κ : 0.342

saad vs Jais  (n=20)
  % agree : 65.0%
  Cohen κ : 0.000

Nour vs Qwen  (n=20)
  % agree : 85.0%
  Cohen κ : 0.318

Nour vs Jais  (n=20)
  % agree : 85.0%
  Cohen κ : 0.000

Qwen vs Jais  (n=20)
  % agree : 90.0%
  Cohen κ : 0.000

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)   F1
   TP          13          17     12        70.588235       92.307692 80.0
   FP           7           3      2        66.666667       28.571429 40.0

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          13          18     13        72.222222      100.000000 83.870968
   FP           7           2      2       100.000000       28.571429 44.444444

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          13          20     13             65.0           100.0 78.787879
   FP           7           0      0              NaN             0.0       NaN

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          17          18     16        88.888889       94.117647 91.428571
   FP           3           2      1        50.000000       33.333333 40.000000

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          17          20     17             85.0           100.0 91.891892
   FP           3           0      0              NaN             0.0       NaN

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          18          20     18             90.0           100.0 94.736842
   FP           2           0      0              NaN             0.0       NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       12        1
saad=FP        5        2

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       13        0
saad=FP        5        2

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       13        0
saad=FP        7        0

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       16        1
Nour=FP        2        1

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       17        0
Nour=FP        3        0

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       18        0
Qwen=FP        2        0

============================================================
ALL FOUR AGREE (n=20): 12 rows = 60.0%

Label breakdown where all four agree:
saad
TP    12
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    TP    TP    TP      4
      FP    TP    TP      1
TP    FP    TP    TP      1
FP    TP    FP    TP      1
      FP    FP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: ptsd  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 18 valid, 2 invalid {'NA': 2}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 95.0%
  Cohen κ : 0.886

saad vs Qwen  (n=18)
  % agree : 66.7%
  Cohen κ : 0.100

saad vs Jais  (n=20)
  % agree : 70.0%
  Cohen κ : 0.178

Nour vs Qwen  (n=18)
  % agree : 72.2%
  Cohen κ : 0.151

Nour vs Jais  (n=20)
  % agree : 75.0%
  Cohen κ : 0.219

Qwen vs Jais  (n=18)
  % agree : 83.3%
  Cohen κ : -0.080

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          13          14     13        92.857143      100.000000 96.296296
   FP           7           6      6       100.000000       85.714286 92.307692

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          12          16     11            68.75       91.666667 78.571429
   FP           6           2      1            50.00       16.666667 25.000000

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)    F1
   TP          13          19     13        68.421053      100.000000 81.25
   FP           7           1      1       100.000000       14.285714 25.00

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          13          16     12             75.0       92.307692 82.758621
   FP           5           2      1             50.0       20.000000 28.571429

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          14          19     14        73.684211      100.000000 84.848485
   FP           6           1      1       100.000000       16.666667 28.571429

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          16          17     15        88.235294           93.75 90.909091
   FP           2           1      0         0.000000            0.00       NaN

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       13        0
saad=FP        1        6

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       11        1
saad=FP        5        1

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       13        0
saad=FP        6        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       12        1
Nour=FP        4        1

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       14        0
Nour=FP        5        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       15        1
Qwen=FP        2        0

============================================================
ALL FOUR AGREE (n=18): 11 rows = 61.1%

Label breakdown where all four agree:
saad
TP    11
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    FP    TP    TP      3
TP    TP    FP    TP      1
FP    FP    FP    TP      1
      TP    TP    TP      1
      FP    TP    FP      1
Name: count, dtype: int64

######################################################################
CONDITION: schizophrenia  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 16 valid, 4 invalid {'NA': 3, 'PARSE_FAIL': 1}
  jais: 18 valid, 2 invalid {'PARSE_FAIL': 1, 'NA': 1}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 95.0%
  Cohen κ : 0.894

saad vs Qwen  (n=16)
  % agree : 81.2%
  Cohen κ : 0.538

saad vs Jais  (n=18)
  % agree : 77.8%
  Cohen κ : 0.478

Nour vs Qwen  (n=16)
  % agree : 75.0%
  Cohen κ : 0.333

Nour vs Jais  (n=18)
  % agree : 72.2%
  Cohen κ : 0.286

Qwen vs Jais  (n=15)
  % agree : 80.0%
  Cohen κ : 0.444

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          12          13     12        92.307692           100.0 96.000000
   FP           8           7      7       100.000000            87.5 93.333333

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          11          12     10        83.333333       90.909091 86.956522
   FP           5           4      3        75.000000       60.000000 66.666667

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          11          15     11        73.333333      100.000000 84.615385
   FP           7           3      3       100.000000       42.857143 60.000000

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          12          12     10        83.333333       83.333333 83.333333
   FP           4           4      2        50.000000       50.000000 50.000000

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          12          15     11        73.333333       91.666667 81.481481
   FP           6           3      2        66.666667       33.333333 44.444444

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          11          12     10        83.333333       90.909091 86.956522
   FP           4           3      2        66.666667       50.000000 57.142857

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       12        0
saad=FP        1        7

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       10        1
saad=FP        2        3

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       11        0
saad=FP        4        3

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       10        2
Nour=FP        2        2

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       11        1
Nour=FP        4        2

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       10        1
Qwen=FP        2        2

============================================================
ALL FOUR AGREE (n=15): 10 rows = 66.7%

Label breakdown where all four agree:
saad
TP    9
FP    1
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
FP    TP    FP    FP      1
TP    TP    FP    TP      1
FP    FP    TP    FP      1
            FP    TP      1
            TP    TP      1
Name: count, dtype: int64

######################################################################
CONDITION: sleep_disorder  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 19 valid, 1 invalid {'': 1}
  qwen: 19 valid, 1 invalid {'NA': 1}
  jais: 15 valid, 5 invalid {'NA': 5}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=19)
  % agree : 89.5%
  Cohen κ : 0.000

saad vs Qwen  (n=19)
  % agree : 73.7%
  Cohen κ : -0.145

saad vs Jais  (n=15)
  % agree : 66.7%
  Cohen κ : 0.118

Nour vs Qwen  (n=18)
  % agree : 83.3%
  Cohen κ : 0.000

Nour vs Jais  (n=15)
  % agree : 66.7%
  Cohen κ : 0.000

Qwen vs Jais  (n=15)
  % agree : 60.0%
  Cohen κ : 0.000

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)        F1
   TP          17          19     17        89.473684           100.0 94.444444
   FP           2           0      0              NaN             0.0       NaN

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          17          16     14             87.5       82.352941 84.848485
   FP           2           3      0              0.0        0.000000       NaN

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          13          10      9             90.0       69.230769 78.260870
   FP           2           5      1             20.0       50.000000 28.571429

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          18          15     15            100.0       83.333333 90.909091
   FP           0           3      0              0.0             NaN       NaN

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)   F1
   TP          15          10     10            100.0       66.666667 80.0
   FP           0           5      0              0.0             NaN  NaN

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          12          10      8             80.0       66.666667 72.727273
   FP           3           5      1             20.0       33.333333 25.000000

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       17        0
saad=FP        2        0

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       14        3
saad=FP        2        0

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP        9        4
saad=FP        1        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       15        3
Nour=FP        0        0

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       10        5
Nour=FP        0        0

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP        8        4
Qwen=FP        2        1

============================================================
ALL FOUR AGREE (n=15): 7 rows = 46.7%

Label breakdown where all four agree:
saad
TP    7
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    TP    FP      3
            FP    TP      2
                  FP      1
FP    TP    TP    TP      1
                  FP      1
Name: count, dtype: int64

######################################################################
CONDITION: suicidal  (n=20)
######################################################################
Total rows: 20
  saad: 20 valid, 0 invalid {}
  nour: 20 valid, 0 invalid {}
  qwen: 20 valid, 0 invalid {}
  jais: 20 valid, 0 invalid {}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

saad vs Nour  (n=20)
  % agree : 100.0%
  Cohen κ : 1.000

saad vs Qwen  (n=20)
  % agree : 80.0%
  Cohen κ : 0.216

saad vs Jais  (n=20)
  % agree : 90.0%
  Cohen κ : 0.459

Nour vs Qwen  (n=20)
  % agree : 80.0%
  Cohen κ : 0.216

Nour vs Jais  (n=20)
  % agree : 90.0%
  Cohen κ : 0.459

Qwen vs Jais  (n=20)
  % agree : 90.0%
  Cohen κ : 0.459

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- saad vs Nour ---
label  saad_count  Nour_count  agree  prec(Nour→saad)  rec(saad→Nour)    F1
   TP          17          17     17            100.0           100.0 100.0
   FP           3           3      3            100.0           100.0 100.0

--- saad vs Qwen ---
label  saad_count  Qwen_count  agree  prec(Qwen→saad)  rec(saad→Qwen)        F1
   TP          17          17     15        88.235294       88.235294 88.235294
   FP           3           3      1        33.333333       33.333333 33.333333

--- saad vs Jais ---
label  saad_count  Jais_count  agree  prec(Jais→saad)  rec(saad→Jais)        F1
   TP          17          19     17        89.473684      100.000000 94.444444
   FP           3           1      1       100.000000       33.333333 50.000000

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP          17          17     15        88.235294       88.235294 88.235294
   FP           3           3      1        33.333333       33.333333 33.333333

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP          17          19     17        89.473684      100.000000 94.444444
   FP           3           1      1       100.000000       33.333333 50.000000

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP          17          19     17        89.473684      100.000000 94.444444
   FP           3           1      1       100.000000       33.333333 50.000000

============================================================
CONFUSION MATRICES
============================================================

--- saad (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
saad=TP       17        0
saad=FP        0        3

--- saad (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
saad=TP       15        2
saad=FP        2        1

--- saad (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
saad=TP       17        0
saad=FP        2        1

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP       15        2
Nour=FP        2        1

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP       17        0
Nour=FP        2        1

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP       17        0
Qwen=FP        2        1

============================================================
ALL FOUR AGREE (n=20): 16 rows = 80.0%

Label breakdown where all four agree:
saad
TP    15
FP     1
Name: count, dtype: int64

Top disagreement patterns (saad / nour / qwen / jais):
saad  nour  qwen  jais
TP    TP    FP    TP      2
FP    FP    TP    TP      2
Name: count, dtype: int64
