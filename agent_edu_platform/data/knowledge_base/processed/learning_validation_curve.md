# 学习曲线与验证曲线

- 知识点：过拟合、欠拟合、learning_curve、validation_curve、训练分数、验证分数

学习曲线用于观察随着训练样本数量增加，训练分数和验证分数如何变化。如果训练分数很高、验证分数很低，通常是过拟合；如果二者都低，可能是欠拟合；如果增加数据后验证分数持续上升，说明更多数据可能有帮助。

验证曲线用于观察某个超参数变化时模型表现如何。例如决策树的 `max_depth`、正则化模型的 `alpha`、KNN 的 `n_neighbors` 都可以用验证曲线分析。

```python
from sklearn.model_selection import learning_curve, validation_curve

train_sizes, train_scores, val_scores = learning_curve(
    estimator, X, y, cv=5, scoring='accuracy'
)

param_range = [1, 2, 3, 5, 10]
train_scores, val_scores = validation_curve(
    estimator, X, y,
    param_name='max_depth',
    param_range=param_range,
    cv=5,
    scoring='accuracy'
)
```

教学要点：学习曲线和验证曲线能让学生从“调参玄学”转向“诊断问题”。它们不是为了画图好看，而是为了判断模型复杂度、数据量和泛化之间的关系。

审核规则：
- 曲线应基于交叉验证或验证集，而不是测试集。
- 需要同时比较训练分数和验证分数。
- 结论应说明是过拟合、欠拟合还是数据不足。
