from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


def _escape_annotation(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


class GitHubTextResult(unittest.TextTestResult):
    def _annotate(self, kind: str, test: unittest.case.TestCase, err) -> None:
        test_id = getattr(test, "id", lambda: str(test))()
        detail = self._exc_info_to_string(err, test)
        compact = detail[-6000:]
        print(
            f"::{kind} title={_escape_annotation(test_id)}::{_escape_annotation(compact)}",
            flush=True,
        )

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._annotate("error", test, err)

    def addError(self, test, err):
        super().addError(test, err)
        self._annotate("error", test, err)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        test_id = getattr(test, "id", lambda: str(test))()
        print(
            f"::error title={_escape_annotation(test_id)}::Unexpected success",
            flush=True,
        )

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._annotate("error", subtest, err)


def _write_summary(result: GitHubTextResult) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    failures = [("FAIL", test, err) for test, err in result.failures]
    errors = [("ERROR", test, err) for test, err in result.errors]
    with Path(summary_path).open("a", encoding="utf-8") as fh:
        fh.write("## Harmonia Studio test results\n\n")
        fh.write(
            f"- Tests run: **{result.testsRun}**\n"
            f"- Failures: **{len(result.failures)}**\n"
            f"- Errors: **{len(result.errors)}**\n\n"
        )
        for label, test, err in failures + errors:
            test_id = getattr(test, "id", lambda: str(test))()
            fh.write(f"### {label}: `{test_id}`\n\n")
            fh.write("```text\n")
            fh.write(err[-6000:])
            fh.write("\n```\n\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=2,
        resultclass=GitHubTextResult,
    )
    result = runner.run(suite)
    _write_summary(result)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
