# 类别不平衡处理 (Class Imbalance)

- 知识点：类权重调整 (class_weight)、重采样、SMOTE

如果正类样本极少，模型倾向于全部预测为负类也能得到很高的准确率。可以通过设置 `class_weight='balanced'` 让模型对少数类分错时给予更大的惩罚，或者使用欠采样、过采样（如 SMOTE）等技术平衡数据集。
