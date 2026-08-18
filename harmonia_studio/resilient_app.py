from __future__ import annotations

import os

from .crash_reporting import run_tk_app
from .professional_shell_app import ProfessionalShellHarmoniaApp


def main() -> int:
    if os.environ.get("HARMONIA_WORKFLOW_SMOKE", "").strip() == "1":
        from .workflow_smoke_app import WorkflowSmokeHarmoniaApp

        return run_tk_app(
            WorkflowSmokeHarmoniaApp,
            smoke_env="HARMONIA_WORKFLOW_SMOKE",
            report_env="HARMONIA_WORKFLOW_REPORT",
            auto_close=False,
            write_success_report=False,
        )
    return run_tk_app(ProfessionalShellHarmoniaApp)


if __name__ == "__main__":
    raise SystemExit(main())
