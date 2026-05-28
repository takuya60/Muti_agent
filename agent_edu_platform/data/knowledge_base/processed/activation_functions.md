# 激活函数

- 知识点：ReLU、Sigmoid、Tanh、非线性、梯度消失

激活函数给神经网络引入非线性。如果没有激活函数，多层线性变换叠加仍然等价于一个线性模型，无法表达复杂模式。常见激活函数包括 Sigmoid、Tanh 和 ReLU。

Sigmoid 会把数值压到 0 到 1，适合二分类输出层；Tanh 输出 -1 到 1；ReLU 在隐藏层中最常见，形式为 $\max(0, x)$，计算简单且缓解梯度消失问题。

```python
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])
```

教学要点：隐藏层常用 ReLU，二分类输出层常用 Sigmoid，多分类输出层常用 Softmax。激活函数的选择要和任务、损失函数配合。

审核规则：
- 二分类输出概率时通常用 Sigmoid + binary_crossentropy。
- 多分类互斥类别通常用 Softmax + categorical/cross entropy。
- 不应在所有层机械使用同一个激活函数。
