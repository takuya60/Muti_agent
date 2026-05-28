# 特征构造与筛选

- 知识点：特征工程、比率特征、交叉特征、多项式特征、相关性、特征重要性、L1筛选

特征工程是把原始数据转化为更适合模型学习的表达。一个简单模型如果有好的特征，往往比复杂模型直接吃原始字段效果更稳定。常见特征构造包括：比率特征、差值特征、时间特征、分箱特征、交叉特征和多项式特征。例如在电商数据中，`购买金额 / 浏览次数` 可能比单独的金额和浏览次数更能反映购买意愿。

特征筛选的目标是去掉无意义、冗余或泄漏字段。常用方法包括相关性分析、方差过滤、基于模型的特征重要性、L1 正则化筛选、树模型重要性等。筛选特征时要注意：筛选规则必须在训练集上确定，不能先看全量数据再选择特征，否则会产生数据泄漏。

实操示例：

```python
# 构造比率特征
df['spend_per_visit'] = df['total_spend'] / (df['visit_count'] + 1)

# 相关性筛选示例
corr = df.corr(numeric_only=True)['target'].abs().sort_values(ascending=False)
print(corr.head(10))

# 多项式特征
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_train)
```

教学要点：特征工程不是“越多越好”，而是让特征更接近任务目标。新增特征后要通过验证集或交叉验证判断是否真的提升效果。

审核规则：
- 不允许使用标签或未来信息构造特征。
- 特征筛选必须放在训练流程内，最好使用 Pipeline。
- 多项式和交叉特征容易增加过拟合风险，通常需要配合正则化。
