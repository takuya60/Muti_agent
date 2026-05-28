# 决策树剪枝与复杂度控制

- 知识点：max_depth、min_samples_leaf、min_samples_split、剪枝、过拟合

决策树最大的风险是过拟合。如果不加限制，树可以不断细分训练样本，甚至记住噪声。复杂度控制的目标是让树足够表达规律，但不要过度记忆训练集。

常见参数包括：`max_depth` 限制最大深度；`min_samples_leaf` 限制叶子节点最少样本数；`min_samples_split` 限制继续分裂所需的最少样本数；`ccp_alpha` 可用于代价复杂度剪枝。

```python
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier

params = {
    'max_depth': [2, 3, 5, None],
    'min_samples_leaf': [1, 5, 10]
}
search = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    params,
    cv=5,
    scoring='f1'
)
search.fit(X_train, y_train)
print(search.best_params_)
```

教学要点：剪枝不是让树“变弱”，而是让它更像总结规律，而不是背答案。可以通过比较训练集和验证集分数来观察过拟合。

审核规则：
- 决策树示例不应默认无限深度后直接报告好结果。
- 参数选择应通过验证集或交叉验证。
- 可视化树时要注意深度过大导致图不可读。
