# K-Means 聚类

- 知识点：无监督学习、聚类、簇中心、k值、初始化、轮廓系数

K-Means 是常见聚类算法。它把样本分成 k 个簇，每个簇有一个中心点，算法不断重复“分配样本到最近中心”和“更新中心”两个步骤。K-Means 适合发现球状、距离可分的簇结构。

K-Means 需要提前指定 k。k 的选择可以参考肘部法、轮廓系数或业务需求。由于算法基于距离，特征缩放非常重要。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=3, random_state=42, n_init='auto'))
])
labels = pipeline.fit_predict(X)
print(silhouette_score(X, labels))
```

教学要点：聚类没有真实标签时，不应该用 accuracy 表述效果。应关注簇是否紧凑、是否分离、是否有业务解释。

审核规则：
- K-Means 前应做缩放。
- k 值应有选择依据。
- 不要把聚类标签直接解释成真实类别，除非有外部验证。
