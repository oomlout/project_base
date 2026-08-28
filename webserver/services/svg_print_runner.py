from __future__ import annotations

import subprocess
import sys
import time
import traceback
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


WAIT_SECONDS = 30
PRINT_SERVER_BASE_URL = "http://192.168.1.230:5678/print"


def _log(message: str) -> None:
    print(message, flush=True)


def _build_print_server_url(download_url: str, printer_name: str) -> str:
    query = urlencode({"filename": download_url, "printer_name": printer_name})
    return f"{PRINT_SERVER_BASE_URL}?{query}"


def _convert_svg_to_pdf(svg_path: Path, pdf_path: Path) -> None:
    command = ["inkscape", str(svg_path), f"--export-filename={pdf_path}"]
    _log("[1/3] Converting SVG to PDF")
    _log(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected PDF was not created: {pdf_path}")
    _log(f"Created PDF: {pdf_path}")


def _trigger_print(print_url: str) -> None:
    _log("[2/3] Triggering print URL")
    _log(print_url)
    with urlopen(print_url) as response:
        status_code = getattr(response, "status", response.getcode())
        response_body = response.read(200).decode("utf-8", errors="replace").strip()
    _log(f"Print server response: HTTP {status_code}")
    if response_body:
        _log(response_body)


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        _log("Usage: svg_print_runner.py <svg_input> <pdf_output> <download_url> <printer_name>")
        _log(f"Window closes in {WAIT_SECONDS} seconds.")
        time.sleep(WAIT_SECONDS)
        return 2

    svg_path = Path(argv[1]).resolve()
    pdf_path = Path(argv[2]).resolve()
    download_url = argv[3]
    printer_name = argv[4]
    print_url = _build_print_server_url(download_url, printer_name)

    _log(f"SVG input: {svg_path}")
    _log(f"PDF output: {pdf_path}")
    _log(f"Printer: {printer_name}")

    if not svg_path.exists():
        _log(f"Input SVG does not exist: {svg_path}")
        _log(f"Window closes in {WAIT_SECONDS} seconds.")
        time.sleep(WAIT_SECONDS)
        return 1

    try:
        _convert_svg_to_pdf(svg_path, pdf_path)
        _trigger_print(print_url)
        _log("[3/3] Done")
        return 0
    except subprocess.CalledProcessError as exc:
        _log(f"SVG to PDF conversion failed with exit code {exc.returncode}.")
        return exc.returncode or 1
    except HTTPError as exc:
        _log(f"Print request failed with HTTP {exc.code}: {exc.reason}")
        return 1
    except URLError as exc:
        _log(f"Print request failed: {exc.reason}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        _log(f"Window closes in {WAIT_SECONDS} seconds.")
        time.sleep(WAIT_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))