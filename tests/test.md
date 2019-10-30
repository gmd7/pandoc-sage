```sagesilent
f(x)=x^2
```
```{.sageplot width="50%"}
p = plot(x^2,(x,0,4))
sageplot[ymin=0,ymax=4](p)
```
```sageplot
p = plot(f(x),(x,0,4))
sageplot[ymin=0,ymax=4](p)
```

\begin{align}
f(x)&=\sage{f(x)} \\
&=4
\end{align}

$$f(x)=\sage{2*f(x)}$$

```{.latex width="60%"}
\documentclass{standalone}
 \usepackage{polynom}
\begin{document}
\vspace{5mm}
\polyset{style=C, div=:,vars=x}
\polylongdiv{x^3 - 2x^2 - 5x + 6}{x-1}
\end{document}
```
