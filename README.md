gapbuffer
----

A gap buffer ([wiki](http://en.wikipedia.org/wiki/Gap_buffer)) implemented in
pure Python using the `array` module. Supports all the functions you'd expect of
an iterable, and additionally allows comparisons against non-gapbuffer
iterables.

How it Works
---
A gap buffer is an array optimized for insertions that happen near each other,
like those in a text editor.

Say we have some text, 'hello, world!'. Our buffer might look like this:
`hello, world!_____`
where the underscores are the gap.

Say we want to insert some text in the middle of the string. First, we move the
gap iteratively to the point we want to insert the text, copying characters from
one end of the buffer to the other as we go:
1. `hello, world!_______`
2. `hello, world_______!`
3. `hello, worl_______d!`
4. `hello, wor_______ld!`
5. `hello, wo_______rld!`
6. `hello, w_______orld!`
7. `hello, _______world!`
8. `hello,_______ world!`
9. `hello_______, world!`

Then, we insert some new text into the spaces left by the gap:
1. `hello ______, world!`
2. `hello t_____, world!`
3. `hello th____, world!`
4. `hello the___, world!`
5. `hello ther__, world!`
6. `hello there_, world!`

When we iterate over the contents, we only return the non-gap text, i.e. `hello
there, world!`.

If we want to delete some text, we just expand the gap to consume it:
1. `hello there__ world!`
2. `hello there___world!`
3. `hello there____orld!`
4. `hello there_____rld!`
5. `hello there______ld!`
5. `hello there_______d!`
5. `hello there________!`

Leaving us with `hello there!`.

The `gapbuffer` class handles all of this internally, so all a user has to do is
use it like one would use the `array` module. Inserts and deletes that are
near the same location should show near linear behavior on the length of the
inserted content, as long as the content doesn't exceed the average size of the
gap.

Tests
----
Tests can be run with `python test_gapbuffer.py`, and will use the `coverage`
module if available to generate a HTML report. Currently, test code coverage is
100%!
