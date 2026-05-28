# GBDT 与 XGBoost 思想

- 知识点：Boosting、梯度提升、残差拟合、弱学习器、表格数据强模型

GBDT 是梯度提升决策树。与随机森林并行训练多棵树不同，GBDT 是一棵接一棵地训练：后一棵树重点修正前面模型的错误。可以把它理解为不断学习“还没解释好的残差”。XGBoost、LightGBM、CatBoost 都是在梯度提升思想上的高效实现。

GBDT 系列模型在表格数据上非常强，但参数较多，也更容易因为调参不当产生过拟合。常见参数包括树数量、学习率、树深、子采样比例和正则化项。

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
print(scores.mean())
```

教学要点：GBDT 适合作为表格数据建模进阶内容。初学者应先理解决策树和随机森林，再学习 Boosting。

审核规则：
- 不应在入门阶段直接跳到 XGBoost 而不解释树和 Boosting。
- 需要验证集或交叉验证选择参数。
- 学习率和树数量应配合调整。
