# KNN 分类

- 知识点：K近邻、距离度量、特征缩放、k值、懒惰学习

KNN 是一种直观的分类算法：预测一个新样本时，找到训练集中离它最近的 k 个样本，由这些邻居投票决定类别。它没有显式训练参数，更多是在预测时计算距离，因此也被称为“懒惰学习”。

KNN 对特征尺度非常敏感。如果一个特征是年龄，另一个特征是收入，收入数值范围更大，会主导距离计算。因此 KNN 前通常必须做标准化或归一化。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier(n_neighbors=5))
])

scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
print(scores.mean())
```

教学要点：KNN 适合说明“距离”和“特征尺度”的重要性。k 太小容易受噪声影响，k 太大可能把局部结构抹平，因此 k 应通过验证集或交叉验证选择。

审核规则：
- KNN 必须强调特征缩放。
- k 值不应随意固定，应比较多个候选。
- 高维数据中距离可能失效，需谨慎解释。
