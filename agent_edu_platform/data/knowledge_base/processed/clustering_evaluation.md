# 聚类评估与可视化

- 知识点：轮廓系数、Calinski-Harabasz、Davies-Bouldin、二维可视化、业务解释

聚类属于无监督学习，大多数时候没有真实标签，因此不能直接用分类准确率评价。常用内部指标包括轮廓系数、Calinski-Harabasz 指数和 Davies-Bouldin 指数。轮廓系数越高通常表示簇内更紧凑、簇间更分离。

```python
from sklearn.metrics import silhouette_score, calinski_harabasz_score

labels = model.fit_predict(X_scaled)
print(silhouette_score(X_scaled, labels))
print(calinski_harabasz_score(X_scaled, labels))
```

除了指标，还应做可视化和业务解释。高维数据可以先用 PCA 降到二维，再画散点图观察簇结构。

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

X_2d = PCA(n_components=2).fit_transform(X_scaled)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels)
```

教学要点：聚类结果不是“答案”，而是一种探索性发现。最终是否有价值，需要结合业务或后续任务解释。

审核规则：
- 没有真实标签时不要报告 accuracy。
- 指标和可视化应一起使用。
- 聚类标签编号本身没有大小顺序。
