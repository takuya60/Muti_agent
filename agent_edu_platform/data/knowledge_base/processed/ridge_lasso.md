# Ridge 与 Lasso 正则化回归

- 知识点：L2正则、L1正则、alpha、系数收缩、特征选择、过拟合控制

Ridge 和 Lasso 都是在普通线性回归基础上加入正则化约束，用于控制模型复杂度、缓解过拟合。Ridge 使用 L2 正则，会把系数整体缩小，但通常不会变成 0；Lasso 使用 L1 正则，有可能把一些系数压到 0，因此也可以作为特征选择方法。

正则化强度由 `alpha` 控制。`alpha` 太小，模型接近普通线性回归；`alpha` 太大，模型可能过度约束而欠拟合。实际项目中应通过验证集或交叉验证选择 alpha。

```python
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import GridSearchCV

params = {'alpha': [0.01, 0.1, 1, 10, 100]}
model = GridSearchCV(Ridge(), params, cv=5, scoring='neg_root_mean_squared_error')
model.fit(X_train, y_train)
print(model.best_params_)
```

教学要点：正则化不是“让训练分数更高”，而是牺牲一点训练集拟合能力，换取更好的泛化能力。它和过拟合诊断、验证曲线密切相关。

审核规则：
- alpha 不能凭感觉随便写，应有验证依据。
- 正则化模型通常需要标准化，否则不同尺度特征受到的惩罚不公平。
- Lasso 系数为 0 不代表变量在业务上绝对无用，只代表当前数据和模型下贡献弱。
