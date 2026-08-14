import os
import unittest
from unittest.mock import patch

from harmonia_studio.crash_reporting import format_exception_text, run_tk_app


class FakeTkApp:
    instances = []

    def __init__(self):
        self.destroyed = False
        self.scheduled = []
        self.report_callback_exception = None
        self.__class__.instances.append(self)

    def after(self, delay, callback):
        self.scheduled.append((delay, callback))

    def after_idle(self, callback):
        callback()

    def destroy(self):
        self.destroyed = True

    def mainloop(self):
        for _delay, callback in list(self.scheduled):
            callback()


class CallbackFailureApp(FakeTkApp):
    def mainloop(self):
        self.report_callback_exception(ValueError, ValueError("callback boom"), None)


class StartupFailureApp:
    def __init__(self):
        raise RuntimeError("startup boom")


class CrashReportingTests(unittest.TestCase):
    def test_format_exception_contains_type_and_message(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            text = format_exception_text(*sys.exc_info())
        self.assertIn("ValueError", text)
        self.assertIn("boom", text)

    def test_smoke_mode_auto_closes_clean_app(self):
        FakeTkApp.instances.clear()
        with patch.dict(os.environ, {"HARMONIA_STARTUP_SMOKE": "1"}, clear=False):
            result = run_tk_app(FakeTkApp)
        self.assertEqual(result, 0)
        self.assertTrue(FakeTkApp.instances[-1].destroyed)

    def test_callback_exception_fails_smoke_run(self):
        with patch.dict(os.environ, {"HARMONIA_STARTUP_SMOKE": "1"}, clear=False):
            result = run_tk_app(CallbackFailureApp)
        self.assertEqual(result, 1)

    def test_startup_exception_returns_nonzero(self):
        with patch.dict(os.environ, {"HARMONIA_STARTUP_SMOKE": "1"}, clear=False):
            result = run_tk_app(StartupFailureApp)
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
