# Keras Sequential 快速实验

- 知识点：Keras、Sequential、Dense、compile、fit、evaluate、快速原型

Keras 适合用来快速搭建神经网络原型。Sequential 模型按顺序堆叠层，适合入门演示简单回归、二分类、多分类和 MNIST 等任务。相比底层框架训练循环，Keras 更关注模型结构、损失函数、优化器和训练过程。

```python
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=20,
    batch_size=32
)

print(model.evaluate(X_test, y_test))
```

教学取舍：Keras 可以作为“体验神经网络”的入口，但不应该替代表格机器学习主线。对于小型结构化数据，线性模型、树模型和集成模型通常更容易解释，也更适合作为入门路线主体。

审核规则：
- 注意旧教程中的过时 API，例如 `output_dim`、`lr` 等，应改成现代写法。
- 应保留验证集或 early stopping。
- 分类任务要匹配正确输出层和损失函数。
