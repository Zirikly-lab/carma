## post level
Loading preprocessed posts …
Loading split manifest …
  9,149 users with posts, 7,467 users in manifest, 13 conditions

adhd: 643 pos users, train=130154 posts, test=17313 posts
  NB: F1=0.738  Acc=0.590  P=0.602  R=0.951
  LR: F1=0.733  Acc=0.592  P=0.608  R=0.921
  SVM: F1=0.724  Acc=0.590  P=0.612  R=0.885
  XGB: F1=0.751  Acc=0.603  P=0.607  R=0.984

anxiety: 644 pos users, train=128584 posts, test=12511 posts
  NB: F1=0.819  Acc=0.696  P=0.714  R=0.960
  LR: F1=0.798  Acc=0.676  P=0.721  R=0.894
  SVM: F1=0.782  Acc=0.659  P=0.721  R=0.853
  XGB: F1=0.828  Acc=0.709  P=0.717  R=0.979

autism: 227 pos users, train=42839 posts, test=4974 posts
  NB: F1=0.792  Acc=0.659  P=0.665  R=0.978
  LR: F1=0.771  Acc=0.642  P=0.669  R=0.910
  SVM: F1=0.736  Acc=0.619  P=0.681  R=0.799
  XGB: F1=0.778  Acc=0.639  P=0.657  R=0.953

bipolar: 76 pos users, train=10570 posts, test=3227 posts
  NB: F1=0.883  Acc=0.791  P=0.792  R=0.998
  LR: F1=0.874  Acc=0.778  P=0.793  R=0.975
  SVM: F1=0.803  Acc=0.682  P=0.790  R=0.816
  XGB: F1=0.871  Acc=0.772  P=0.789  R=0.971

bpd: 98 pos users, train=16178 posts, test=1660 posts
  NB: F1=0.863  Acc=0.778  P=0.808  R=0.927
  LR: F1=0.825  Acc=0.729  P=0.804  R=0.849
  SVM: F1=0.765  Acc=0.661  P=0.802  R=0.731
  XGB: F1=0.858  Acc=0.769  P=0.799  R=0.927

depression: 1831 pos users, train=351102 posts, test=37621 posts
  NB: F1=0.807  Acc=0.679  P=0.681  R=0.992
  LR: F1=0.791  Acc=0.667  P=0.690  R=0.926
  SVM: F1=0.787  Acc=0.664  P=0.690  R=0.917
  XGB: F1=0.808  Acc=0.680  P=0.681  R=0.994

eating_disorder: 41 pos users, train=7515 posts, test=1709 posts
  NB: F1=0.773  Acc=0.651  P=0.801  R=0.746
  LR: F1=0.761  Acc=0.642  P=0.811  R=0.716
  SVM: F1=0.745  Acc=0.628  P=0.819  R=0.683
  XGB: F1=0.789  Acc=0.667  P=0.795  R=0.783

ocd: 311 pos users, train=59031 posts, test=8114 posts
  NB: F1=0.746  Acc=0.612  P=0.716  R=0.778
  LR: F1=0.716  Acc=0.597  P=0.740  R=0.692
  SVM: F1=0.683  Acc=0.570  P=0.742  R=0.633
  XGB: F1=0.797  Acc=0.672  P=0.728  R=0.882

panic: 147 pos users, train=31197 posts, test=1761 posts
  NB: F1=0.825  Acc=0.734  P=0.767  R=0.892
  LR: F1=0.824  Acc=0.727  P=0.754  R=0.909
  SVM: F1=0.804  Acc=0.711  P=0.770  R=0.841
  XGB: F1=0.818  Acc=0.717  P=0.747  R=0.903

ptsd: 92 pos users, train=23545 posts, test=1660 posts
  NB: F1=0.665  Acc=0.550  P=0.514  R=0.944
  LR: F1=0.665  Acc=0.567  P=0.525  R=0.906
  SVM: F1=0.632  Acc=0.559  P=0.523  R=0.798
  XGB: F1=0.655  Acc=0.539  P=0.507  R=0.924

schizophrenia: 45 pos users, train=9606 posts, test=896 posts
  NB: F1=0.956  Acc=0.915  P=0.917  R=0.998
  LR: F1=0.949  Acc=0.903  P=0.922  R=0.977
  SVM: F1=0.875  Acc=0.782  P=0.919  R=0.835
  XGB: F1=0.943  Acc=0.892  P=0.915  R=0.972

sleep_disorder: 357 pos users, train=85063 posts, test=8865 posts
  NB: F1=0.810  Acc=0.684  P=0.686  R=0.988
  LR: F1=0.781  Acc=0.655  P=0.688  R=0.903
  SVM: F1=0.752  Acc=0.629  P=0.690  R=0.827
  XGB: F1=0.802  Acc=0.671  P=0.680  R=0.976

suicidal: 80 pos users, train=16112 posts, test=1766 posts
  NB: F1=0.861  Acc=0.772  P=0.786  R=0.953
  LR: F1=0.855  Acc=0.764  P=0.786  R=0.936
  SVM: F1=0.813  Acc=0.715  P=0.792  R=0.835
  XGB: F1=0.864  Acc=0.776  P=0.784  R=0.963

Results saved to results/classical.csv

Best F1 per condition:
      condition model     f1
           adhd   XGB 0.7506
        anxiety   XGB 0.8279
         autism    NB 0.7917
        bipolar    NB 0.8833
            bpd    NB 0.8634
     depression   XGB 0.8082
eating_disorder   XGB 0.7889
            ocd   XGB 0.7974
          panic    NB 0.8249
           ptsd    NB 0.6655
  schizophrenia    NB 0.9556
 sleep_disorder    NB 0.8100
       suicidal   XGB 0.8642



