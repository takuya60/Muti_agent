# complex_linear_algebra_03 解答

## 最终答案

**

## 验证状态

pending

## 推理过程

**最终答案：**

**1. 特征值及其代数重数**  
矩阵 \(A - \lambda I\) 的特征多项式为：
\[
\det(A - \lambda I) = (\lambda - 1)(\lambda - 2)(\lambda - 4)^2
\]
特征值及代数重数：  
- \(\lambda_1 = 1\)，代数重数 \(1\)  
- \(\lambda_2 = 2\)，代数重数 \(1\)  
- \(\lambda_3 = 4\)，代数重数 \(2\)

**2. 特征空间及其几何重数**  
**对于 \(\lambda = 1\)：**  
解 \((A - I)\mathbf{x} = \mathbf{0}\)，经行化简得基础解系：
\[
\mathbf{v}_1 = \begin{pmatrix} -1 \\ 1 \\ 0 \\ 0 \end{pmatrix}
\]
特征空间为 \(\operatorname{span}\{\mathbf{v}_1\}\)，几何重数为 \(1\)。

**对于 \(\lambda = 2\)：**  
解 \((A - 2I)\mathbf{x} = \mathbf{0}\)，经行化简得基础解系：
\[
\mathbf{v}_2 = \begin{pmatrix} 1 \\ -1 \\ 0 \\ 1 \end{pmatrix}
\]
特征空间为 \(\operatorname{span}\{\mathbf{v}_2\}\)，几何重数为 \(1\)。

**对于 \(\lambda = 4\)：**  
解 \((A - 4I)\mathbf{x} = \mathbf{0}\)，经行化简得基础解系：
\[
\mathbf{v}_3 = \begin{pmatrix} 1 \\ 0 \\ -1 \\ 1 \end{pmatrix}
\]
特征空间为 \(\operatorname{span}\{\mathbf{v}_3\}\)，几何重数为 \(1\)。

**3. 可对角化性及 Jordan 标准型**  
由于特征值 \(\lambda = 4\) 的几何重数 \(1\) 小于其代数重数 \(2\)，故矩阵 \(A\) 不可对角化。  
其 Jordan 标准型 \(J\) 由一个 \(1\) 阶块（对应 \(\lambda=1\)）、一个 \(1\) 阶块（对应 \(\lambda=2\)）和一个 \(2\) 阶块（对应 \(\lambda=4\)）构成：
\[
J = \begin{pmatrix}
1 & 0 & 0 & 0 \\
0 & 2 & 0 & 0 \\
0 & 0 & 4 & 1 \\
0 & 0 & 0 & 4
\end{pmatrix}
\]
