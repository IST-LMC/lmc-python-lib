lmc-python-lib
==============

### Purpose

This may not be useful at all outside of the LMC project, unless the odd code
snippet helps someone else using pyrax with swift (or some other future thing
that we add here). We're writing more and more operational scripts in python
and this should help DRY them up a bit. If any of it proves to be more generally
applicable outside of the project, it may make sense to turn it into a python
egg. Until then, there's this...

### Example deployment

```bash
cd /usr/local/lib
git clone https://github.com/cybera/lmc-python-lib.git lmc-python
```

### Example usage

```python
import sys
sys.path += [ '/usr/local/lib/lmc-python' ]
import lmc.swift
```
