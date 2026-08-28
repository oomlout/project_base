from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlencode


CommandBuilder = Callable[[Path, Path], list[str]]


@dataclass(frozen=True)
class FileActionInvocation:
    mode: str
    command: list[str] | None = None
    cwd: Path | None = None
    target_path: Path | None = None
    additional_commands: tuple[list[str], ...] = ()
    print_server_printer_name: str | None = None


@dataclass(frozen=True)
class FileActionDefinition:
    id: str
    label: str
    suffixes: tuple[str, ...]
    output_suffix: str | None = None
    command_builder: CommandBuilder | None = None
    additional_command_builders: tuple[CommandBuilder, ...] = ()
    destructive: bool = False
    icon: str | None = None
    button_variant: str = "ghost"
    confirm_message_template: str | None = None
    print_server_printer_selection: int | None = None
    print_server_printer_name: str | None = None
    convert_svg_before_print: bool = False
    legend_group: str | None = None

    def applies_to(self, file_path: Path) -> bool:
        if not self.suffixes:
            return True
        return file_path.suffix.lower() in self.suffixes

    def build_output_path(self, source_path: Path) -> Path | None:
        if self.output_suffix is None:
            return None
        return source_path.with_suffix(self.output_suffix)

    def build_command(self, source_path: Path) -> list[str]:
        if self.command_builder is None:
            raise ValueError(f"Action {self.id} does not define a command builder.")
        output_path = self.build_output_path(source_path)
        if output_path is None:
            raise ValueError(f"Action {self.id} does not define an output path.")
        return self.command_builder(source_path, output_path)

    def build_invocation(self, source_path: Path) -> FileActionInvocation:
        output_path = self.build_output_path(source_path)
        if self.convert_svg_before_print and self.print_server_printer_name is not None:
            pdf_path = source_path.with_suffix(".pdf")
            return FileActionInvocation(
                mode="svg-print",
                command=_inkscape_pdf_command(source_path, pdf_path),
                cwd=source_path.parent,
                target_path=pdf_path,
                print_server_printer_name=self.print_server_printer_name,
            )
        if self.print_server_printer_selection is not None:
            return FileActionInvocation(mode="external-link", target_path=source_path)
        if self.command_builder is not None:
            additional = tuple(
                builder(source_path, source_path.with_suffix(".png") if output_path is None else output_path.with_suffix(".png"))
                for builder in self.additional_command_builders
            )
            return FileActionInvocation(
                mode="launch",
                command=self.build_command(source_path),
                cwd=source_path.parent,
                target_path=output_path,
                additional_commands=additional,
            )
        return FileActionInvocation(
            mode="delete",
            target_path=source_path,
        )

    def build_confirm_message(self, source_path: Path, base_dir: Path | None = None) -> str | None:
        if not self.confirm_message_template:
            return None

        relative_path = source_path.name
        if base_dir is not None:
            try:
                relative_path = source_path.relative_to(base_dir).as_posix()
            except ValueError:
                relative_path = source_path.name
        return self.confirm_message_template.format(relative_path=relative_path)

    def describe(self, source_path: Path, base_dir: Path | None = None) -> dict[str, str | bool | int]:
        output_path = self.build_output_path(source_path)
        target_relative_path = ""
        target_name = ""
        output_exists = False
        if output_path is not None:
            target_relative_path = output_path.name
            if base_dir is not None:
                try:
                    target_relative_path = output_path.relative_to(base_dir).as_posix()
                except ValueError:
                    target_relative_path = output_path.name
            target_name = output_path.name
            output_exists = output_path.exists()

        return {
            "id": self.id,
            "label": self.label,
            "target_relative_path": target_relative_path,
            "target_name": target_name,
            "output_exists": output_exists,
            "destructive": self.destructive,
            "icon": self.icon or "",
            "button_variant": self.button_variant,
            "confirm_message": self.build_confirm_message(source_path, base_dir) or "",
            "print_server_printer_selection": self.print_server_printer_selection or "",
            "print_server_printer_name": self.print_server_printer_name or "",
            "convert_svg_before_print": self.convert_svg_before_print,
            "legend_group": self.legend_group or "",
        }


