# 深度学习正则化与早停

- 知识点：Dropout、L1/L2、EarlyStopping、验证集、过拟合

神经网络参数多，容易过拟合。常见泛化手段包括 L1/L2 正则化、Dropout、早停、数据增强和减少模型规模。早停是实训中非常实用的方法：当验证集指标不再提升时停止训练，避免模型继续记忆训练集噪声。

```python
from tensorflow import keras

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )
]

model = keras.Sequential([
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_split=0.2, epochs=100, callbacks=callbacks)
```

教学要点：早停依赖验证集，不是看训练集 loss。Dropout 只在训练时随机关闭部分神经元，预测时会使用完整网络。

审核规则：
- 深度学习示例应包含验证集。
- 不应只训练固定 epoch 后报告训练集准确率。
- 小数据集上要警惕深度模型过拟合。
