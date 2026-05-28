# 多项式回归

- 知识点：非线性关系、PolynomialFeatures、线性模型扩展、过拟合、正则化

多项式回归并不是换了一个全新的模型，而是通过构造多项式特征，让线性模型能够拟合非线性关系。例如原始特征只有 $x$，加入 $x^2$、$x^3$ 后，模型仍然对新特征做线性组合，但整体曲线可以变弯。

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

model = Pipeline([
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('reg', LinearRegression())
])

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

多项式特征会快速增加特征数量，阶数越高越容易过拟合。因此多项式回归常常需要配合 Ridge 或 Lasso 正则化，并用验证集或交叉验证选择 degree。

教学要点：多项式回归适合说明“特征工程可以增强模型表达能力”。它也能让学习者理解：复杂度提高不一定带来泛化提升。

审核规则：
- 不应盲目使用高阶多项式。
- degree 应通过验证集或交叉验证选择。
- 多项式特征通常应配合标准化和正则化。
