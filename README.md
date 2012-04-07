gapbuffer
====

A gap buffer ([wikipedia](http://en.wikipedia.org/wiki/Gap_buffer)) implemented
in pure Python using the `array` module. It supports almost all the functions
you'd expect of an iterable, and additionally allows comparisons against
non-gapbuffer iterables.

Usage
----
A `gapbuffer` uses an `array.array` internally to store its data, and is
therefor bound by the same constraints the `array.array` is, namely that it can
only contain items of the same type, and that the type must be specified at
instantiation.

See the `array` module documentation at http://docs.python.org/library/array.html
for valid type codes and usage examples.

Now for some code:

```python
from gapbuffer import gapbuffer

g = gapbuffer("c", "hello, world!")
print g
# prints 'hello, world!'

g[5:5] = " there"
print g
# prints 'hello there, world!'

del g[11:-1]
print g
# prints 'hello there!'

print g.pop()
# prints '!'
print g
# prints 'hello there'

g.extend(", i'm a gapbuffer!")
print g
# prints 'hello there, i'm a gapbuffer!'

print 'there' in g
# prints 'True'

print 'tear' in g
# prints 'False'

print g.index("o")
# prints '4'
```

gapbuffers support Python's `with` syntax to access the underlying `array`,
sans-gap. This is useful for doing regular expression searches over the buffer,
since the `re` library can't easily search over custom classes.

```python
from gapbuffer import gapbuffer
import re

g = gapbuffer("c", "you say goodbye, i say hello!")
print re.findall("goodbye|hello", g)
# raises 'TypeError: expected string or buffer'

with g as buf:
    print type(buf)
    # prints "<type 'array.array'>"

    print re.findall("goodbye|hello", buf)
    # prints "[array('c', 'goodbye'), array('c', 'hello')]"
```

How it Works
---
A gap buffer is an array optimized for insertions that happen near each other,
like those in a text editor.

Say we have some text, `hello, world!`. Internally, our buffer might look like
`hello, world!_______`, where the underscores represent the gap.

Say we want to insert some text in the middle of the string. First, we move the
gap iteratively to the point we want to insert the text, copying characters from
one end of the buffer to the other as we go:

```
hello, world!_______
hello, world_______!
hello, worl_______d!
hello, wor_______ld!
hello, wo_______rld!
hello, w_______orld!
hello, _______world!
hello,_______ world!
hello_______, world!
```


Then, we insert some new text into the spaces left by the gap:

```
hello ______, world!
hello t_____, world!
hello th____, world!
hello the___, world!
hello ther__, world!
hello there_, world!
```


When we iterate over the contents, we only return the non-gap text, i.e. `hello
there, world!`.

If we want to delete some text, we just expand the gap to consume it:

```
hello there__ world!
hello there___world!
hello there____orld!
hello there_____rld!
hello there______ld!
hello there_______d!
hello there________!
```


Leaving us with `hello there!`.

When the content to be inserted is larger than the gap, the gap is expanded and
the existing content is moved further down the buffer.

The `gapbuffer` class handles this manipulation internally, so all a user has to
do is use it like one would use the `array` module. Inserts and deletes that are
near the same location should show near-linear behavior on the length of the
inserted content, as long as the content doesn't exceed the average size of the
gap.

Tests
----
Tests can be run with `python test_gapbuffer.py`, and will use the `coverage`
module if available to generate a HTML report. Currently, test code coverage is
100%!
