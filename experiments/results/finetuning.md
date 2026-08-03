## post level
((.venv) ) [g21775526@gpu033 experiments]$ python3 finetune.py --model arabert
Device: cuda
GPU: Tesla V100-SXM2-16GB
Loading preprocessed posts …
Loading split manifest …
  9,149 users with posts, 7,467 users in manifest, 13 conditions

==================================================
Model: arabert  Condition: adhd  Level: post

  adhd (post-level): train=130154 (94336 pos), test=17313 (10501 pos)
Loading weights: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:01<00:00, 144.70it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5324  F1=0.747  Acc=0.622
    epoch 2: loss=0.4470  F1=0.727  Acc=0.611
    epoch 3: loss=0.3242  F1=0.701  Acc=0.597

==================================================
Model: arabert  Condition: anxiety  Level: post

  anxiety (post-level): train=128584 (87060 pos), test=12511 (8952 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3173.10it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5773  F1=0.766  Acc=0.643
    epoch 2: loss=0.4832  F1=0.766  Acc=0.641
    epoch 3: loss=0.3583  F1=0.741  Acc=0.616

==================================================
Model: arabert  Condition: autism  Level: post

  autism (post-level): train=42839 (30584 pos), test=4974 (3295 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3652.07it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5160  F1=0.771  Acc=0.653
    epoch 2: loss=0.4009  F1=0.780  Acc=0.650
    epoch 3: loss=0.2552  F1=0.773  Acc=0.662

==================================================
Model: arabert  Condition: bipolar  Level: post

  bipolar (post-level): train=10570 (7422 pos), test=3227 (2557 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 4112.55it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5153  F1=0.841  Acc=0.734
    epoch 2: loss=0.3249  F1=0.768  Acc=0.647
    epoch 3: loss=0.1379  F1=0.837  Acc=0.730

==================================================
Model: arabert  Condition: bpd  Level: post

  bpd (post-level): train=16178 (10321 pos), test=1660 (1254 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3966.48it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.4973  F1=0.847  Acc=0.766
    epoch 2: loss=0.3187  F1=0.784  Acc=0.692
    epoch 3: loss=0.1571  F1=0.799  Acc=0.711

==================================================
Model: arabert  Condition: depression  Level: post

  depression (post-level): train=351102 (239687 pos), test=37621 (25538 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3867.71it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5898  F1=0.796  Acc=0.680
    epoch 2: loss=0.5231  F1=0.784  Acc=0.667
    epoch 3: loss=0.4312  F1=0.743  Acc=0.631

==================================================
Model: arabert  Condition: eating_disorder  Level: post

  eating_disorder (post-level): train=7515 (4436 pos), test=1709 (1358 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3208.58it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.4240  F1=0.731  Acc=0.593
    epoch 2: loss=0.2219  F1=0.701  Acc=0.555
    epoch 3: loss=0.0855  F1=0.748  Acc=0.614

==================================================
Model: arabert  Condition: ocd  Level: post

  ocd (post-level): train=59031 (36384 pos), test=8114 (5943 pos)
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 197/197 [00:00<00:00, 3111.79it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | Details
-------------------------------------------+------------+--------
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED |        
cls.predictions.bias                       | UNEXPECTED |        
cls.predictions.transform.dense.weight     | UNEXPECTED |        
cls.predictions.transform.LayerNorm.weight | UNEXPECTED |        
cls.predictions.transform.dense.bias       | UNEXPECTED |        
classifier.bias                            | MISSING    |        
bert.pooler.dense.weight                   | MISSING    |        
classifier.weight                          | MISSING    |        
bert.pooler.dense.bias                     | MISSING    |        

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5813  F1=0.655  Acc=0.545
    epoch 2: loss=0.4324  F1=0.709  Acc=0.605


    epoch 3: loss=0.2631  F1=0.694  Acc=0.597

==================================================
Model: arabert  Condition: panic  Level: post

  panic (post-level): train=31197 (21890 pos), test=1761 (1239 pos)
Loading weights: 100%|██████████████████████| 197/197 [00:00<00:00, 3346.11it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | 
-------------------------------------------+------------+-
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED | 
cls.predictions.bias                       | UNEXPECTED | 
cls.predictions.transform.dense.weight     | UNEXPECTED | 
cls.predictions.transform.LayerNorm.weight | UNEXPECTED | 
cls.predictions.transform.dense.bias       | UNEXPECTED | 
classifier.bias                            | MISSING    | 
bert.pooler.dense.weight                   | MISSING    | 
classifier.weight                          | MISSING    | 
bert.pooler.dense.bias                     | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.4156  F1=0.839  Acc=0.773

    epoch 2: loss=0.2690  F1=0.851  Acc=0.777
    epoch 3: loss=0.1326  F1=0.830  Acc=0.752

==================================================
Model: arabert  Condition: ptsd  Level: post

  ptsd (post-level): train=23545 (15914 pos), test=1660 (787 pos)
Loading weights: 100%|██████████████████████| 197/197 [00:00<00:00, 3663.96it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | 
-------------------------------------------+------------+-
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED | 
cls.predictions.bias                       | UNEXPECTED | 
cls.predictions.transform.dense.weight     | UNEXPECTED | 
cls.predictions.transform.LayerNorm.weight | UNEXPECTED | 
cls.predictions.transform.dense.bias       | UNEXPECTED | 
classifier.bias                            | MISSING    | 
bert.pooler.dense.weight                   | MISSING    | 
classifier.weight                          | MISSING    | 
bert.pooler.dense.bias                     | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5010  F1=0.660  Acc=0.641
    epoch 2: loss=0.3423  F1=0.677  Acc=0.675
    epoch 3: loss=0.1594  F1=0.652  Acc=0.648

==================================================
Model: arabert  Condition: schizophrenia  Level: post

  schizophrenia (post-level): train=9606 (7256 pos), test=896 (820 pos)
Loading weights: 100%|███████████████████████| 197/197 [00:01<00:00, 130.54it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | 
-------------------------------------------+------------+-
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED | 
cls.predictions.bias                       | UNEXPECTED | 
cls.predictions.transform.dense.weight     | UNEXPECTED | 
cls.predictions.transform.LayerNorm.weight | UNEXPECTED | 
cls.predictions.transform.dense.bias       | UNEXPECTED | 
classifier.bias                            | MISSING    | 
bert.pooler.dense.weight                   | MISSING    | 
classifier.weight                          | MISSING    | 
bert.pooler.dense.bias                     | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.4382  F1=0.828  Acc=0.712
    epoch 2: loss=0.2461  F1=0.814  Acc=0.692
    epoch 3: loss=0.0934  F1=0.875  Acc=0.781

==================================================
Model: arabert  Condition: sleep_disorder  Level: post

  sleep_disorder (post-level): train=85063 (57977 pos), test=8865 (6039 pos)
Loading weights: 100%|██████████████████████| 197/197 [00:00<00:00, 4762.82it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | 
-------------------------------------------+------------+-
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED | 
cls.predictions.bias                       | UNEXPECTED | 
cls.predictions.transform.dense.weight     | UNEXPECTED | 
cls.predictions.transform.LayerNorm.weight | UNEXPECTED | 
cls.predictions.transform.dense.bias       | UNEXPECTED | 
classifier.bias                            | MISSING    | 
bert.pooler.dense.weight                   | MISSING    | 
classifier.weight                          | MISSING    | 
bert.pooler.dense.bias                     | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.5618  F1=0.766  Acc=0.636
    epoch 2: loss=0.4307  F1=0.770  Acc=0.640
    epoch 3: loss=0.2814  F1=0.777  Acc=0.655

==================================================
Model: arabert  Condition: suicidal  Level: post

  suicidal (post-level): train=16112 (11228 pos), test=1766 (1309 pos)
Loading weights: 100%|██████████████████████| 197/197 [00:00<00:00, 7319.71it/s]
[transformers] BertForSequenceClassification LOAD REPORT from: aubmindlab/bert-base-arabertv02-twitter
Key                                        | Status     | 
-------------------------------------------+------------+-
cls.predictions.transform.LayerNorm.bias   | UNEXPECTED | 
cls.predictions.bias                       | UNEXPECTED | 
cls.predictions.transform.dense.weight     | UNEXPECTED | 
cls.predictions.transform.LayerNorm.weight | UNEXPECTED | 
cls.predictions.transform.dense.bias       | UNEXPECTED | 
classifier.bias                            | MISSING    | 
bert.pooler.dense.weight                   | MISSING    | 
classifier.weight                          | MISSING    | 
bert.pooler.dense.bias                     | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
    epoch 1: loss=0.4392  F1=0.865  Acc=0.788
    epoch 2: loss=0.2795  F1=0.866  Acc=0.788
    epoch 3: loss=0.1296  F1=0.790  Acc=0.686

Results saved to results/finetune_arabert_post.csv
      condition level   model     f1  accuracy  precision  recall
           adhd  post arabert 0.7470    0.6218     0.6286  0.9202
        anxiety  post arabert 0.7662    0.6434     0.7216  0.8167
         autism  post arabert 0.7797    0.6498     0.6684  0.9354
        bipolar  post arabert 0.8406    0.7344     0.8014  0.8838
            bpd  post arabert 0.8469    0.7657     0.8361  0.8581
     depression  post arabert 0.7957    0.6799     0.7020  0.9182
eating_disorder  post arabert 0.7481    0.6138     0.7765  0.7216
            ocd  post arabert 0.7088    0.6053     0.7709  0.6561
          panic  post arabert 0.8514    0.7774     0.8027  0.9064
           ptsd  post arabert 0.6770    0.6747     0.6395  0.7192
  schizophrenia  post arabert 0.8750    0.7812     0.9171  0.8366
 sleep_disorder  post arabert 0.7769    0.6553     0.6948  0.8809
       suicidal  post arabert 0.8659    0.7882     0.8161  0.9221
