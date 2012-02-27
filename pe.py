#!/usr/bin/env python
import array
import os

class Range(object):
    """
    Represents a numeric range. Use 'len()' to get its size.
    """

    def __init__(self, start, stop):
        self.__start = start
        self.__stop = stop
        self.__size = stop - start

    @property
    def start(self):
        """
        Get the position of the range's start, the first valid character in the
        range.
        """

        return self.__start

    @property
    def stop(self):
        """
        Get the position of the range's end, the first character after the final
        character in the range (i.e. the first character not in the range).
        """

        return self.__stop

    def __len__(self):
        """Get the distance between the range's start and end."""
        return self.__size

class Buffer(object):
    """
    Represents unicode text using a gap buffer.
    """

    def __init__(self, initial_content=None):

        # points to first empty space after left text
        self.__gap_start = 0

        # points to first taken space at beginning of right text
        self.__gap_end = 0

        # the end of text content in our buffer
        self.__content_end = 0

        # where the gap should be moved to when it needs to be moved
        self.__cursor = 0

        # whether the cursor has been moved without the gap being moved
        self.__cursor_dirty = False

        # the minimum amount of space to create when resizing the gap
        self.__min_gap_len = 10

        # initialize the buffer we use to hold text data in, a unicode array
        buf_content = None
        if initial_content is None:
            buf_content = u" " * 10
        else:
            # make sure our initial content is unicode
            if not isinstance(initial_content, unicode):
                raise ValueError("initial_content must be a unicode object")

            # insert the initial content and set the content end pointer for it
            buf_content = initial_content
            self.__content_end = len(initial_content)

        self.__buf = array.array("u", buf_content)

    @property
    def cursor(self):
        """Get the current position of the cursor."""
        return self.__cursor

    @cursor.setter
    def cursor(self, position):
        """Move the cursor within the buffer."""

        # NOTE: does not move the gap! when moved, the cursor position is marked
        # as 'dirty' so that when text changes happen, the gap can be moved
        # accordingly elsewhere.

        # store the former cursor position
        old_cursor = self.__cursor

        # move the cursor
        self.__cursor = position

        # constrain the cursor to the buffer's boundaries
        if self.__cursor < 0:
            self.__cursor = 0
        elif self.__cursor > len(self.__buf) - self.__gap_len:
            self.__cursor = len(self__buf) - self.__gap_len

        # mark the cursor as 'dirty' if it has moved
        self.__cursor_dirty = self.__cursor != old_cursor

    def insert(self, text):
        """
        Insert text before the cursor's current position. Moves the cursor to
        the last character of the inserted text.

        'text' must be a unicode string.
        """

        # we only allow unicode values in, so we can't screw up the data types!
        if not isinstance(text, unicode):
            raise ValueError("text must be a unicode object")

        # ensure the gap is large enough for the text being inserted
        self.__resize_gap(len(text))

        # move the gap to the cursor
        self.__move_gap()

        # insert text at left gap edge while moving the gap start forward
        for c in text:
            self.__buf[self.__gap_start] = c
            self.__gap_start += 1

        # move the cursor to match the new gap start and mark it as 'clean'
        self.__cursor = self.__gap_start
        self.__cursor_dirty = False

        return self

    def delete(self, length):
        """
        Remove text starting with the character at the cursor's current position
        and ending after 'length' characters have been removed.

        If 'length' is larger than the size of the buffer's remaining content,
        the text from the cursor to the end of the buffer is removed.
        """

        if length < 0:
            raise ValueError("length must be greater than or equal to 0")

        # don't do anything if nothing is to be deleted
        if length != 0:
            # move the gap to the cursor
            self.__move_gap()

            # increase the size of the gap to consume the deleted characters
            self.__gap_end += length

            # constrain the gap size to the length of the content
            if self.__gap_end > self.__content_end:
                self.__gap_end = self.__content_end

        return self

    def find(self, pattern, start=0, end=None):
        """
        Search for the given string or regular expression in the buffer.

        Returns an iterator that yields Range objects for all the matches in the
        buffer.

        'start' is the position to start looking for the pattern (default 0).
        'end' is the position after which to stop looking for the pattern
        (default None, i.e. the end of the buffer).

        Once the buffer is changed, the iterator will no longer be valid, but
        will still yield its original match locations. Make sure to do another
        'find()' operation if the buffer is changed!
        """

    def view(self, start=0, end=None):
        """
        Get the unicode string for the characters between start and end. Gets
        the entire buffer by default.

        'start' and 'end' are constrained to the beginning and end of the
        content of the buffer.

        If 'start' is greater than 'end', a ValueError will be raised.
        """

        # constrain the start and end values
        start = 0 if start < 0 else start
        if end is None or end > self.__content_end:
            end = self.__content_end

        # make sure we've got valid start/end values
        if start > end:
            raise ValueError("start must be less than or equal to end")

        # return the text with the gap excised
        return (self.__buf[start:self.__gap_start] +
                self.__buf[self.__gap_end:end]).tounicode()

    def debug_view(self):
        """
        Get a debug view of the buffer's contents and internal values as a
        unicode string.
        """

        # write special values into gap
        for i in xrange(self.__gap_start, self.__gap_end):
            self.__buf[i] = u"_"

        # write special values into blank area
        for i in xrange(self.__content_end, len(self.__buf)):
            self.__buf[i] = u"#"

        # our desired display characters and their positions
        chars = [
            ("s", self.__gap_start),
            ("e", self.__gap_end),
            ("^", self.__cursor),
            ("$", self.__content_end)
        ]

        # find the left-most value we'll be displaying
        max_pos = max(map(lambda t: t[1], chars))

        # track all the rows we'll need
        rows = []

        # add the first row
        rows.append([None] * (max_pos + 1))

        # insert all the characters into rows
        for char, pos in chars:
            # try all the rows in turn until an empty slot is found
            for i in xrange(len(chars)):
                # add more space if we need it
                if len(rows) == i:
                    rows.append([None] * (max_pos + 1))

                # fill the slot if it was empty, then move on
                if rows[i][pos] is None:
                    rows[i][pos] = char
                    break

        # build the final string
        s = [u"'", str(self), u"', ", str(len(self)), u"\n",
                self.__buf.tounicode(), u"\n"]

        for row in rows:
            for c in row:
                s.append(c if c is not None else u" ")
            s.append(u'\n')

        return u''.join(s)

    @property
    def __gap_len(self):
        """Get the length of the current gap."""
        return self.__gap_end - self.__gap_start

    @property
    def __left_len(self):
        """Get the length of the text to the left of the gap's start."""
        return self.__gap_start

    @property
    def __right_len(self):
        """Get the length of the text to the right of the gap's end."""
        return self.__content_end - self.__gap_end

    def __resize_gap(self, target_size):
        """Ensure that the gap is at least as large as some target."""

        if self.__gap_len < target_size:

            # calculate size increase of the gap
            gap_delta = target_size + self.__min_gap_len - self.__gap_len

            # make room for the current content and the new gap
            self.__resize_buf(len(self) + gap_delta)

            # shift the right content down to make room for the new gap
            for i in reversed(xrange(self.__gap_end, self.__content_end)):
                self.__buf[i + gap_delta] = self.__buf[i]

            # move the gap and content end pointers forward
            self.__gap_end += gap_delta
            self.__content_end += gap_delta

        return self

    def __resize_buf(self, target_size):
        """Ensure that the buffer is at least as large as some target."""

        # double the size while the buffer is shorter than the target length
        while len(self.__buf) < target_size:
            self.__buf.extend(self.__buf)

        return self

    def __move_gap(self):
        """
        Move the gap to the current cursor position if the cursor is dirty.
        """

        if self.__cursor_dirty:
            # move the gap left as far as necessary
            while self.__gap_start > self.__cursor:
                # slide the gap to the left
                self.__gap_start -= 1
                self.__gap_end -= 1

                # copy the gap's former preceding character to the gap's old
                # final slot.
                self.__buf[self.__gap_end] = self.__buf[self.__gap_start]

            # move the gap right as far as necessary
            while self.__gap_start < self.__cursor:
                # copy the gap's following character to the gap's first slot.
                self.__buf[self.__gap_start] = self.__buf[self.__gap_end]

                # slide the gap to the right
                self.__gap_start += 1
                self.__gap_end += 1

            # the gap start now matches the cursor, so mark it 'clean'
            self.__cursor_dirty = False

        return self

    def __len__(self):
        """Get the length of the buffer's text."""
        return self.__left_len + self.__right_len

    def __unicode__(self):
        """Get the buffer's entire text."""
        return self.view()

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self.__class__.__name__ + "(" + repr(self.view() + ")"))

if __name__ == "__main__":
    b = Buffer()
    print b.debug_view()

    b.insert(u"Hello!")
    print b.debug_view()

    b.cursor -= 1
    print b.debug_view()

    b.insert(u", world")
    print b.debug_view()

    b.cursor -= 5
    print b.debug_view()

    b.delete(5)
    print b.debug_view()

    b.insert(u"pants")
    print b.debug_view()

    b.cursor = 0
    print b.debug_view()

    b.insert(u"Whoa! ")
    print b.debug_view()
