# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2026 NV Access Limited

"""Unit tests for the argsParsing module."""

import argparse
import unittest

from argsParsing import logLevelFromString


class TestLogLevelFromString(unittest.TestCase):
	def test_namesAccepted(self):
		expectations = {
			"secrets": 5,
			"debug_unredacted": 5,
			"DEBUG": 10,
			"io": 12,
			"debugWarning": 15,
			"info": 20,
			"off": 100,
		}
		for name, level in expectations.items():
			with self.subTest(name=name):
				self.assertEqual(logLevelFromString(name), level)

	def test_numbersAccepted(self):
		for value in ("5", "10", "12", "15", "20", "100"):
			with self.subTest(value=value):
				self.assertEqual(logLevelFromString(value), int(value))

	def test_invalidRejected(self):
		for value in ("nonsense", "25", "", "true"):
			with self.subTest(value=value):
				with self.assertRaises(argparse.ArgumentTypeError):
					logLevelFromString(value)
