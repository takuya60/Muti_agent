# 缺失值处理

- 知识点：缺失率、删除、均值插补、中位数插补、众数插补、SimpleImputer、训练集 fit

缺失值是表格机器学习中最常见的问题之一。处理缺失值不能简单地“一律删除”或“一律填 0”，而要先看缺失比例、字段类型和缺失原因。数值字段常见做法是均值或中位数插补；类别字段常见做法是众数插补或增加“Unknown”类别；缺失比例过高且业务价值低的字段可以考虑删除。

实操中推荐使用 sklearn 的 `SimpleImputer`，并把它放进 Pipeline。关键原则是：插补器只能在训练集上 `fit`，然后对验证集和测试集 `transform`。如果先对全量数据计算均值再划分训练/测试，就会把测试集分布信息泄漏给训练过程。

```python
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

imputer = SimpleImputer(strategy='median')
X_train_imp = imputer.fit_transform(X_train)
X_test_imp = imputer.transform(X_test)
```

教学要点：缺失值处理是“数据预处理”的一部分，不是模型训练之后才做。对于不同字段应采用不同策略，尤其要区分数值和类别变量。

审核规则：
- 不允许 `imputer.fit_transform(X)` 后再切分数据。
- 应说明缺失率和插补策略。
- 类别变量不要用数值均值插补。
