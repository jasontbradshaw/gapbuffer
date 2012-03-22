#!/usr/bin/env python
import array
from itertools import izip_longest
import re

class gapbuffer(object):
    """
    Represents a sequence of identically-typed primitive items using a gap
    buffer. Can be initialized with any iterable item, as long as the items in
    the iterable are all of the same type. Uses an array.array internally to
    store data.
    """

    # type information for the different types our internal array can take on.
    # used to initialize the internal array to some non-zero size and to get
    # formal names for the type codes.
    TYPE_INFO = {
        "c": (str(' '), "character"),
        "b": (0, "signed character"),
        "B": (0, "unsigned character"),
        "u": (unicode(' '), "unicode character"),
        "h": (0, "signed short"),
        "H": (0, "unsigned short"),
        "i": (0, "signed int"),
        "I": (0L, "unsigned int"),
        "l": (0L, "signed long"),
        "L": (0L, "unsigned long"),
        "f": (0.0, "float"),
        "d": (0.0, "double")
    }

    def __init__(self, typecode, initial_content=[], min_gap_size=10):
        """
        TODO
        """

        # minimum space to create for the new gap when resizing the current one
        self.__min_gap_size = min_gap_size

        # allocate the initial gap for the internal buffer. if the typecode is
        # invalid, array.array throws a nice ValueError for us.
        item = gapbuffer.TYPE_INFO[typecode][0]
        self.__buf = array.array(typecode, (item for i in xrange(min_gap_size)))

        # first space of the gap, initially always at the start of the buffer
        self.__gap_start = 0

        # first space after the final space in the gap, even if past the end of
        # the internal buffer. since our buffer is (at the moment) all-gap, it
        # starts as the length of the buffer.
        self.__gap_end = len(self.__buf)

        # add the initial content (defaults to an empty iterable)
        try:
            # add the initial content to the end of the buffer
            self.__buf.extend(initial_content)

        except TypeError:
            # map array's TypeError to our own version of the same
            raise TypeError(self.__class__.__name__ + " items must be of type "
                    + gapbuffer.TYPE_INFO[typecode][1])

        # the space immediately following the final item in the buffer,
        # including space for the gap. i.e., if the gap is at the very end of
        # the buffer, the content end is equivalent to the gap end.
        self.__content_end = len(self.__buf)

    @property
    def __gap_len(self):
        """Get the length of the current gap."""
        return self.__gap_end - self.__gap_start

    def __len__(self):
        """Get the length of the buffer."""
        return self.__content_end - self.__gap_len

    def __compare(self, other):
        """
        Does a lexicographic comparison with another other iterable, and returns
        -1, 0, or 1 if the buffer is less than, equal to, or greater than the
        other.
        """

        # fill value guaranteed to be unique to this fun. call and inaccessible
        fv = lambda: None
        for i, (si, oi) in enumerate(izip_longest(self, other, fillvalue=fv)):
            # we're shorter than the other iterable and aren't different
            if si is fv:
                return -1

            # the other is shorter than us and not different
            if oi is fv:
                return 1

            # we're smaller than the other, or the other is larger
            if oi > si:
                return -1
            elif oi < si:
                return 1

            # guard against infinite iterable comparisons
            if i >= len(self):
                return -1

        # we're equal if none of the cases passed (same length, not different)
        return 0

    def __eq__(self, other):
        """Determine whether this is item-equivalent to another iterable."""

        # optimize for iterables that the len() method works on
        if hasattr(other, "__len__") and len(other) != len(self):
            return False

        return self.__compare(other) == 0

    def __cmp__(self, other):
        """Lexicographically compares this with another iterable."""
        return self.__compare(other)

    def __contains__(self, value):
        """
        Return True if the given item is contained in the buffer, False
        otherwise.
        """

        # substring test for character and unicode buffers
        if (self.__buf.typecode in ["u", "c"] and isinstance(value, basestring)
                and len(value) > 1):
            # prevent re from finding weird things if given an empty string
            if len(value) == 0:
                return False

            # store the gap size for later
            gap_len = self.__gap_len

            # move the gap to the end of the buffer
            self.__move_gap(len(self))

            # remove the gap. this should just be a pointer update in the C code
            for i in xrange(gap_len):
                self.__buf.pop(len(self))

            # get the result, replace the gap, then return the stored result
            result = re.search(re.escape(value), self.__buf) is not None

            for i in xrange(gap_len):
                item = gapbuffer.TYPE_INFO[self.__buf.typecode][0]
                self.__buf.extend(item for i in xrange(gap_len))

            return result

        # general test for membership, including single-character string values
        for item in self:
            if value == item:
                return True

        return False

    def __add__(self, other):
        """
        Concatenate the other iterable to this one and return the result as a
        new buffer.
        """

        added = gapbuffer(self.__buf.typecode, self)
        added.extend(other)

        return added

    def __iadd__(self, other):
        """Concatenate the other iterable to this one in-place."""
        self.extend(other)

    def __mul__(self, n):
        """
        Concatenate ourself to ourself some number of times and return the
        result as a new buffer.
        """

        multiplied = gapbuffer(self.__buf.typecode)

        # don't concatenate if 0 or less was specified
        if n > 0:
            for i in xrange(n):
                multiplied.extend(self)

        return multiplied

    def __imul__(self, n):
        """Concatenate ourself to ourself some number of times in-place."""

        # clear the buffer if 0 or less was specified
        if n <= 0:
            # completely rebuild this buffer
            self.__init__(self.__buf.typecode, min_gap_size=self.__min_gap_size)
        else:
            for i in xrange(n - 1):
                self.extend(self)

    def __getitem__(self, x):
        """Get the item or slice at the given index."""

        # handle slicing with a 'step' (normal format is handled by __getslice__)
        if isinstance(x, slice):
            return self.__get_slice(x)
        return self.__get_index(x)

    def __get_index(self, i):
        """Get the item at some index."""

        # constrain index bounds
        if i >= len(self) or i < -len(self):
            raise IndexError(self.__class__.__name__ + " index out of range")

        # if before the gap, access buffer directly, else account for gap
        index = i if i < self.__gap_start else i + self.__gap_len
        return self.__buf[index]

    def __get_slice(self, s):
        """Get the sequence at the given slice."""

        # unpack 'indices()' into xrange as a generator for our items
        return gapbuffer(self.__buf.typecode,
                (self[i] for i in xrange(*s.indices(len(self)))))

    def __setitem__(self, x, value):
        """Set an index or slice to some value."""

        if isinstance(x, slice):
            return self.__set_slice(x, value)
        return self.__set_index(x, value)

    def __set_index(self, i, value):
        """Set the item at some index."""

        if i >= len(self) or i < -len(self):
            raise IndexError(self.__class__.__name__ + " index out of range")

        index = i if i < self.__gap_start else i + self.__gap_len
        self.__buf[index] = value

    def __set_slice(self, s, value):
        """Set the slice at some index."""

        raise NotImplementedError()

        # get shorthand values for the indices of the slice
        stop, start, step = s.indices(len(self))

        # if we can get the length of the value and get its items directly,
        # and the value is the same size as what it's replacing, do a direct
        # replace without moving the gap.
        slice_len = stop - start
        if (hasattr(value, "__len__") and hasattr(value, "__getitem__")
                and len(value) == slice_len):
            # do a direct replacement
            for vi, si in enumerate(xrange(*s.indices(len(self)))):
                self[si] = value[vi]
        else:
            for vi, si in enumerate(xrange(*s.indices(len(self)))):
                self[si] = value[vi]

    def __delitem__(self, x):
        """Delete some index or slice."""

        if isinstance(x, slice):
            return self.__del_slice(x)
        return self.__del_index(x)

    def __del_index(self, i):
        """Delete the item at some index."""
        raise NotImplementedError()

    def __del_slice(self, s):
        """Delete some slice."""
        raise NotImplementedError()

    def index(self, item, start=0, end=None):
        """
        Return the index of the first occurence of 'item' in this gapbuffer such
        that 'start' (default 0) <= the index of 'item' < end (default end of
        the buffer). Return negative if the item was not found.
        """

        raise NotImplementedError()

    def count(self, item):
        """Return the number of times 'item' occurs in this gapbuffer."""
        raise NotImplementedError()

    def append(self, item):
        """Append the 'item' to this gapbuffer."""
        self.insert(len(self), item)

    def extend(self, other):
        """
        Append all the items from the other iterable onto the end of this
        gapbuffer.
        """

        # put the gap at the beginning of the buffer
        self.__move_gap(0)

        # append the other iterable's items to the end of the existing buffer
        self.__buf.extend(other)

    def insert(self, index, item):
        """Insert an item at the given index."""
        self[index:index] = [item]

    def pop(self, index=None):
        """Remove the item at 'index' (default final item) and returns it."""

        if len(self) == 0:
            raise IndexError("pop from empty " + self.__class__.__name__)

        # default index to the end of the buffer
        index = len(self) - 1 if index is None else index

        item = self[index]
        del self[index]
        return item

    def remove(self, item):
        """Remove the first occurence of 'item' in this gapbuffer."""
        del self[self.index(item)]

    def reverse(self):
        """Reverse the items in this gapbuffer in-place."""

        # only reverse if necessary
        if len(self) > 1:
            for i in xrange(len(self) / 2):
                self[-(i + 1)], self[i] = self[i], self[-(i + 1)]

    def sort(self, cmp=None, key=None, reverse=False):
        """Sort the items of this gapbuffer in-place."""
        raise NotImplementedError()

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
        s = [
            u"'" + unicode(self) + u"', " + unicode(len(self)),
            self.__buf.tounicode()
        ]

        for row in rows:
            t = []
            for c in row:
                t.append(c if c is not None else u" ")
            s.append(u"".join(t))

        return u'\n'.join(s)

    def __resize_buf(self, target_size, factor=(1.0 / 16)):
        """
        Ensure that the buffer is at least as large as some target by repeatedly
        increasing its size by some factor (default 1/16).
        """

        # prevent decreasing or failure to increase buffer size
        assert factor > 0

        # increase the buffer size by our factor until it's long enough
        item = gapbuffer.TYPE_INFO[self.__buf.typecode][0]
        while len(self.__buf) < target_size:
            extend_len = max(1, int((1.0 + factor) * (1 + len(self.__buf))))
            self.__buf.extend(item for i in xrange(extend_len))

    def __resize_gap(self, target_size):
        """Ensure that the gap is at least as large as some target."""

        if self.__gap_len < target_size:
            # calculate size increase of the gap, including the min gap size
            gap_delta = target_size + self.__min_gap_size - self.__gap_len

            # make room for the current content and the new gap
            self.__resize_buf(len(self.__buf) + gap_delta)

            # shift the right content down to make room for the new gap
            for i in reversed(xrange(self.__gap_end, self.__content_end)):
                self.__buf[i + gap_delta] = self.__buf[i]

            # move the gap and content end pointers forward
            self.__gap_end += gap_delta
            self.__content_end += gap_delta

    def __move_gap(self, index):
        """Move the gap to some index."""

        # TODO: test corner cases (0-length gap, gap to ends, etc.)

        # don't move the gap if it consists of the entire internal buffer
        if len(self) == 0:
            return

        # make sure we're within virtual buffer bounds. the start of the
        # gap is always the same as the virtual buffer index, so we must limit
        # it to this since its end extends to the end of the actual buffer.
        assert 0 <= index < len(self)

        # optimize for moving a zero-length gap (avoids needless copies)
        if self.__gap_len == 0:
            self.__gap_start = self.__gap_end = index
            return

        # move the gap left as far as necessary
        while self.__gap_start > index:
            # slide the gap to the left
            self.__gap_start -= 1
            self.__gap_end -= 1

            # copy the gap's former preceding character to the gap's old
            # final slot.
            self.__buf[self.__gap_end] = self.__buf[self.__gap_start]

        # move the gap right as far as necessary
        while self.__gap_start < index:
            # copy the gap's following character to the gap's first slot.
            self.__buf[self.__gap_start] = self.__buf[self.__gap_end]

            # slide the gap to the right
            self.__gap_start += 1
            self.__gap_end += 1

    def __str__(self):
        """Return the string representation of the buffer's contents."""

        # NOTE: we do this separately from the unicode version to prevent weird
        # str/unicode conversions.

        # do more compact representations for string and unicode types
        if self.__buf.typecode in ["u", "c"]:
            return ''.join(c for c in self)

        # turn all other types into a simple list
        return repr([i for i in self])

    def __unicode__(self):
        """Return the unicode representation of the buffer's contents."""

        if self.__buf.typecode in ["u", "c"]:
            return u''.join(c for c in self)

        return unicode(repr([i for i in self]))

    def __repr__(self):
        # class name, typecode, and opening paren
        s = unicode(self.__class__.__name__ + "(" + repr(self.__buf.typecode))

        # add the content representation if there is any
        if len(self) > 0:
            s += u", "

            # do more compact represenstations for string and unicode types
            if self.__buf.typecode == "c":
                s += repr(''.join(c for c in self))
            elif self.__buf.typecode == "u":
                s += repr(u''.join(c for c in self))
            else:
                # turn all other types into a simple list
                s += repr([i for i in self])

        # add close paren and return
        return s + u")"
