# 数值缩放：标准化与归一化

- 知识点：StandardScaler、MinMaxScaler、距离模型、梯度优化、Pipeline

数值缩放是把不同量纲的特征调整到可比较范围。标准化通常把特征变成均值为 0、标准差为 1 的分布；归一化常把特征压到 0 到 1。KNN、SVM、逻辑回归、线性回归（带正则）、神经网络等模型通常需要缩放，因为它们受特征尺度影响较大。决策树和随机森林对单调缩放不敏感，一般不强制要求。

标准化必须只在训练集上 `fit`，再对验证集/测试集 `transform`。最推荐把缩放器放入 Pipeline，尤其在交叉验证中可以避免数据泄漏。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=1000))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
```

教学类比：标准化像是把身高、收入、年龄放到同一个比较尺度上，否则收入这种数值大的变量会在距离或梯度中“声音更大”。

审核规则：
- 禁止 `StandardScaler().fit_transform(X)` 后再切分数据。
- 交叉验证时必须把 scaler 放进 Pipeline。
- 应说明哪些模型需要缩放，哪些模型不敏感。
