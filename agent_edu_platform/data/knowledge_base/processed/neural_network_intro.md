# 神经网络入门

- 知识点：感知器、隐藏层、矩阵乘法、激活函数、损失函数、梯度下降

神经网络可以理解为多层可学习的函数组合。每一层通常执行线性变换和非线性激活：线性部分用矩阵乘法计算加权和，激活函数让模型能表达非线性关系。多个隐藏层叠加后，模型可以学习更复杂的特征表示。

一个最小神经网络包括输入层、隐藏层、输出层、损失函数和优化器。训练过程会先前向传播得到预测，再根据损失通过反向传播计算梯度，最后用梯度下降更新参数。

教学上不要一开始堆 CNN/RNN/Transformer，而应先让学生理解：神经网络本质上仍是在学习参数、最小化损失、提升泛化。

```python
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_split=0.2, epochs=20)
```

易错点：
- 神经网络不等于一定比传统模型好。
- 表格小数据上，树模型和线性模型往往更稳。
- 神经网络通常需要缩放输入、验证集和早停。
