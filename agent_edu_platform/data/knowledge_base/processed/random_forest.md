# 随机森林

- 知识点：Bagging、集成学习、决策树、特征随机性、泛化能力

随机森林是多个决策树组成的集成模型。每棵树在不同的样本子集和特征子集上训练，最后通过投票或平均得到结果。相比单棵决策树，随机森林通常更稳定、泛化能力更强，不容易因为单次划分或局部噪声而剧烈波动。

随机森林的核心思想是“多个不完全相同的弱模型共同决策”。每棵树可能有偏差，但通过集成可以降低方差。常见参数包括 `n_estimators`、`max_depth`、`min_samples_leaf` 和 `max_features`。

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(model.feature_importances_)
```

教学要点：随机森林适合作为决策树后的进阶分支。它通常是表格数据的强基线模型，但可解释性不如单棵树直观。

审核规则：
- 不应只报告训练集分数。
- 特征重要性只能说明模型使用程度，不等于因果关系。
- 类别不平衡时可考虑 `class_weight` 或重采样。
