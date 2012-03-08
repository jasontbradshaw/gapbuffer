#!/usr/bin/env python

import unittest
import gapbuffer

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
            gapbuffer.gapbuffer(typecode)

    def test_init_content(self):
        """Can we init for every typecode with valid initial content?"""

        for typecode in self.valid_content:
            gapbuffer.gapbuffer(typecode, self.valid_content[typecode])

    def test_init_content_generator(self):
        """Can we init for every typecode with valid initial content generator?
        """

        for typecode in self.valid_content:
            gapbuffer.gapbuffer(typecode,
                    (i for i in self.valid_content[typecode]))

    def test_init_content_empty(self):
        """Can we init for every typecode with zero-length initial content?"""

        for typecode in self.valid_content:
            b = gapbuffer.gapbuffer(typecode, [])
            self.assertEqual(len(b), 0)

    def test_init_content_empty_generator(self):
        """Can we init for every typecode with an empty initial content
        generator?
        """

        for typecode in self.valid_content:
            gapbuffer.gapbuffer(typecode, (i for i in []))

    def test_init_char_content_wrong_type(self):
        """Does giving 'c' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but str are invalid for 'c'
        for typecode in self.valid_content:
            if typecode != "c":
                with self.assertRaises(TypeError):
                    gapbuffer.gapbuffer("c", self.valid_content[typecode])

    def test_init_unicode_content_wrong_type(self):
        """Does giving 'u' typecode buffers incorrect types raise the correct
        exceptions?
        """

        # all types but unicode are invalid for 'u'
        for typecode in self.valid_content:
            if typecode != "u":
                with self.assertRaises(TypeError):
                    gapbuffer.gapbuffer("u", self.valid_content[typecode])

    def test_eq(self):
        """Test all typecodes for equality to their respective initial content.
        """

        for typecode in self.valid_content:
            b = gapbuffer.gapbuffer(typecode, self.valid_content[typecode])
            self.assertEqual(self.valid_content[typecode], b)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGapBuffer)
    unittest.TextTestRunner(verbosity=2).run(suite)
