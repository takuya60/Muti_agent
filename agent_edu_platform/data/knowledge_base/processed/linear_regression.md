# 线性回归

- 知识点：回归任务、线性关系、最小二乘、MSE、系数解释、残差

线性回归用于预测连续数值，例如房价、销售额、成绩等。它假设目标值可以由多个特征的线性组合近似表示：

$$y \approx w_1x_1 + w_2x_2 + \cdots + b$$

训练线性回归的目标通常是最小化均方误差（MSE），也就是让预测值和真实值之间的平方误差尽可能小。线性回归的优点是简单、可解释，系数可以反映特征对预测值的方向和强度；缺点是表达能力有限，对非线性关系和异常值比较敏感。

实操示例：

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(model.coef_)
print(mean_squared_error(y_test, y_pred, squared=False))
print(r2_score(y_test, y_pred))
```

教学要点：线性回归不是“过时模型”，而是理解监督学习、损失函数、特征系数和泛化误差的基础。学习者应学会看残差图，而不是只看一个 R²。

易错点：
- 把分类任务误用线性回归解决。
- 只看训练集分数，不看测试集或验证集。
- 忽略异常值对 MSE 和线性系数的影响。
