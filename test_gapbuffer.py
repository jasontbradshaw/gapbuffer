#!/usr/bin/env python

import unittest
from gapbuffer import gapbuffer

class TestGapBuffer(unittest.TestCase):
    def setUp(self):
        # correct content for each typecode
        self.valid_content = {
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

    def test_init_empty(self):
        """Can we init for every typecode without exceptions?"""

        for typecode in self.valid_content:
            gapbuffer(typecode)

    def test_init_content(self):
        """Can we init for every typecode with valid initial content?"""

        for typecode in self.valid_content:
            gapbuffer(typecode, self.valid_content[typecode])

    def test_init_content_generator(self):
        """Can we init for every typecode with valid initial content generator?
        """

        for typecode in self.valid_content:
            gapbuffer(typecode,
                    (i for i in self.valid_content[typecode]))

    def test_init_content_empty(self):
        """Can we init for every typecode with zero-length initial content?"""

        for typecode in self.valid_content:
            b = gapbuffer(typecode, [])
            self.assertEqual(len(b), 0)

    def test_init_content_empty_generator(self):
        """Can we init for every typecode with an empty initial content
        generator?
        """

        for typecode in self.valid_content:
            gapbuffer(typecode, (i for i in []))

    def test_init_char_content_wrong_type(self):
        """Does giving 'c' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but str are invalid for 'c'
        for typecode in self.valid_content:
            if typecode != "c":
                with self.assertRaises(TypeError):
                    gapbuffer("c", self.valid_content[typecode])

    def test_init_unicode_content_wrong_type(self):
        """Does giving 'u' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but unicode are invalid for 'u'
        for typecode in self.valid_content:
            if typecode != "u":
                with self.assertRaises(TypeError):
                    gapbuffer("u", self.valid_content[typecode])

    def test_eq(self):
        """Test all typecodes for equality to their respective initial content.
        """

        for typecode in self.valid_content:
            b = gapbuffer(typecode, self.valid_content[typecode])
            self.assertEqual(self.valid_content[typecode], b)

    def test_eq_different_lengths(self):
        """Test all typecodes for inequality to similar, different-length
        content.
        """

        for typecode in self.valid_content:
            b = gapbuffer(typecode, self.valid_content[typecode])
            self.assertNotEqual(self.valid_content[typecode] * 2, b)

        for typecode in self.valid_content:
            b = gapbuffer(typecode, self.valid_content[typecode][:2])
            self.assertNotEqual(self.valid_content[typecode], b)

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
        b.pop()
        self.assertTrue(0 not in b)

    def test_in_nonstring_sequece(self):
        """Do non string-based buffers contain sequences that are in them?"""

        seq = [0, 1, 2, 3, 4, 5]
        b = gapbuffer("i", seq)

        self.assertTrue([0, 1] not in b)

    def test_in_string(self):
        """Do string-based buffers contain other string sequences?"""

        s = "hello, world!"
        b = gapbuffer("c", s)

        self.assertTrue("h" in b)
        self.assertTrue("hello" in b)
        self.assertTrue(u"hello" in b)
        self.assertTrue("foo" not in b)

        u = u"hello, world!"
        bu = gapbuffer("u", u)

        self.assertTrue(u"h" in bu)
        self.assertTrue(u"hello" in bu)
        self.assertTrue("hello" in bu)
        self.assertTrue(u"foo" not in bu)

    def test_in_string_added(self):
        """Do string-based buffers contain sequences that are added to them?"""
        s = "hello, world!"
        b = gapbuffer("c", s)

        self.assertTrue("pants" not in b)
        b.extend(" pants")
        self.assertTrue("pants" in b)

        u = u"hello, world!"
        bu = gapbuffer("u", u)

        self.assertTrue(u"pants" not in b)
        bu.extend(u" pants")
        self.assertTrue(u"pants" in b)

    def test_in_string_deleted(self):
        """Do string-based buffers contain sequences that have been removed from
        them?
        """

        s = "hello, world!"
        b = gapbuffer("c", s)

        self.assertTrue("world" in b)
        del b[4:]
        self.assertTrue("world" not in b)

        u = u"hello, world!"
        bu = gapbuffer("u", u)

        self.assertTrue(u"world" in bu)
        del b[4:]
        self.assertTrue(u"world" not in bu)

    def test_add(self):
        """Does concatenating like-typed buffers work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b + b, content + content)

    def test_add_non_gapbuffer(self):
        """Does concatenating non-gapbuffers work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b + content, content + content)

    def test_multiply(self):
        """Does multiplying gapbuffers work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b * 0, [])
            self.assertEqual(b * 1, content)
            self.assertEqual(b * 2, content * 2)

            self.assertEqual(1 * b, content)
            self.assertEqual(0 * b, [])
            self.assertEqual(2 * b, content * 2)

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

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b.index(content[0]), 0)

            # can't ever find a sequence since gapbuffers can't contain them
            with self.assertRaises(ValueError):
                b.index([])

    def test_count(self):
        """Does getting the index of an item in a gapbuffer work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(1, b.count(content[0]))

            # buffers can't contain sequences, so there are never more than zero
            self.assertEqual(0, b.count([]))

    def test_get_index(self):
        """Does getting an item at some index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            for i in xrange(len(content)):
                self.assertEqual(content[i], b[i])

    def test_get_index_negative(self):
        """Does getting an item at a negative index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            for i in xrange(1, len(content) + 1):
                self.assertEqual(content[-i], b[-i])

    def test_get_index_out_of_bounds(self):
        """Does getting an out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[len(b) + 1]

    def test_get_index_negative_out_of_bounds(self):
        """Does getting a negative out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[-(len(b) + 1)]

    def test_set_index(self):
        """Does setting an item at some index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            for index, item in enumerate(reversed(content)):
                b[index] = item
                self.assertEqual(item, b[index])

    def test_set_index_negative(self):
        """Does setting an item at a negative index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            for index, item in enumerate(reversed(content)):
                b[-(index + 1)] = item

            self.assertEqual(reversed(content), b)

    def test_set_index_out_of_bounds(self):
        """Does setting an out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[len(b) + 1] = item

    def test_set_index_negative_out_of_bounds(self):
        """Does setting a negative out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            with self.assertRaises(IndexError):
                b[-(len(b) + 1)] = item

    def test_del_index(self):
        """Does deleting an index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            del b[0]
            self.assertEqual(b, content[1:])

    def test_del_index_negative(self):
        """Does deleting a negative index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            del b[-1]
            self.assertEqual(b, content[:-1])

    def test_del_index_out_of_bounds(self):
        """Does deleting an out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            # can't delete out-of-bounds index
            with self.assertRaises(IndexError):
                del b[len(b) + 1]

    def test_del_index_negative_out_of_bounds(self):
        """Does deleting a negative out-of-bounds index work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            # can't delete out-of-bounds index
            with self.assertRaises(IndexError):
                del b[-(len(b) + 1)]

    def test_get_slice(self):
        """Does getting a slice work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
            b = gapbuffer(typecode, content)

            self.assertEqual(b[:], content[:])
            self.assertEqual(b[1:], content[1:])
            self.assertEqual(b[-2:], content[-2:])
            self.assertEqual(b[len(b) * 2:], content[len(content) * 2:])

    def test_get_slice_extended(self):
        """Does getting an extended slice work?"""

        for typecode in self.valid_content:
            content = self.valid_content[typecode]
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
        """Does deleting an extended slice with a very larger range work?"""

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

    def test_del_slice_extended_congruency(self):
        """Is deleting an extended slice equivalent to setting it to an empty
        slice?
        """

        # entire range
        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[::] = []
        del b2[::]

        self.assertEqual(b1, b2)

        # sub-range
        b1 = gapbuffer("i", [0, 1, 2, 3, 4, 5])
        b2 = gapbuffer("i", b1)

        b1[::2] = []
        del b2[::2]

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

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGapBuffer)
    unittest.TextTestRunner(verbosity=2).run(suite)
