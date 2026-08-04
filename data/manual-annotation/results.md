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
