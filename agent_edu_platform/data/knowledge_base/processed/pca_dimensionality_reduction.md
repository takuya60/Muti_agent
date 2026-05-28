# PCA 降维

- 知识点：主成分分析、方差最大方向、explained_variance_ratio_、可视化、压缩

PCA 是一种常见降维方法，它寻找能够保留数据最大方差信息的新方向，把高维特征投影到低维空间。PCA 常用于可视化、压缩、去噪和缓解特征冗余。它是无监督方法，不使用标签。

PCA 对特征尺度敏感，因此通常要先标准化。否则数值范围大的特征会主导主成分方向。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=2))
])
X_2d = pipeline.fit_transform(X)

pca = pipeline.named_steps['pca']
print(pca.explained_variance_ratio_)
```

教学要点：PCA 不是简单删除列，而是生成新的组合特征。`explained_variance_ratio_` 可以告诉我们每个主成分保留了多少信息。

审核规则：
- PCA 前通常需要标准化。
- PCA 是无监督降维，不应说它直接“提高分类准确率”。
- 在交叉验证中 PCA 应放进 Pipeline，避免泄漏。
