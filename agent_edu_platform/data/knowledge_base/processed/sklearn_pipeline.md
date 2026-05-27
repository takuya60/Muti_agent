# Sklearn Pipeline 构建

- 知识点：工作流封装、Pipeline、防止数据泄露

将数据预处理（如 `StandardScaler`）和模型训练（如 `LogisticRegression`）串联起来，可以使用 `Pipeline`。这不仅使代码更简洁，更重要的是在进行交叉验证时，能保证每次划分的数据都是在各自的训练集上进行预处理拟合，完全避免数据泄露。
