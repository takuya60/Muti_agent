# 类别变量编码

- 知识点：类别变量、One-Hot 编码、Ordinal 编码、ColumnTransformer、线性模型、树模型

机器学习模型通常只能处理数值输入，因此类别变量需要编码。最常见方法是 One-Hot 编码，它把一个类别字段拆成多个 0/1 特征。例如颜色字段 red/blue/green 会变成 is_red、is_blue、is_green。对于逻辑回归、线性回归、KNN、SVM 等模型，One-Hot 通常比简单地把类别映射成 0、1、2 更安全，因为数字大小会引入不存在的顺序关系。

对于确实有顺序的变量，如“低/中/高”，可以使用 Ordinal 编码。对于树模型，一些简单整数编码有时也能工作，但仍需要谨慎解释。

推荐用 `ColumnTransformer` 把数值预处理和类别编码放在同一个 Pipeline 里。

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric_features = ['age', 'income']
categorical_features = ['city', 'gender']

preprocess = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
])
```

易错点：
- 不能对训练集和测试集分别 `get_dummies` 后不对齐列。
- 线上预测可能出现训练时没见过的新类别，应使用 `handle_unknown='ignore'`。
- 对无序类别直接编码为 0/1/2，可能误导线性模型。
