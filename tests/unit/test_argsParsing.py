# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2026 NV Access Limited

"""Unit tests for the argsParsing module."""

import argparse
import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import argsParsing
from argsParsing import logLevelFromString
from config.configFlags import LoggingLevel


class TestLogLevelFromString(unittest.TestCase):
	def test_namesAccepted(self):
		expectations = {
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
		for value in ("nonsense", "25", "", "true", "secrets"):
			with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
				logLevelFromString(value)

	def test_namesMatchConfigLevels(self):
		"""The accepted names must stay in step with the names used by general.loggingLevel."""
		expected = {level.name.casefold(): level.value for level in LoggingLevel}
		self.assertEqual(argsParsing._LOG_LEVEL_NAMES, expected)


class TestLogLevelArgument(unittest.TestCase):
	def test_parserAcceptsName(self):
		args, _ = argsParsing.getParser().parse_known_args(["--log-level=info"])
		self.assertEqual(args.logLevel, 20)

	def test_parserRejectsInvalid(self):
		with tempfile.TemporaryDirectory() as tmpDir:
			with (
				mock.patch.object(argsParsing.tempfile, "gettempdir", return_value=tmpDir),
				mock.patch.object(argsParsing.winUser, "MessageBox"),
				contextlib.redirect_stderr(io.StringIO()),
				self.assertRaises(SystemExit) as cm,
			):
				argsParsing.getParser().parse_known_args(["--log-level=nonsense"])
			self.assertEqual(cm.exception.code, 2)


class TestNoConsoleOptionParserError(unittest.TestCase):
	def test_errorRecordsDiagnostics(self):
		parser = argsParsing.NoConsoleOptionParser(prog="nvda")
		with tempfile.TemporaryDirectory() as tmpDir:
			with (
				mock.patch.object(argsParsing.tempfile, "gettempdir", return_value=tmpDir),
				mock.patch.object(argsParsing.winUser, "MessageBox") as messageBox,
			):
				stderr = io.StringIO()
				with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
					parser.error("boom")
			self.assertEqual(cm.exception.code, 2)
			with open(os.path.join(tmpDir, "nvda-cli-error.log"), encoding="utf-8") as f:
				recorded = f.read()
			self.assertIn("error: boom", recorded)
			self.assertEqual(recorded.rstrip("\n"), stderr.getvalue().rstrip("\n"))
			self.assertIn(os.path.join(tmpDir, "nvda-cli-error.log"), messageBox.call_args.args[1])
