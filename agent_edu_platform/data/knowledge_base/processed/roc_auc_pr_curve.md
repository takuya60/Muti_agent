# ROC-AUC 与 PR 曲线

- 知识点：ROC、AUC、PR曲线、阈值、类别不平衡、排序能力

分类模型通常先输出概率，再根据阈值转成类别。ROC 曲线展示不同阈值下 TPR 和 FPR 的关系，AUC 可以理解为模型把正样本排在负样本前面的能力。PR 曲线展示 Precision 和 Recall 的权衡，在类别极不平衡时通常比 ROC 更有参考价值。

```python
from sklearn.metrics import roc_auc_score, average_precision_score

prob = model.predict_proba(X_test)[:, 1]
print(roc_auc_score(y_test, prob))
print(average_precision_score(y_test, prob))
```

AUC 高不代表默认阈值 0.5 下的业务效果一定好。实际应用中，阈值应结合业务成本调整：医疗筛查可能更看重召回率，垃圾短信过滤可能更看重精确率。

教学要点：ROC-AUC 评价的是排序能力，不直接告诉你最终阈值应该是多少。PR 曲线尤其适合正类稀少的场景。

审核规则：
- 不应只报告 AUC 而不报告类别分布。
- 不平衡数据建议补充 PR-AUC 或 Precision/Recall/F1。
- 阈值选择不能用测试集反复调。
