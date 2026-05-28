# 训练/验证/测试集划分

- 知识点：训练集、验证集、测试集、调参、最终评估、数据泄漏

机器学习建模不能只把数据分成训练集和测试集。更完整的流程通常包括训练集、验证集和测试集：训练集用于学习模型参数；验证集用于选择超参数、比较模型和调整阈值；测试集只在最后用一次，用来估计最终模型在未知数据上的表现。

如果反复查看测试集分数并据此改模型，测试集就不再是真正的“未知考试题”，评估结果会偏乐观。这是机器学习实训中最常见的隐性数据泄漏。

实操示例：

```python
from sklearn.model_selection import train_test_split

X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)
```

上面代码最终得到 60% 训练集、20% 验证集、20% 测试集。分类任务建议使用 `stratify` 保持类别比例一致；回归任务则需要关注目标值分布是否在各集合中大致一致。

审核规则：
- 测试集不能参与调参、选特征、定阈值。
- 分类任务要检查划分后类别比例。
- 小数据集可以用交叉验证替代单一验证集，但最终测试集仍应保留。
