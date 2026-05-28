# DBSCAN 聚类

- 知识点：密度聚类、eps、min_samples、噪声点、非球状簇

DBSCAN 是基于密度的聚类方法。它不需要提前指定簇数量，而是通过 `eps` 和 `min_samples` 定义“密度足够高”的区域。DBSCAN 可以发现非球状簇，并能把孤立样本识别为噪声点。

核心参数中，`eps` 表示邻域半径，`min_samples` 表示形成核心点所需的最少邻居数。参数过小会产生大量噪声点，过大会把多个簇合并。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('dbscan', DBSCAN(eps=0.5, min_samples=5))
])
labels = pipeline.fit_predict(X)
print(set(labels))  # -1 表示噪声点
```

教学要点：DBSCAN 适合讲解“不是所有聚类都必须指定 k”。它也适合处理存在噪声和非球状结构的数据。

审核规则：
- 需要解释 `-1` 噪声标签。
- 参数选择不能随意，应结合距离分布或可视化。
- 高维数据中密度概念可能变差，需要谨慎使用。
