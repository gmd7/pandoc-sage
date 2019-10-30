```sagesilent
p1(x)=3*x
q1(x)=x^2-9
f1p(x)=2*x
f1(x)=f1p(x)+p1(x)/q1(x)
f1s(x)=f1(x).factor()
```

 $f(x)=\sage{f1s(x)} = \sage{latex(f1s(x)).replace("x","(-x)").strip()}=-f(x)$ 
