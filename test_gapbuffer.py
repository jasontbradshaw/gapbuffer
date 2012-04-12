#!/usr/bin/env python

import unittest

# correct content for each typecode
VALID_CONTENT = {
    "c": str("abc"),
    "b": [0, 1, 2],
    "B": [0, 1, 2],
    "u": unicode("abc"),
    "h": [0, 1, 2],
    "H": [0, 1, 2],
    "i": [0, 1, 2],
    "I": [0L, 1L, 2L],
    "l": [0L, 1L, 2L],
    "L": [0L, 1L, 2L],
    "f": [0.0, 1.0, 2.0],
    "d": [0.0, 1.0, 2.0]
}

class TestGapBuffer(unittest.TestCase):

    def test_init_empty(self):
        """Can we init for every typecode without exceptions?"""

        for typecode in VALID_CONTENT:
            gapbuffer(typecode)

    def test_init_content(self):
        """Can we init for every typecode with valid initial content?"""

        for typecode in VALID_CONTENT:
            gapbuffer(typecode, VALID_CONTENT[typecode])

    def test_init_content_generator(self):
        """Can we init for every typecode with valid initial content generator?
        """

        for typecode in VALID_CONTENT:
            gapbuffer(typecode,
                    (i for i in VALID_CONTENT[typecode]))

    def test_init_content_empty(self):
        """Can we init for every typecode with zero-length initial content?"""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, [])
            self.assertEqual(len(b), 0)

    def test_init_content_empty_generator(self):
        """Can we init for every typecode with an empty initial content
        generator?
        """

        for typecode in VALID_CONTENT:
            gapbuffer(typecode, (i for i in []))

    def test_init_char_content_wrong_type(self):
        """Does giving 'c' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but str are invalid for 'c'
        for typecode in VALID_CONTENT:
            if typecode != "c":
                with self.assertRaises(TypeError):
                    gapbuffer("c", VALID_CONTENT[typecode])

    def test_init_unicode_content_wrong_type(self):
        """Does giving 'u' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but unicode are invalid for 'u'
        for typecode in VALID_CONTENT:
            if typecode != "u":
                with self.assertRaises(TypeError):
                    gapbuffer("u", VALID_CONTENT[typecode])

    def test_typecode_property(self):
        """The typecode property should return the typecode used in init."""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])
            self.assertEqual(b.typecode, typecode)

    def test_context_manager_read(self):
        """Does using the context manager to read the raw buffer work?"""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])

            with b as raw_b:
                self.assertEqual(list(VALID_CONTENT[typecode]), raw_b.tolist())

    def test_context_manager_add(self):
        """Does using the context manager to add to the raw buffer work?"""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])

            # add content to the underlying buffer
            with b as raw_b:
                raw_b.extend(VALID_CONTENT[typecode])

            # see if the content is counted as part of the buffer
            self.assertEqual(VALID_CONTENT[typecode] * 2, b)

    def test_context_manager_delete(self):
        """Does using the context manager to pop from the raw buffer work?"""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])

            # add content to the underlying buffer
            with b as raw_b:
                raw_b.pop()

            # see if the content is counted as part of the buffer
            self.assertEqual(VALID_CONTENT[typecode][:-1], b)

    def test_eq(self):
        """Test all typecodes for equality to their respective initial content.
        """

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])
            self.assertEqual(VALID_CONTENT[typecode], b)

    def test_eq_infinite_other(self):
        """Test whether comparison correctly handles infinite iterables."""

        b = gapbuffer("i", [9, 9, 9, 9, 9])

        # an infinite generator that's identical (besides length) to our buffer
        def g():
            while 1:
                yield 9

        self.assertFalse(b == g())

    def test_eq_different_lengths(self):
        """Test all typecodes for inequality to similar, different-length
        content.
        """

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode])
            self.assertNotEqual(VALID_CONTENT[typecode] * 2, b)
            self.assertFalse(VALID_CONTENT[typecode] * 2 == b)

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode, VALID_CONTENT[typecode][:2])
            self.assertNotEqual(VALID_CONTENT[typecode], b)
            self.assertFalse(VALID_CONTENT[typecode] == b)

    def test_lt(self):
        """Does comparing buffers with '<' work?"""

        s1 = "abc"
        s2 = "acd"

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s1 < s2 and b1 < b2)

    def test_le(self):
        """Does comparing buffers with '<=' work?"""

        s1 = "abc"
        s2 = "acd"

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s1 < s2 and b1 < b2)

        s1 = "abc"
        s2 = s1

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s1 <= s2 and b1 <= b2)

    def test_gt(self):
        """Does comparing buffers with '>' work?"""

        s1 = "abc"
        s2 = "acd"

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s2 > s1 and b2 > b1)

    def test_ge(self):
        """Does comparing buffers with '>=' work?"""

        s1 = "abc"
        s2 = "acd"

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s2 >= s1 and b2 >= b1)

        s1 = "abc"
        s2 = s1

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertTrue(s2 >= s1 and b2 >= b1)

    def test_cmp_same_other_shorter(self):
        """Does comparing buffers work when the buffers are identical, besides
        their lengths?"""

        s1 = "abc"
        s2 = "ab"

        b1 = gapbuffer("c", s1)
        b2 = gapbuffer("c", s2)

        self.assertEqual(cmp(s1, s2), cmp(b1, b2))

    def test_cmp_same_other_infinite(self):
        """Does comparing buffers work when the buffers are identical, but the
        other iterable is infinite?"""

        # infinite sequence generator
        def g():
            while 1:
                yield "a"

        s1 = "aaaa"
        s2 = g()

        b1 = gapbuffer("c", s1)

        self.assertEqual(cmp(s1, s2), cmp(b1, s2))

    def test_in_nonstring(self):
        """Do non string-based buffers contain items that are in them?"""

        seq = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", seq)

        for i in seq:
            self.assertTrue(i in b)

        for i in xrange(6, 10):
            self.assertTrue(i not in b)

    def test_in_nonstring_added(self):
        """Do non string-based buffers contain items that are added to them?"""

        seq = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", seq)

        self.assertTrue(6 not in b)
        b.append(6)
        self.assertTrue(6 in b)

    def test_in_nonstring_deleted(self):
        """Do non string-based buffers contain items that are deleted from them?
        """

        seq = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", seq)

        self.assertTrue(0 in b)
        b.pop(0)
        self.assertTrue(0 not in b)

    def test_in_nonstring_sequece(self):
        """Do non string-based buffers contain sequences that are in them?"""

        seq = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", seq)

        self.assertTrue([0, 1] not in b)

    def test_in_string(self):
        """Do string-based buffers contain other string sequences?"""

        bc = gapbuffer("c", "hello, world!")
        bu = gapbuffer("u", u"hello, world!")

        for b in [bc, bu]:
            self.assertTrue("" in b)
            self.assertTrue("h" in b)
            self.assertTrue(u"h" in b)
            self.assertTrue("hello" in b)
            self.assertTrue(u"hello" in b)
            self.assertTrue("foo" not in b)
            self.assertTrue(u"foo" not in b)
            self.assertTrue(["f", "o", "o"] not in b)
            self.assertTrue([u"f", u"o", u"o"] not in b)

        self.assertTrue("" in gapbuffer("c"))
        self.assertTrue(u"" in gapbuffer("u"))

    def test_in_string_added(self):
        """Do string-based buffers contain sequences that are added to them?"""
        s = "hello, world!"
        b = gapbuffer("c", s)

        self.assertTrue("pants" not in b)
        b.extend(" pants")
        self.assertTrue("pants" in b)

        u = u"hello, world!"
        bu = gapbuffer("u", u)

        self.assertTrue(u"pants" not in bu)
        bu.extend(u" pants")
        self.assertTrue(u"pants" in bu)

    def test_in_string_deleted(self):
        """Do string-based buffers contain sequences that have been removed from
        them?
        """

        s = "hello, world!"
        b = gapbuffer("c", s)

        self.assertTrue("world" in b)
        del b[5:]
        self.assertTrue("world" not in b)

        u = u"hello, world!"
        bu = gapbuffer("u", u)

        self.assertTrue(u"world" in bu)
        del bu[5:]
        self.assertTrue(u"world" not in bu)

    def test_add(self):
        """Does concatenating like-typed buffers work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b + b, content + content)

    def test_add_non_gapbuffer(self):
        """Does concatenating non-gapbuffers work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b + content, content + content)

    def test_iadd(self):
        """Does concatenating like-typed buffers incrementally work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)
            b += b

            self.assertEqual(b, content + content)

    def test_iadd_non_gapbuffer(self):
        """Does concatenating non-gapbuffers incrementally work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)
            b += content

            self.assertEqual(b, content + content)

    def test_mul(self):
        """Does multiplying gapbuffers work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b * 0, [])
            self.assertEqual(b * 1, content)
            self.assertEqual(b * 2, content * 2)

            # this can't work since built-ins don't support gapbuffer
            with self.assertRaises(TypeError):
                0 * b

    def test_imul(self):
        """Does multiplying gapbuffers incrementally work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]

            b = gapbuffer(typecode, content)
            b *= 0
            self.assertEqual(b, [])

            b = gapbuffer(typecode, content)
            b *= 1
            self.assertEqual(b, content)

            b = gapbuffer(typecode, content)
            b *= 2
            self.assertEqual(b, content * 2)

    def test_len(self):
        """Does getting the length of a gapbuffer work?"""

        b = gapbuffer("i")

        self.assertEqual(0, len(b))
        b.append(0)
        self.assertEqual(1, len(b))
        b.extend([1, 2, 3, 4])
        self.assertEqual(5, len(b))
        del b[:]
        self.assertEqual(0, len(b))

    def test_min(self):
        """Does getting the min in a gapbuffer work?"""

        self.assertEqual(0, min(gapbuffer("i", [1, 2, 3, 0])))
        self.assertEqual(0, min(gapbuffer("i", [0, 0, 0, 0])))

        with self.assertRaises(ValueError):
            min(gapbuffer("i"))

    def test_max(self):
        """Does getting the max in a gapbuffer work?"""

        self.assertEqual(3, max(gapbuffer("i", [1, 2, 3, 0])))
        self.assertEqual(0, max(gapbuffer("i", [0, 0, 0, 0])))

        with self.assertRaises(ValueError):
            max(gapbuffer("i"))

    def test_index(self):
        """Does getting the index of an item in a gapbuffer work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b.index(content[0]), 0)

            # can't ever find a sequence since gapbuffers can't contain them
            with self.assertRaises(ValueError):
                b.index([])

    def test_count(self):
        """Does getting the index of an item in a gapbuffer work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(1, b.count(content[0]))

            # buffers can't contain sequences, so there are never more than zero
            self.assertEqual(0, b.count([]))

    def test_get_index(self):
        """Does getting an item at some index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            for i in xrange(len(content)):
                self.assertEqual(content[i], b[i])

    def test_get_index_negative(self):
        """Does getting an item at a negative index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            for i in xrange(1, len(content) + 1):
                self.assertEqual(content[-i], b[-i])

    def test_get_index_out_of_bounds(self):
        """Does getting an out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[len(b) + 1]

    def test_get_index_negative_out_of_bounds(self):
        """Does getting a negative out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[-(len(b) + 1)]

    def test_set_index(self):
        """Does setting an item at some index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            for index, item in enumerate(reversed(content)):
                b[index] = item
                self.assertEqual(item, b[index])

    def test_set_index_wrong_type(self):
        """Does setting an item at some index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(TypeError):
                b[0] = []

    def test_set_index_negative(self):
        """Does setting an item at a negative index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            for index, item in enumerate(content):
                b[-(index + 1)] = item

            self.assertEqual([i for i in reversed(content)], b)

    def test_set_index_out_of_bounds(self):
        """Does setting an out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[len(b) + 1] = VALID_CONTENT[typecode][0]

    def test_set_index_negative_out_of_bounds(self):
        """Does setting a negative out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[-(len(b) + 1)] = VALID_CONTENT[typecode][0]

    def test_del_index(self):
        """Does deleting an index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            del b[0]
            self.assertEqual(b, content[1:])

    def test_del_index_negative(self):
        """Does deleting a negative index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            del b[-1]
            self.assertEqual(b, content[:-1])

    def test_del_index_out_of_bounds(self):
        """Does deleting an out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            # can't delete out-of-bounds index
            with self.assertRaises(IndexError):
                del b[len(b) + 1]

    def test_del_index_negative_out_of_bounds(self):
        """Does deleting a negative out-of-bounds index work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            # can't delete out-of-bounds index
            with self.assertRaises(IndexError):
                del b[-(len(b) + 1)]

    def test_get_slice(self):
        """Does getting a slice work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b[:], content[:])
            self.assertEqual(b[1:], content[1:])
            self.assertEqual(b[-2:], content[-2:])
            self.assertEqual(b[len(b) * 2:], content[len(content) * 2:])

    def test_get_slice_extended(self):
        """Does getting an extended slice work?"""

        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b[::], content[::])
            self.assertEqual(b[::2], content[::2])
            self.assertEqual(b[1::2], content[1::2])
            self.assertEqual(b[2::2], content[2::2])
            self.assertEqual(b[::len(b)], content[::len(content)])

    def test_set_slice_empty(self):
        """Does setting an empty slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:3] = []
        content[1:3] = []

        self.assertEqual(b, content)

    def test_set_slice_generator(self):
        """Does setting a slice to a generator work?"""

        # sequence generator, has no __len__ method
        def g():
            for i in xrange(10):
                yield i

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:3] = g()
        content[1:3] = g()

        self.assertEqual(b, content)

    def test_set_slice_entire_range(self):
        """Does setting the entire range work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[:] = [9, 9, 9]
        content[:] = [9, 9, 9]

        self.assertEqual(b, content)

    def test_set_slice_after_end(self):
        """Does setting a slice past the end of the buffer work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[len(b) * 2:] = [9, 9, 9]
        content[len(content) * 2:] = [9, 9, 9]

        self.assertEqual(b, content)

    def test_set_slice_shorter(self):
        """Does setting a shorter-length slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:3] = [9]
        content[1:3] = [9]

        self.assertEqual(b, content)

    def test_set_slice_longer(self):
        """Does setting a longer-length slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:3] = [9, 9, 9, 9]
        content[1:3] = [9, 9, 9, 9]

        self.assertEqual(b, content)

    def test_set_slice_same_length(self):
        """Does setting an equivalent-length slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:3] = [9, 9]
        content[1:3] = [9, 9]

        self.assertEqual(b, content)

    def test_set_slice_empty_slice(self):
        """Does setting an empty slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[0:0] = [9]
        content[0:0] = [9]

        self.assertEqual(b, content)

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[1:1] = [9]
        content[1:1] = [9]

        self.assertEqual(b, content)

    def test_set_slice_extended_odd_length(self):
        """Does setting an extended slice on an odd-length buffer work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b[::2] = [9, 9, 9]
        content[::2] = [9, 9, 9]

        self.assertEqual(b, content)

    def test_set_slice_extended_even_length(self):
        """Does setting an extended slice on an even-length buffer work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b[::2] = [9, 9, 9]
        content[::2] = [9, 9, 9]

        self.assertEqual(b, content)

    def test_set_slice_extended_too_short(self):
        """Does setting a too-short extended slice on a buffer work?"""

        with self.assertRaises(ValueError):
            b = gapbuffer("i", [0, 1, 2, 3, 4])
            b[::2] = [9]

    def test_set_slice_extended_too_long(self):
        """Does setting a too-long extended slice on a buffer work?"""

        with self.assertRaises(ValueError):
            b = gapbuffer("i", [0, 1, 2, 3, 4])
            b[::2] = [9, 9, 9, 9, 9, 9, 9, 9]

    def test_del_slice(self):
        """Does deleting a slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        del b[1:3]
        del content[1:3]

        self.assertEqual(b, content)

    def test_del_slice_entire_range(self):
        """Does deleting the entire range work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        del b[:]
        del content[:]

        self.assertEqual(b, content)

    def test_del_slice_after_end(self):
        """Does deleting a slice after the end of the buffer work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        del b[len(b) * 2:]
        del content[len(content) * 2:]

        self.assertEqual(b, content)

    def test_del_slice_empty_slice(self):
        """Does deleting an empty slice work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        del b[0:0]
        del b[1:1]
        del content[0:0]
        del content[1:1]

        self.assertEqual(b, content)

    def test_del_slice_extended_odd_length(self):
        """Does deleting an extended slice on an odd-length buffer work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        del b[::2]
        del content[::2]

        self.assertEqual(b, content)

    def test_del_slice_extended_even_length(self):
        """Does deleting an extended slice on an even-length buffer work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        del b[::2]
        del content[::2]

        self.assertEqual(b, content)

    def test_del_slice_extended_very_large_range(self):
        """Does deleting an extended slice with a very large range work?"""

        # should only delete first item
        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        del b[::len(b) * 2]
        del content[::len(content) * 2]

        self.assertEqual(b, content)

    def test_del_slice_congruency(self):
        """Is deleting a slice equivalent to setting it to an empty slice?"""

        # entire range
        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[:] = []
        del b2[:]

        self.assertEqual(b1, b2)

        # sub-range
        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[1:3] = []
        del b2[1:3]

        self.assertEqual(b1, b2)

    def test_append(self):
        """Does appending an item work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        content.append(9)
        b.append(9)

        self.assertEqual(b, content)

    def test_extend(self):
        """Does extending with an iterable work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        content.extend([9, 9, 9])
        b.extend([9, 9, 9])

        self.assertEqual(b, content)

    def test_extend_with_self(self):
        """Does extending with self work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        content.extend(content)
        b.extend(b)

        self.assertEqual(b, content)

    def test_extend_empty(self):
        """Does extending with an empty iterable work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        content.extend([])
        b.extend([])

        self.assertEqual(b, content)

    def test_append_congruency(self):
        """Is appending an item the same as setting the final slice to a one-
        element list?
        """

        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[len(b1):len(b1)] = [9]
        b2.append(9)

        self.assertEqual(b1, b2)

    def test_extend_congruency(self):
        """Is extending a buffer the same as setting the final slice to an
        iterable?
        """

        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[len(b1):len(b1)] = [9, 9, 9]
        b2.extend([9, 9, 9])

        self.assertEqual(b1, b2)

    def test_count(self):
        """Does counting items work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.count(2), b.count(2))

    def test_count_string(self):
        """Does counting items in strings work?"""

        content = "hello, hello, helo"
        b = gapbuffer("c", content)

        self.assertEqual(content.count(""), b.count(""))
        self.assertEqual(content.count("h"), b.count("h"))
        self.assertEqual(content.count("hello"), b.count("hello"))
        self.assertEqual(content.count("helo"), b.count("helo"))
        self.assertEqual(content.count("foo"), b.count("foo"))

    def test_count_unicode(self):
        """Does counting items in unicode strings work?"""

        content = u"hello, hello, helo"
        b = gapbuffer("u", content)

        self.assertEqual(content.count(u""), b.count(u""))
        self.assertEqual(content.count(u"h"), b.count(u"h"))
        self.assertEqual(content.count(u"hello"), b.count(u"hello"))
        self.assertEqual(content.count(u"helo"), b.count(u"helo"))
        self.assertEqual(content.count(u"foo"), b.count(u"foo"))

    def test_count_multiples(self):
        """Does counting multiple items work?"""

        content = [0, 1, 3, 3, 3, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.count(3), b.count(3))

    def test_count_does_not_exist(self):
        """Does counting non-existing items work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.count(9), b.count(9))

    def test_count_wrong_type(self):
        """Does counting incorrectly-typed items work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.count([]), b.count([]))

    def test_index(self):
        """Does indexing items work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(2), b.index(2))

    def test_index_empty(self):
        """Does indexing items when the buffer is empty work?"""

        b = gapbuffer("i")

        with self.assertRaises(ValueError):
            b.index(0)

    def test_index_not_present(self):
        """Does indexing items when they aren't present work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        with self.assertRaises(ValueError):
            b.index(9)

    def test_index_wrong_type_not_present(self):
        """Does indexing items when they aren't present and are of the incorrect
        type work?
        """

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        with self.assertRaises(ValueError):
            b.index([])

    def test_index_multiple(self):
        """Does indexing items where there are duplicates work?"""

        content = [0, 1, 2, 3, 3, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3), b.index(3))

    def test_index_start_range(self):
        """Does indexing with a starting index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3, 2), b.index(3, 2))

    def test_index_start_range_negative(self):
        """Does indexing with a negative starting index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3, -3), b.index(3, -3))

    def test_index_start_range_negative_not_found(self):
        """Does indexing with a negative starting index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        with self.assertRaises(ValueError):
            content.index(3, -2)

        with self.assertRaises(ValueError):
            b.index(3, -2)

    def test_index_end_range(self):
        """Does indexing with a starting and ending index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3, 2, 4), b.index(3, 2, 4))

    def test_index_end_range_negative(self):
        """Does indexing with a starting and negative ending index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3, 2, -2), b.index(3, 2, -2))

        # both should fail to find the item, but not raise other errors
        with self.assertRaises(ValueError):
            content.index(3, 0, -4)

        with self.assertRaises(ValueError):
            b.index(3, 0, -4)

    def test_index_end_range_negative_not_found(self):
        """Does indexing with a starting and negative ending index work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        self.assertEqual(content.index(3, 2, -2), b.index(3, 2, -2))

    def test_index_end_range_negative_out_of_bounds(self):
        """Does indexing with a starting and negative, out-of-bounds ending
        index work?
        """

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        # both should fail to find the item, but not raise other errors
        with self.assertRaises(ValueError):
            content.index(0, 0, -(len(content) * 2))

        with self.assertRaises(ValueError):
            b.index(0, 0, -(len(b) * 2))

    def test_insert(self):
        """Does insert work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b.insert(0, 9)
        content.insert(0, 9)

        self.assertEqual(b, content)

    def test_insert_into_empty(self):
        """Does insertion into an empty buffer work?"""

        content = []
        b = gapbuffer("i")

        b.insert(0, 9)
        content.insert(0, 9)

        self.assertEqual(b, content)

    def test_insert_wrong_type(self):
        """Does insert work when the type is incorrect?"""

        b = gapbuffer("i")
        with self.assertRaises(TypeError):
            b.insert(0, [])

    def test_insert_out_of_bounds(self):
        """Does insert work when the index is out-of-bounds?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b.insert(len(b) * 2, 9)
        content.insert(len(content) * 2, 9)

        self.assertEqual(b, content)

    def test_insert_negative(self):
        """Does insert work when the index is negative?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b.insert(-2, 9)
        content.insert(-2, 9)

        self.assertEqual(b, content)

    def test_insert_negative_out_of_bounds(self):
        """Does insert work when the index is negative and out-of-bounds?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b.insert(-(len(b) * 2), 9)
        content.insert(-(len(content) * 2), 9)

        self.assertEqual(b, content)

    def test_insert_congruency(self):
        """Is insert congruent to setting a zero-length slice?"""

        b1 = gapbuffer("i", [0, 1, 2, 3, 4])
        b2 = gapbuffer("i", b1)

        b1.insert(0, 9)
        b2[0:0] = [9]

        self.assertEqual(b1, b2)

    def test_pop_no_arg(self):
        """Does pop work without an index argument?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        bp = b.pop()
        cp = content.pop()

        self.assertEqual(bp, cp)
        self.assertEqual(b, content)

    def test_pop_index_zero(self):
        """Does pop work with the 0 index argument?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        bp = b.pop(0)
        cp = content.pop(0)

        self.assertEqual(bp, cp)
        self.assertEqual(b, content)

    def test_pop_index_negone(self):
        """Does pop work with the -1 index argument?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        bp = b.pop(-1)
        cp = content.pop(-1)

        self.assertEqual(bp, cp)
        self.assertEqual(b, content)

    def test_pop_index_negone(self):
        """Does pop work with a negative index argument?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        bp = b.pop(-3)
        cp = content.pop(-3)

        self.assertEqual(bp, cp)
        self.assertEqual(b, content)

    def test_pop_index_non_zero(self):
        """Does pop work with a non-zero index argument?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        bp = b.pop(3)
        cp = content.pop(3)

        self.assertEqual(bp, cp)
        self.assertEqual(b, content)

    def test_pop_default(self):
        """Does the no-arg pop work the same as pop with a -1 index argument?"""

        b1 = gapbuffer("i", [0, 1, 2, 3, 4])
        b2 = gapbuffer("i", b1)

        bp1 = b1.pop(-1)
        bp2 = b2.pop()

        self.assertEqual(bp1, bp2)
        self.assertEqual(b1, b2)

    def test_pop_index_out_of_bounds(self):
        """Does pop work with an out-of-bounds index?"""

        b = gapbuffer("i", [0, 1, 2, 3, 4])
        with self.assertRaises(IndexError):
            b.pop(len(b) + 1)

    def test_pop_index_negative_out_of_bounds(self):
        """Does pop work with a negative out-of-bounds index?"""

        b = gapbuffer("i", [0, 1, 2, 3, 4])
        with self.assertRaises(IndexError):
            b.pop(-(len(b) + 1))

    def test_pop_empty(self):
        """Does pop work on an empty buffer?"""

        for typecode in VALID_CONTENT:
            b = gapbuffer(typecode)
            with self.assertRaises(IndexError):
                b.pop()

    def test_pop_congruency(self):
        """Is pop congruent to saving an index, then deleting it?"""

        b1 = gapbuffer("i", [0, 1, 2, 3, 4])
        b2 = gapbuffer("i", b1)

        bp1 = b1.pop(1)
        bp2 = b2[1]
        del b2[1]

        self.assertEqual(bp1, bp2)
        self.assertEqual(b1, b2)

    def test_remove(self):
        """Does remove work?"""

        content = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", content)

        b.remove(3)
        content.remove(3)

        self.assertEqual(b, content)

    def test_remove_multiple_items_only_first(self):
        """Does remove only remove the first item when there are duplicates?"""

        content = [0, 1, 2, 3, 4, 3]
        b = gapbuffer("i", content)

        b.remove(3)
        content.remove(3)

        self.assertEqual(b[-1], 3)
        self.assertEqual(content[-1], 3)

        self.assertEqual(b, content)

    def test_remove_not_present(self):
        """Does remove work when the item isn't present?"""

        b = gapbuffer("i", [0, 1, 2, 3, 4])
        with self.assertRaises(ValueError):
            b.remove(9)

    def test_remove_congruency(self):
        """Is remove congruent to deleting an item found by index?"""

        b1 = gapbuffer("i", [0, 1, 2, 3, 4])
        b2 = gapbuffer("i", b1)

        b1.remove(2)
        del b2[b2.index(2)]

        self.assertEqual(b1, b2)

    def test_reverse(self):
        """Does in-place reverse work?"""

        content = [0, 1, 2, 3, 4]
        b = gapbuffer("i", content)

        b.reverse()
        content.reverse()

        self.assertEqual(b, content)

    def test_reverse_empty(self):
        """Does in-place reverse work when the buffer is empty?"""

        content = []
        b = gapbuffer("i", content)

        b.reverse()
        content.reverse()

        self.assertEqual(b, content)

    def test_reverse_single_item(self):
        """Does in-place reverse work when the buffer has only one item?"""

        content = [0]
        b = gapbuffer("i", content)

        b.reverse()
        content.reverse()

        self.assertEqual(b, content)

    def test_reverse_even_items(self):
        """Does in-place reverse work when the buffer has an even number of
        items?
        """

        content = [0, 1, 2, 3]
        b = gapbuffer("i", content)

        b.reverse()
        content.reverse()

        self.assertEqual(b, content)

    def test_reverse_odd_items(self):
        """Does in-place reverse work when the buffer has an odd number of
        items?
        """

        content = [0, 1, 2]
        b = gapbuffer("i", content)

        b.reverse()
        content.reverse()

        self.assertEqual(b, content)

    def test_reverse_congruency(self):
        """Does reversing yield the same sequence as the reverse iterator?"""

        b1 = gapbuffer("i", [0, 1, 2, 3, 4])
        b2 = gapbuffer("i", b1)

        b2.reverse()

        self.assertEqual([i for i in reversed(b1)], b2)

    def test_str(self):
        """Does __str__ work?"""
        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            self.assertTrue(str(gapbuffer(typecode, content)) is not None)

    def test_unicode(self):
        """Does __unicode__ work?"""
        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            self.assertTrue(unicode(gapbuffer(typecode, content)) is not None)

    def test_repr(self):
        """Does __repr__ work?"""
        for typecode in VALID_CONTENT:
            content = VALID_CONTENT[typecode]
            self.assertTrue(repr(gapbuffer(typecode, content)) is not None)
            self.assertTrue(repr(gapbuffer(typecode, ())) is not None)

    def test_move_gap(self):
        """Does moving the gap work?"""

        # add to the beginning, to make sure the gap is at the beginning
        gap_size = 3
        b = gapbuffer("i", range(5), gap_size=gap_size)
        b.insert(0, -1)

        # extend with an empty iterable, to force a gap move to the end
        b.extend([])

        self.assertEqual(b, [-1] + range(5))

    def test_move_gap_zero_length(self):
        """Does moving a zero-length gap work?"""

        # fill the gap from the beginning so it has no space left, forcing the
        # gap to be at the start of the buffer.
        gap_size = 3
        b = gapbuffer("i", range(5), gap_size=gap_size)
        [b.insert(0, -1) for i in xrange(gap_size)]

        # extend with an empty iterable, to force a gap move to the end
        b.extend([])

        self.assertEqual(b, ([-1] * gap_size) + range(5))

    def test_resize_gap(self):
        """Does increasing the gap size work?"""

        gap_size = 3
        b = gapbuffer("i", range(5), gap_size=gap_size)

        # gap should resize if more items are added than spaces it contains
        [b.insert(0, -1) for i in xrange(gap_size + 1)]

        self.assertEqual(b, ([-1] * (gap_size + 1)) + range(5))

    def test_resize_gap_during_extend(self):
        """Does increasing the gap size during extend() work?"""

        gap_size = 3
        b = gapbuffer("i", range(5), gap_size=gap_size)

        b.extend([-1] * (gap_size + 1))

        self.assertEqual(b, range(5) + ([-1] * (gap_size + 1)))

    def test_resize_gap_multiple_times(self):
        """Does increasing the gap size so it must resize several times work?"""

        gap_size = 3
        b = gapbuffer("i", range(5), gap_size=gap_size)

        b.extend([-1] * (gap_size * 4))

        self.assertEqual(b, range(5) + ([-1] * (gap_size * 4)))

if __name__ == "__main__":
    import sys

    # generate coverage data if coverage module is available
    try:
        from coverage import coverage
        cov = coverage(config_file=False, branch=True, omit=["test_*.py"])
        cov.start()
    except ImportError:
        cov = None

    # imported here so coverage can catch the function/class definitions
    from gapbuffer import gapbuffer

    suite = unittest.TestLoader().loadTestsFromTestCase(TestGapBuffer)
    unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

    # end coverage and generate a report if coverage was loaded
    if cov is not None:
        cov.stop()
        cov.html_report(directory="htmlcov")
