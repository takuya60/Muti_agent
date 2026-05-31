# complex_calculus_02 解答

## 最终答案

** 0

## 验证状态

pending

## 推理过程

**分析：**  
计算反常积分：
$$ I = \int_{0}^{\infty} \frac{\ln x}{1 + x^2} \, dx $$
该积分存在两个需要处理的瑕点：\(x \to 0^+\) 时 \(\ln x \to -\infty\)，以及积分上限为无穷大。在计算前需先验证其收敛性。

**收敛性分析：**
- 当 \(x \to 0^+\) 时，\(\frac{\ln x}{1+x^2} \sim \ln x\)。因为 \(\int_0^a \ln x \, dx = \lim_{\varepsilon \to 0^+} [x \ln x - x]_\varepsilon^a = a\ln a - a\) 收敛，原积分在 \(x=0\) 处收敛。
- 当 \(x \to \infty\) 时，\(\frac{\ln x}{1+x^2} \sim \frac{\ln x}{x^2}\)。任取 \(p \in (1,2)\)（如 \(p=3/2\)），有 \(\lim_{x\to\infty} \frac{\ln x}{x^2} \big/ \frac{1}{x^{3/2}} = \lim_{x\to\infty} \frac{\ln x}{x^{1/2}} = 0\)，且 \(\int^\infty \frac{dx}{x^{3/2}}\) 收敛，故积分在无穷远处收敛。  
综上，该反常积分绝对收敛。

**变量代换法求值：**  
令 \(x = \frac{1}{t}\)，则当 \(x \to 0^+\) 时 \(t \to +\infty\)；当 \(x \to +\infty\) 时 \(t \to 0^+\)。且有：
$$ dx = -\frac{1}{t^2}\,dt, \qquad \ln x = \ln\left(\frac{1}{t}\right) = -\ln t, \qquad 1 + x^2 = 1 + \frac{1}{t^2} = \frac{t^2+1}{t^2} $$
代入积分：
\[
\begin{aligned}
I &= \int_{x=0}^{x=\infty} \frac{\ln x}{1+x^2}\,dx \\
&= \int_{t=\infty}^{t=0} \frac{-\ln t}{\frac{t^2+1}{t^2}} \left(-\frac{1}{t^2}\right) dt \\
&= \int_{\infty}^{0} \frac{-\ln t}{1} \cdot \frac{t^2}{t^2+1} \cdot \left(-\frac{1}{t^2}\right) dt \\
&= \int_{\infty}^{0} \frac{\ln t}{t^2+1}\,dt \\
&= -\int_{0}^{\infty} \frac{\ln t}{t^2+1}\,dt = -I
\end{aligned}
\]
得到 \(I = -I\)，即 \(2I = 0\)，故 \(I = 0\)。

**最终答案：** 0
