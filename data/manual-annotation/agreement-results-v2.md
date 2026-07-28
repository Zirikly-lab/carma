Total rows: 260
  fady: 259 valid, 1 invalid {'NA': 1}
  nour: 255 valid, 5 invalid {'': 5}
  qwen: 244 valid, 16 invalid {'NA': 15, 'PARSE_FAIL': 1}
  jais: 246 valid, 14 invalid {'NA': 12, 'PARSE_FAIL': 2}

============================================================
PAIRWISE AGREEMENT SUMMARY
============================================================

Fady vs Nour  (n=254)
  % agree : 85.8%
  Cohen κ : 0.641

Fady vs Qwen  (n=243)
  % agree : 70.8%
  Cohen κ : 0.115

Fady vs Jais  (n=245)
  % agree : 69.8%
  Cohen κ : 0.159

Nour vs Qwen  (n=239)
  % agree : 76.6%
  Cohen κ : 0.119

Nour vs Jais  (n=243)
  % agree : 74.9%
  Cohen κ : 0.182

Qwen vs Jais  (n=233)
  % agree : 82.8%
  Cohen κ : 0.237

============================================================
PER-LABEL BREAKDOWN (precision / recall / F1)
  prec(B→A) = of B's calls for label, how many A agrees
  rec(A→B)  = of A's calls for label, how many B agrees
============================================================

--- Fady vs Nour ---
label  Fady_count  Nour_count  agree  prec(Nour→Fady)  rec(Fady→Nour)        F1
   TP         177         195    168        86.153846       94.915254 90.322581
   FP          77          59     50        84.745763       64.935065 73.529412

--- Fady vs Qwen ---
label  Fady_count  Qwen_count  agree  prec(Qwen→Fady)  rec(Fady→Qwen)        F1
   TP         174         217    160        73.732719       91.954023 81.841432
   FP          69          26     12        46.153846       17.391304 25.263158

--- Fady vs Jais ---
label  Fady_count  Jais_count  agree  prec(Jais→Fady)  rec(Fady→Jais)        F1
   TP         172         208    153        73.557692       88.953488 80.526316
   FP          73          37     18        48.648649       24.657534 32.727273

--- Nour vs Qwen ---
label  Nour_count  Qwen_count  agree  prec(Qwen→Nour)  rec(Nour→Qwen)        F1
   TP         191         213    174        81.690141       91.099476 86.138614
   FP          48          26      9        34.615385       18.750000 24.324324

--- Nour vs Jais ---
label  Nour_count  Jais_count  agree  prec(Jais→Nour)  rec(Nour→Jais)        F1
   TP         189         206    167        81.067961       88.359788 84.556962
   FP          54          37     15        40.540541       27.777778 32.967033

--- Qwen vs Jais ---
label  Qwen_count  Jais_count  agree  prec(Jais→Qwen)  rec(Qwen→Jais)        F1
   TP         207         199    183        91.959799       88.405797 90.147783
   FP          26          34     10        29.411765       38.461538 33.333333

============================================================
CONFUSION MATRICES
============================================================

--- Fady (rows) vs Nour (cols) ---
         Nour=TP  Nour=FP
Fady=TP      168        9
Fady=FP       27       50

--- Fady (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Fady=TP      160       14
Fady=FP       57       12

--- Fady (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Fady=TP      153       19
Fady=FP       55       18

--- Nour (rows) vs Qwen (cols) ---
         Qwen=TP  Qwen=FP
Nour=TP      174       17
Nour=FP       39        9

--- Nour (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Nour=TP      167       22
Nour=FP       39       15

--- Qwen (rows) vs Jais (cols) ---
         Jais=TP  Jais=FP
Qwen=TP      183       24
Qwen=FP       16       10

============================================================
ALL FOUR AGREE (n=229): 135 rows = 59.0%

Label breakdown where all four agree:
fady
TP    129
FP      6
Name: count, dtype: int64

Top disagreement patterns (fady / nour / qwen / jais):
fady  nour  qwen  jais
FP    FP    TP    TP      23
      TP    TP    TP      20
TP    TP    TP    FP      16
            FP    TP      12
      FP    TP    TP       7
FP    FP    TP    FP       6
            FP    TP       3
      TP    FP    FP       2
            TP    FP       2
TP    TP    FP    FP       2
FP    TP    FP    TP       1
Name: count, dtype: int64
