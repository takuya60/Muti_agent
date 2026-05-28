# 交叉熵损失

- 知识点：分类损失、log loss、概率预测、二分类、多分类

分类模型不仅要输出类别，也常常输出属于某个类别的概率。交叉熵损失用于衡量预测概率和真实标签之间的差距。以二分类为例，如果真实标签是 1，而模型给正类概率 0.9，损失很小；如果只给 0.1，损失会很大。

二分类交叉熵可写为：

$$L = -y\log(p) - (1-y)\log(1-p)$$

其中 $p$ 是模型预测为正类的概率。逻辑回归通常使用 Sigmoid 输出概率，再用交叉熵作为训练目标。相比 MSE，交叉熵更适合分类概率建模。

实操中 sklearn 的 `LogisticRegression` 已经封装了优化过程，初学者不必手写损失函数，但需要理解为什么输出概率和阈值很重要。

```python
from sklearn.metrics import log_loss

prob = model.predict_proba(X_test)
print(log_loss(y_test, prob))
```

易错点：
- 分类任务不宜直接用 MSE 作为主要损失理解。
- 概率接近 0 或 1 时，错误预测会被严重惩罚。
- `predict` 输出类别，`predict_proba` 输出概率，二者用途不同。
