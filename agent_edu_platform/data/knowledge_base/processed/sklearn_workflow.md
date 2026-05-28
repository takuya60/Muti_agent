# sklearn 标准建模流程

- 知识点：sklearn、fit、predict、predict_proba、score、Pipeline、基线模型

sklearn 是传统机器学习入门最常用的工具库。一个标准建模流程通常包括：读取数据、划分训练/测试集、预处理、建立模型、训练、预测、评估和复盘。大多数 sklearn 模型都有统一接口：`fit` 用于训练，`predict` 用于预测类别或数值，`predict_proba` 用于输出分类概率，`score` 用于快速查看默认分数。

建议初学者先建立一个简单基线模型，而不是一开始就追求复杂算法。基线模型能帮助判断后续特征工程和模型调参是否真的有效。

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=1000))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))
```

教学要点：sklearn 的统一接口能帮助学习者把注意力放在机器学习流程，而不是 API 细节。训练代码应优先使用 Pipeline，尤其是存在标准化、缺失值插补、编码等预处理步骤时。

审核规则：
- 不建议预处理散落在训练流程外部。
- 代码应包含明确的评估步骤，而不仅仅是 `model.fit`。
- 分类模型如果需要概率解释，应使用 `predict_proba` 而不是只看 `predict`。
