# 决策树

- 知识点：规则划分、信息增益、基尼指数、CART、可解释性、过拟合

决策树通过一系列“如果-那么”的条件划分样本。例如先按年龄是否大于 30 切分，再按收入是否大于某个阈值切分，最终每个叶子节点给出预测类别或数值。决策树的优点是直观、可解释、能处理非线性关系；缺点是容易过拟合，对数据扰动比较敏感。

分类树常见划分标准包括信息增益、增益率和基尼指数。sklearn 中 `DecisionTreeClassifier` 默认使用基尼指数，也可以设置 `criterion='entropy'`。

```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))

plt.figure(figsize=(12, 6))
plot_tree(model, feature_names=feature_names, class_names=class_names, filled=True)
```

教学要点：决策树适合作为从线性模型过渡到非线性模型的第一站。它也能帮助学生理解模型解释性和过拟合之间的权衡。

易错点：
- 不限制深度的树容易训练集接近满分，但测试集很差。
- 特征重要性不等于因果关系。
- 树模型不要求标准化，但仍需要处理缺失值和类别编码。
