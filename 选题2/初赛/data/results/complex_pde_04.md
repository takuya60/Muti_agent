# complex_pde_04 解答

## 最终答案

**

## 验证状态

pending

## 推理过程

**题目分析：**
求解一维热传导方程的初边值问题：
- 方程：\(\frac{\partial u}{\partial t} = \alpha^2 \frac{\partial^2 u}{\partial x^2}\)，\(0 < x < L\)，\(t > 0\)
- 边界条件：\(u(0, t) = 0\)，\(u(L, t) = 0\)，\(t > 0\)
- 初始条件：\(u(x, 0) = f(x) = \begin{cases} x, & 0 \leq x \leq L/2 \\ L - x, & L/2 < x \leq L \end{cases}\)

**求解目标：**
1. 写出分离变量的假设和特征值问题的推导过程。
2. 求解出傅里叶级数展开式的系数。
3. 给出 \(u(x, t)\) 的最终级数解表达式。

---

### 1. 分离变量假设与特征值问题推导

设解具有分离变量形式：
\[
u(x, t) = X(x) T(t)
\]
代入热传导方程：
\[
X(x) T'(t) = \alpha^2 X''(x) T(t)
\]
分离变量（假设 \(X(x) \neq 0\)，\(T(t) \neq 0\)）：
\[
\frac{T'(t)}{\alpha^2 T(t)} = \frac{X''(x)}{X(x)} = -\lambda
\]
其中 \(\lambda\) 为分离常数（取负号是为了得到常见的特征值形式）。由此得到两个常微分方程：
\[
T'(t) + \alpha^2 \lambda T(t) = 0 \tag{1}
\]
\[
X''(x) + \lambda X(x) = 0 \tag{2}
\]
将分离变量形式代入边界条件：
\[
u(0, t) = X(0) T(t) = 0 \implies X(0) = 0 \quad (\text{若 } T(t) \not\equiv 0)
\]
\[
u(L, t) = X(L) T(t) = 0 \implies X(L) = 0
\]
于是得到关于 \(X(x)\) 的特征值问题：
\[
\begin{cases}
X''(x) + \lambda X(x) = 0, \quad 0 < x < L \\
X(0) = 0, \quad X(L) = 0
\end{cases}
\]

**求解特征值问题：**
对 \(\lambda\) 分三种情况讨论。

- **情况 1：\(\lambda < 0\)**，令 \(\lambda = -\mu^2\)（\(\mu > 0\)）。方程化为 \(X'' - \mu^2 X = 0\)，通解为：
  \[
  X(x) = A \cosh(\mu x) + B \sinh(\mu x)
  \]
  由 \(X(0) = 0\) 得 \(A = 0\)；由 \(X(L) = B \sinh(\mu L) = 0\) 得 \(B = 0\)（因 \(\mu L \neq 0\)）。只有平凡解 \(X(x) \equiv 0\)。

- **情况 2：\(\lambda = 0\)**。方程化为 \(X'' = 0\)，通解为 \(X(x) = Ax + B\)。由 \(X(0) = B = 0\)，再由 \(X(L) = AL = 0\) 得 \(A = 0\)。只有平凡解。

- **情况 3：\(\lambda > 0\)**，令 \(\lambda = \beta^2\)（\(\beta > 0\)）。方程化为 \(X'' + \beta^2 X = 0\)，通解为：
  \[
  X(x) = A \cos(\beta x) + B \sin(\beta x)
  \]
  由 \(X(0) = A = 0\)；再由 \(X(L) = B \sin(\beta L) = 0\)。要求非平凡解（\(B \neq 0\)），则必须 \(\sin(\beta L) = 0\)，即
  \[
  \beta L = n\pi \quad (n = 1, 2, 3, \dots) \implies \beta_n = \frac{n\pi}{L}
  \]
  对应的特征值为：
  \[
  \lambda_n = \beta_n^2 = \left(\frac{n\pi}{L}\right)^2
  \]
  特征函数为：
  \[
  X_n(x) = \sin\left(\frac{n\pi x}{L}\right) \quad (n = 1, 2, 3, \dots)
  \]
  （积分常数可吸收到后续的级数系数中）

---

### 2. 求解傅里叶级数展开式的系数

对于每个特征值 \(\lambda_n\)，求解关于 \(T(t)\) 的方程 (1)：
\[
T'(t) + \alpha^2 \left(\frac{n\pi}{L}\right)^2 T(t) = 0 \implies T_n(t) = C_n \exp\left[-\alpha^2 \left(\frac{n\pi}{L}\right)^2 t\right]
\]
由叠加原理，得到形式解：
\[
u(x, t) = \sum_{n=1}^{\infty} b_n \sin\left(\frac{n\pi x}{L}\right) \exp\left[-\alpha^2 \left(\frac{n\pi}{L}\right)^2 t\right]
\]
其中系数 \(b_n = B_n C_n\) 由初始条件确定。代入 \(t = 0\)：
\[
u(x, 0) = f(x) = \sum_{n=1}^{\infty} b_n \sin\left(\frac{n\pi x}{L}\right)
\]
这是 \(f(x)\) 在 \([0, L]\) 上的正弦傅里叶级数展开，系数公式为：
\[
b_n = \frac{2}{L} \int_0^L f(x) \sin\left(\frac{n\pi x}{L}\right) dx
\]
根据 \(f(x)\) 的分段定义，将积分拆为两部分：
\[
f(x) = \begin{cases}
x, & 0 \leq x \leq L/2 \\
L - x, & L/2 < x \leq L
\end{cases}
\]
计算积分：
\[
I = \int_0^L f(x) \sin\left(\frac{n\pi x}{L}\right) dx = \int_0^{L/2} x \sin\left(\frac{n\pi x}{L}\right) dx + \int_{L/2}^L (L - x) \sin\left(\frac{n\pi x}{L}\right) dx
\]
第二项积分作变量代换 \(y = L - x\)，则 \(dx = -dy\)，积分限变为 \(y = L/2\) 到 \(0\)：
\[
\int_{L/2}^L (L - x) \sin\left(\frac{n\pi x}{L}\right) dx = \int_{L/2}^0 y \sin\left(\frac{n\pi (L - y)}{L}\right) (-dy) = \int_0^{L/2} y \sin\left(n\pi - \frac{n\pi y}{L}\right) dy
\]
利用三角恒等式 \(\sin(n\pi - \theta) = (-1)^{n+1} \sin\theta\)（因 \(\sin(n\pi - \theta) = -\cos(n\pi)\sin\theta = -(-1)^n \sin\theta = (-1)^{n+1}\sin\theta\)）：
\[
= (-1)^{n+1} \int_0^{L/2} y \sin\left(\frac{n\pi y}{L}\right) dy
\]
因此总积分可合并为：
\[
I = \int_0^{L/2} x \sin\left(\frac{n\pi x}{L}\right) dx + (-1)^{n+1} \int_0^{L/2} x \sin\left(\frac{n\pi x}{L}\right) dx = \left[1 + (-1)^{n+1}\right] \int_0^{L/2} x \sin\left(\frac{n\pi x}{L}\right) dx
\]
令 \(k = \frac{n\pi}{L}\)，计算基本积分：
\[
\int_0^{L/2} x \sin(kx) dx = \left[ -\frac{x \cos(kx)}{k} + \frac{\sin(kx)}{k^2} \right]_0^{L/2}
\]
代入上下限：
\[
= -\frac{(L/2) \cos(n\pi/2)}{k} + \frac{\sin(n\pi/2)}{k^2} = -\frac{L^2}{2n\pi} \cos\left(\frac{n\pi}{2}\right) + \frac{L^2}{n^2\pi^2} \sin\left(\frac{n\pi}{2}\right)
\]
由于因子 \(1 + (-1)^{n+1}\)：
- 当 \(n\) 为偶数时，\((-1)^{n+1} = -1\)，因子为 \(0\)，故 \(b_n = 0\)。
- 当 \(n\) 为奇数时，\((-1)^{n+1} = 1\)，因子为 \(2\)，且 \(\cos(n\pi/2) = 0\)，\(\sin(n\pi/2) = (-1)^{(n-1)/2}\)。

设 \(n = 2m-1\)（\(m = 1, 2, 3, \dots\)），则：
\[
I = 2 \cdot \frac{L^2}{(2m-1)^2\pi^2} \sin\left(\frac{(2m-1)\pi}{2}\right) = \frac{2L^2}{(2m-1)^2\pi^2} (-1)^{m-1}
\]
代入系数公式：
\[
b_{2m-1} = \frac{2}{L} \cdot I = \frac{4L}{(2m-1)^2\pi^2} (-1)^{m-1}
\]
对于偶数 \(n\)，\(b_n = 0\)。因此系数可统一写为：
\[
b_n = \begin{cases}
0, & n \text{ 为偶数} \\
\dfrac{4L}{n^2\pi^2} (-1)^{(n-1)/2}, & n \text{ 为奇数}
\end{cases}
\]

---

### 3. \(u(x, t)\) 的最终级数解表达式

将系数代入形式解，只对奇数 \(n = 2m-1\) 求和：
\[
u(x, t) = \sum_{m=1}^{\infty} \frac{4L}{(2m-1)^2\pi^2} (-1)^{m-1} \sin\left(\frac{(2m-1)\pi x}{L}\right) \exp\left[-\alpha^2 \left(\frac{(2m-1)\pi}{L}\right)^2 t\right]
\]
或等价地用 \(n\) 表示：
\[
u(x, t) = \frac{4L}{\pi^2} \sum_{\substack{n=1 \\ n \text{ odd}}}^{\infty} \frac{(-1)^{(n-1)/2}}{n^2} \sin\left(\frac{n\pi x}{L}\right) \exp\left(-\alpha^2 \frac{n^2\pi^2}{L^2} t\right)
\]

---

**验证：**
- 边界条件：每一项在 \(x=0\) 和 \(x=L\) 处 \(\sin\) 为零，满足。
- 初始条件：\(t=0\) 时级数为 \(f(x)\) 的正弦级数，系数计算正确。
- 特征值问题无复数解，Sturm-Liouville 理论保证所有特征值为正实数。

**最终答案：**
\[
u(x, t) = \frac{4L}{\pi^2} \sum_{m=1}^{\infty} \frac{(-1)^{m-1}}{(2m-1)^2} \sin\left(\frac{(2m-1)\pi x}{L}\right) \exp\left[-\alpha^2 \left(\frac{(2m-1)\pi}{L}\right)^2 t\right]
\]