def _openscad_stl_command(source_path: Path, output_path: Path) -> list[str]:
    return ["openscad", "-o", str(output_path), str(source_path)]


def _openscad_png_command(source_path: Path, output_path: Path) -> list[str]:
    return ["openscad", "--render", "-o", str(output_path), str(source_path)]


def _inkscape_pdf_command(source_path: Path, output_path: Path) -> list[str]:
    return ["inkscape", str(source_path), f"--export-filename={output_path}"]


def build_print_server_url(download_url: str, printer_name: str) -> str:
    query = urlencode({"filename": download_url, "printer_name": printer_name})
    return f"http://192.168.1.230:5678/print?{query}"


FILE_ACTIONS: tuple[FileActionDefinition, ...] = (
    FileActionDefinition(
        id="generate-stl",
        label="Generate STL",
        suffixes=(".scad",),
        output_suffix=".stl",
        command_builder=_openscad_stl_command,
        additional_command_builders=(_openscad_png_command,),
    ),
    FileActionDefinition(
        id="convert-pdf",
        label="Convert to PDF",
        suffixes=(".svg",),
        output_suffix=".pdf",
        command_builder=_inkscape_pdf_command,
    ),
    FileActionDefinition(
        id="print-label",
        label="Print Label",
        suffixes=(".pdf",),
        print_server_printer_selection=6,
        print_server_printer_name="label_6_4",
    ),
    FileActionDefinition(
        id="print-postcard",
        label="Print Postcard",
        suffixes=(".pdf",),
        print_server_printer_selection=3,
        print_server_printer_name="postcard",
    ),
    FileActionDefinition(
        id="print-label-2-1",
        label="Print Label 2 1",
        suffixes=(".pdf",),
        print_server_printer_selection=8,
        print_server_printer_name="label_2_1",
    ),
    FileActionDefinition(
        id="print-a4",
        label="Print A4",
        suffixes=(".pdf",),
        print_server_printer_selection=5,
        print_server_printer_name="a4",
    ),
    FileActionDefinition(
        id="svg-print-label",
        label="Print Label",
        suffixes=(".svg",),
        print_server_printer_selection=6,
        print_server_printer_name="label_6_4",
        convert_svg_before_print=True,
        legend_group="print-label",
    ),
    FileActionDefinition(
        id="svg-print-postcard",
        label="Print Postcard",
        suffixes=(".svg",),
        print_server_printer_selection=3,
        print_server_printer_name="postcard",
        convert_svg_before_print=True,
        legend_group="print-postcard",
    ),
    FileActionDefinition(
        id="svg-print-label-2-1",
        label="Print Label 2 1",
        suffixes=(".svg",),
        print_server_printer_selection=8,
        print_server_printer_name="label_2_1",
        convert_svg_before_print=True,
        legend_group="print-label-2-1",
    ),
    FileActionDefinition(
        id="svg-print-a4",
        label="Print A4",
        suffixes=(".svg",),
        print_server_printer_selection=5,
        print_server_printer_name="a4",
        convert_svg_before_print=True,
        legend_group="print-a4",
    ),
    FileActionDefinition(
        id="delete-file",
        label="Delete",
        suffixes=(),
        destructive=True,
        icon="bin",
        button_variant="danger",
        confirm_message_template="Delete {relative_path}? This cannot be undone.",
    ),
)

_FILE_ACTIONS_BY_ID = {action.id: action for action in FILE_ACTIONS}


def get_file_action(action_id: str) -> FileActionDefinition | None:
    return _FILE_ACTIONS_BY_ID.get(action_id)


def iter_file_actions(file_path: Path) -> tuple[FileActionDefinition, ...]:
    file_path = Path(file_path)
    return tuple(action for action in FILE_ACTIONS if action.applies_to(file_path))


def describe_file_actions(file_path: Path, base_dir: Path | None = None) -> list[dict[str, str | bool | int]]:
    file_path = Path(file_path)
    return [action.describe(file_path, base_dir) for action in iter_file_actions(file_path)]
