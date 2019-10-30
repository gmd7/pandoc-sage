```sagesilent
f(x)=x^2
```


\begin{align}
f(x)&=\sage{f(x)}\\
f(x)&=\sage{2*f(x)}
\end{align}


```sageblock
a='$f(x)=' + latex(f(x)) + '$'
print(a.strip())
```
