# 模型保存与实验复现

- 知识点：joblib、随机种子、参数记录、指标记录、实验复现

机器学习实训不只是训练出一个模型，还要能复现结果。复现实验至少包括：固定随机种子、保存训练好的模型、记录数据版本、参数配置和评估指标。否则同一段代码每次运行结果不同，很难判断改动是否有效。

sklearn 模型通常可以用 joblib 保存。对于包含预处理的 Pipeline，应该保存整个 Pipeline，而不是只保存最后的模型。

```python
import joblib
from sklearn.pipeline import Pipeline

pipeline.fit(X_train, y_train)
joblib.dump(pipeline, 'model_pipeline.joblib')

loaded = joblib.load('model_pipeline.joblib')
y_pred = loaded.predict(X_test)
```

复现实验还应记录 `random_state`、交叉验证折数、评价指标、数据切分方式和重要超参数。

教学要点：保存模型不是最后的附加步骤，而是工程化机器学习的一部分。保存完整 Pipeline 可以避免上线时忘记做标准化、编码或插补。

审核规则：
- 不应只保存模型而丢失预处理器。
- random_state 应在演示代码中固定。
- 应记录参数和指标，方便比较实验。
