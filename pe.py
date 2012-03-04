#!/usr/bin/env python
import array

class Buffer(object):
    """
    Represents unicode text using a gap buffer. Can be initialized with any
    iterable item, as long as that item yields unicode characters during
    iteration.
    """

    def __init__(self, initial_content=None):

        # points to first empty space after left text
        self.__gap_start = 0

        # points to first taken space at beginning of right text
        self.__gap_end = 0

        # where the gap should be moved to when it needs to be moved
        self.__cursor = 0

        # the minimum amount of space to create when resizing the gap
        self.__min_gap_len = 10

        # the end of content in the buffer
        self.__content_end = 0

        # NOTE: we set the content end individually later so we can allow
        # initial_content objects that have no __len__ method.

        # initialize the buffer we use to hold text data in, a unicode array
        if initial_content is None:
            # insert placeholder content if no initial content was specified
            self.__buf = array.array("u", u" " * 10)
            self.__content_end = 0
        else:
            # insert the initial content and set the content end pointer for it
            self.__buf = array.array("u", initial_content)
            self.__content_end = len(self.__buf)

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

        # move the cursor
        self.__cursor = position

        # constrain the cursor to the buffer's virtual boundaries
        if self.__cursor < 0:
            self.__cursor = 0
        elif self.__cursor > len(self):
            self.__cursor = len(self)

    @property
    def __cursor_dirty(self):
        """Return whether the cursor matches the gap start."""
        return self.__cursor != self.__gap_start

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

    #
    # NOTE: together, __len__ and __getitem__ make for iteration!
    #

    def __len__(self):
        """Get the length of the buffer's text."""
        return self.__left_len + self.__right_len

    def __getitem__(self, index):
        """Get the character or slice at some index."""

        # get a slice rather than an index if necessary
        if isinstance(index, slice):
            # unpack 'indices()' into xrange, then pass generator to new Buffer
            return u''.join(self[i] for i in xrange(*index.indices(len(self))))
        else:
            # constrain index bounds
            if index >= len(self):
                raise IndexError(self.__class__.__name__ + " index out of range")

            # if before the gap, access buffer directly, else account for gap
            i = index if index < self.__gap_start else index + self.__gap_len

            # access the buffer
            return self.__buf[i]

    def __setitem__(self, index, value):
        """Set the character or slice at some index."""

        # set a slice rather than an index if necessary
        if isinstance(index, slice):
            # if we can get the length of the value, attempt a direct replace
            slice_len = abs(index.stop - index.start)
            if hasattr(value, "__len__") and len(value) == slice_len:
                # do a direct replacement
                for i in xrange(*index.indices(len(self))):
                    self[i] = value[i]
            else:
                # store the cursor position
                old_cursor = self.cursor

                # delete old slice and insert the new one
                self.cursor = index.start
                self.delete(index.stop - index.start)
                self.insert(value)

                # restore the cursor position while accounting for size change
                self.cursor = min(old_cursor, len(self))
        else:
            if index >= len(self):
                raise IndexError(self.__class__.__name__ + " index out of range")

            i = index if index < self.__gap_start else index + self.__gap_len
            self.__buf[i] = value

    def insert(self, text, position=None):
        """
        Insert text before the cursor's current position.

        If 'position' is specified, moves the cursor to the given position
        before inserting the text.

        Moves the cursor to the last character of the inserted text.

        'text' must be return unicode characters during iteration, or a
        TypeError will be raised.
        """

        # first move the cursor to the position if a position was specified
        if position is not None:
            self.cursor = position

        # move the gap to the cursor
        self.__move_gap()

        # ensure the gap is large enough for the text being inserted
        self.__resize_gap(len(text))

        # insert text at left gap edge while moving the gap start forward
        for c in text:
            self.__buf[self.__gap_start] = c
            self.__gap_start += 1

        # move the cursor to match the new gap start
        self.__cursor = self.__gap_start

        return self

    def delete(self, length, position=None):
        """
        Remove text starting with the character at the cursor's current position
        and ending after 'length' characters have been removed.

        If 'position' is specified, moves the cursor to the given position
        before deleting the text.

        If 'length' is larger than the size of the buffer's remaining content,
        the text from the cursor to the end of the buffer is removed.
        """

        if position is not None:
            self.cursor = position

        if length < 0:
            raise ValueError("length must be greater than or equal to 0")

        # don't do anything if nothing is to be deleted
        if length != 0:
            # move the gap to the cursor
            self.__move_gap()

            # increase the size of the gap to consume the deleted characters,
            # but only up to the size of the internal buffer.
            self.__gap_end += min(length, len(self.__buf))

        return self

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
        s = [u"'", unicode(self), u"', ", unicode(len(self)), u"\n",
                self.__buf.tounicode(), u"\n"]

        for row in rows:
            for c in row:
                s.append(c if c is not None else u" ")
            s.append(u'\n')

        return u''.join(s)

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

        return self

    def __unicode__(self):
        """Get the buffer's entire text."""
        return self[:]

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self.__class__.__name__ + "(" + repr(self[:]) + ")")

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