## user level
Loading preprocessed posts …
Loading split manifest …
  9,149 users with posts, 7,467 users in manifest, 13 conditions

adhd (user-level): train=1156 (578 pos), test=130 (65 pos)
  NB: F1=0.576  Acc=0.615  P=0.641  R=0.523
  LR: F1=0.667  Acc=0.654  P=0.643  R=0.692
  SVM: F1=0.662  Acc=0.646  P=0.634  R=0.692
  XGB: F1=0.721  Acc=0.685  P=0.646  R=0.815

anxiety (user-level): train=1158 (579 pos), test=130 (65 pos)
  NB: F1=0.661  Acc=0.669  P=0.677  R=0.646
  LR: F1=0.744  Acc=0.761  P=0.804  R=0.692
  SVM: F1=0.797  Acc=0.808  P=0.845  R=0.754
  XGB: F1=0.850  Acc=0.862  P=0.927  R=0.785

autism (user-level): train=408 (204 pos), test=46 (23 pos)
  NB: F1=0.784  Acc=0.761  P=0.714  R=0.870
  LR: F1=0.792  Acc=0.783  P=0.760  R=0.826
  SVM: F1=0.783  Acc=0.783  P=0.783  R=0.783
  XGB: F1=0.884  Acc=0.891  P=0.950  R=0.826

bipolar (user-level): train=136 (68 pos), test=16 (8 pos)
  NB: F1=0.571  Acc=0.438  P=0.462  R=0.750
  LR: F1=0.526  Acc=0.438  P=0.455  R=0.625
  SVM: F1=0.556  Acc=0.500  P=0.500  R=0.625
  XGB: F1=0.588  Acc=0.562  P=0.556  R=0.625

bpd (user-level): train=176 (88 pos), test=20 (10 pos)
  NB: F1=0.720  Acc=0.650  P=0.600  R=0.900
  LR: F1=0.556  Acc=0.600  P=0.625  R=0.500
  SVM: F1=0.600  Acc=0.600  P=0.600  R=0.600
  XGB: F1=0.571  Acc=0.550  P=0.545  R=0.600

depression (user-level): train=3294 (1647 pos), test=368 (184 pos)
  NB: F1=0.488  Acc=0.606  P=0.697  R=0.375
  LR: F1=0.676  Acc=0.677  P=0.678  R=0.674
  SVM: F1=0.674  Acc=0.663  P=0.653  R=0.696
  XGB: F1=0.683  Acc=0.682  P=0.681  R=0.685

eating_disorder (user-level): train=72 (36 pos), test=10 (5 pos)
  NB: F1=0.500  Acc=0.400  P=0.429  R=0.600
  LR: F1=0.667  Acc=0.600  P=0.571  R=0.800
  SVM: F1=0.727  Acc=0.700  P=0.667  R=0.800
  XGB: F1=0.500  Acc=0.400  P=0.429  R=0.600

ocd (user-level): train=558 (279 pos), test=64 (32 pos)
  NB: F1=0.594  Acc=0.594  P=0.594  R=0.594
  LR: F1=0.739  Acc=0.734  P=0.727  R=0.750
  SVM: F1=0.742  Acc=0.750  P=0.767  R=0.719
  XGB: F1=0.821  Acc=0.844  P=0.958  R=0.719

panic (user-level): train=264 (132 pos), test=30 (15 pos)
  NB: F1=0.722  Acc=0.667  P=0.619  R=0.867
  LR: F1=0.812  Acc=0.800  P=0.765  R=0.867
  SVM: F1=0.909  Acc=0.900  P=0.833  R=1.000
  XGB: F1=0.788  Acc=0.767  P=0.722  R=0.867

ptsd (user-level): train=164 (82 pos), test=20 (10 pos)
  NB: F1=0.700  Acc=0.700  P=0.700  R=0.700
  LR: F1=0.444  Acc=0.500  P=0.500  R=0.400
  SVM: F1=0.667  Acc=0.650  P=0.636  R=0.700
  XGB: F1=0.500  Acc=0.500  P=0.500  R=0.500

schizophrenia (user-level): train=80 (40 pos), test=10 (5 pos)
  NB: F1=0.769  Acc=0.700  P=0.625  R=1.000
  LR: F1=0.909  Acc=0.900  P=0.833  R=1.000
  SVM: F1=0.833  Acc=0.800  P=0.714  R=1.000
  XGB: F1=0.600  Acc=0.600  P=0.600  R=0.600

sleep_disorder (user-level): train=642 (321 pos), test=72 (36 pos)
  NB: F1=0.765  Acc=0.778  P=0.812  R=0.722
  LR: F1=0.754  Acc=0.764  P=0.788  R=0.722
  SVM: F1=0.771  Acc=0.778  P=0.794  R=0.750
  XGB: F1=0.886  Acc=0.889  P=0.912  R=0.861

suicidal (user-level): train=144 (72 pos), test=16 (8 pos)
  NB: F1=0.667  Acc=0.562  P=0.538  R=0.875
  LR: F1=0.706  Acc=0.688  P=0.667  R=0.750
  SVM: F1=0.824  Acc=0.812  P=0.778  R=0.875
  XGB: F1=0.750  Acc=0.750  P=0.750  R=0.750

Results saved to results/classical_user.csv

Best F1 per condition:
      condition model     f1
           adhd   XGB 0.7211
        anxiety   XGB 0.8500
         autism   XGB 0.8837
        bipolar   XGB 0.5882
            bpd    NB 0.7200
     depression   XGB 0.6829
eating_disorder   SVM 0.7273
            ocd   XGB 0.8214
          panic   SVM 0.9091
           ptsd    NB 0.7000
  schizophrenia    LR 0.9091
 sleep_disorder   XGB 0.8857
       suicidal   SVM 0.8235