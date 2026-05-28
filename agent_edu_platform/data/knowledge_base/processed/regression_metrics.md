# 回归模型评估指标

- 知识点：MAE、MSE、RMSE、R²、残差、误差分布

回归任务预测连续数值，不能用 accuracy 评价。常见指标包括 MAE、MSE、RMSE 和 R²。MAE 是平均绝对误差，容易解释；MSE 对大误差惩罚更重；RMSE 与目标变量单位相同，更便于理解；R² 衡量模型解释方差的比例。

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)
print(mae, rmse, r2)
```

除了指标，还应查看残差分布。残差是 `真实值 - 预测值`，如果残差呈现明显模式，说明模型可能漏掉了非线性关系、关键特征或不同群体差异。

```python
import matplotlib.pyplot as plt

residuals = y_test - y_pred
plt.scatter(y_pred, residuals)
plt.axhline(0, color='red', linestyle='--')
```

审核规则：
- 回归任务不能报告 accuracy。
- 只看 R² 不够，应同时报告误差大小。
- 指标应结合目标变量单位解释，例如“平均误差约 3.2 分”。
