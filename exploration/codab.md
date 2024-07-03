---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-contingency-hurricanes
    language: python
    name: ds-contingency-hurricanes
---

# CODAB

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
from src.datasources import codab
```

```python
codab.download_codab("jam")
codab.download_codab("vct")
```

```python
jam = codab.load_codab("jam")
vct = codab.load_codab("vct")
```

```python
ax = jam.plot()
vct.plot(ax=ax)
```

```python

```
