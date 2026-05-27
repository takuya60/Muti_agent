# 阈值调整 (Threshold Tuning)

- 知识点：分类阈值、PR 曲线、ROC 曲线

`LogisticRegression` 默认阈值为 0.5。如果需要提高召回率（宁杀错不放过），可以降低阈值（如 0.3）；如果需要提高精准率，可以提高阈值。这可以通过 `predict_proba` 输出概率后手动判定来实现。
