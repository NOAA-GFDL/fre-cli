"""Validation for the individual YAML files that make up an FRE workflow."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterable

import yaml
from yaml.events import (
    AliasEvent,
    DocumentEndEvent,
    DocumentStartEvent,
    MappingEndEvent,
    MappingStartEvent,
    ScalarEvent,
    SequenceEndEvent,
    SequenceStartEvent,
    StreamEndEvent,
    StreamStartEvent,
)

from fre.yamltools.helpers import yaml_load


class YamlKind(StrEnum):
    """The supported roles of files in an FRE YAML configuration."""

    MODEL = "model"
    COMPILE = "compile"
    PLATFORMS = "platforms"
    PP = "pp"
    ANALYSIS = "analysis"
    CMOR = "cmor"
    GRIDS = "grids"
    SETTINGS = "settings"


class NodeKind(StrEnum):
    """The YAML collection and scalar shapes used by the conventions."""

    MAPPING = "mapping"
    SEQUENCE = "sequence"
    SCALAR = "scalar"
    ALIAS = "alias"


@dataclass(frozen=True)
class YamlConvention:
    """Required and optional top-level keys for one YAML kind."""

    required: dict[str, NodeKind]
    optional: dict[str, NodeKind]


COMMON_OPTIONAL = {"fre_properties": NodeKind.SEQUENCE}

CONVENTIONS = {
    YamlKind.MODEL: YamlConvention(
        required={"experiments": NodeKind.SEQUENCE},
        optional={
            **COMMON_OPTIONAL,
            "fre_cli_version": NodeKind.SCALAR,
            "build": NodeKind.MAPPING,
        },
    ),
    YamlKind.COMPILE: YamlConvention(
        required={"compile": NodeKind.MAPPING},
        optional=COMMON_OPTIONAL,
    ),
    YamlKind.PLATFORMS: YamlConvention(
        required={"platforms": NodeKind.SEQUENCE},
        optional=COMMON_OPTIONAL,
    ),
    YamlKind.PP: YamlConvention(
        required={"postprocess": NodeKind.MAPPING},
        optional=COMMON_OPTIONAL,
    ),
    YamlKind.ANALYSIS: YamlConvention(
        required={"analysis": NodeKind.MAPPING},
        optional=COMMON_OPTIONAL,
    ),
    YamlKind.CMOR: YamlConvention(
        required={"cmor": NodeKind.MAPPING},
        optional={**COMMON_OPTIONAL, "grids": NodeKind.SEQUENCE},
    ),
    YamlKind.GRIDS: YamlConvention(
        required={"grids": NodeKind.SEQUENCE},
        optional=COMMON_OPTIONAL,
    ),
    YamlKind.SETTINGS: YamlConvention(
        required={
            "directories": NodeKind.MAPPING,
            "postprocess": NodeKind.MAPPING,
        },
        optional=COMMON_OPTIONAL,
    ),
}


def _consume_node(first_event, events: Iterable) -> NodeKind:
    """Consume one parser-event node and return its collection shape."""

    if isinstance(first_event, ScalarEvent):
        return NodeKind.SCALAR
    if isinstance(first_event, AliasEvent):
        return NodeKind.ALIAS
    if isinstance(first_event, SequenceStartEvent):
        for event in events:
            if isinstance(event, SequenceEndEvent):
                return NodeKind.SEQUENCE
            _consume_node(event, events)
        raise ValueError("unterminated sequence")
    if isinstance(first_event, MappingStartEvent):
        for event in events:
            if isinstance(event, MappingEndEvent):
                return NodeKind.MAPPING
            _consume_node(event, events)
            try:
                value_event = next(events)
            except StopIteration as exc:
                raise ValueError("mapping key has no value") from exc
            _consume_node(value_event, events)
        raise ValueError("unterminated mapping")
    raise ValueError(f"unsupported YAML event {type(first_event).__name__}")


def _top_level_shape(path: Path) -> dict[str, NodeKind]:
    """Parse top-level keys without resolving aliases from other files."""

    try:
        events = iter(yaml.parse(path.read_text(encoding="utf-8")))
        event = next(events)
        if not isinstance(event, StreamStartEvent):
            raise ValueError("missing YAML stream start")

        event = next(events)
        if not isinstance(event, DocumentStartEvent):
            raise ValueError("missing YAML document start")

        event = next(events)
        if not isinstance(event, MappingStartEvent):
            raise ValueError("the document root must be a mapping")

        shape = {}
        for event in events:
            if isinstance(event, MappingEndEvent):
                break
            if not isinstance(event, ScalarEvent):
                raise ValueError("top-level keys must be strings")
            if event.value in shape:
                raise ValueError(f"duplicate top-level key '{event.value}'")

            try:
                value_event = next(events)
            except StopIteration as exc:
                raise ValueError(f"top-level key '{event.value}' has no value") from exc
            shape[event.value] = _consume_node(value_event, events)
        else:
            raise ValueError("unterminated root mapping")

        if not isinstance(next(events), DocumentEndEvent):
            raise ValueError("missing YAML document end")
        if not isinstance(next(events), StreamEndEvent):
            raise ValueError("FRE YAML files must contain exactly one document")
        return shape
    except (OSError, StopIteration, yaml.YAMLError, ValueError) as exc:
        raise ValueError(f"Invalid YAML structure in '{path}': {exc}") from exc


def validate_yaml_file(path: str | Path, kind: YamlKind) -> None:
    """Validate one FRE YAML file against its pre-combination convention."""

    path = Path(path)
    if not path.is_file():
        raise ValueError(f"{kind.value} YAML file does not exist: '{path}'")

    shape = _top_level_shape(path)
    convention = CONVENTIONS[kind]
    expected = convention.required | convention.optional

    missing = convention.required.keys() - shape.keys()
    if missing:
        keys = ", ".join(sorted(missing))
        raise ValueError(f"Invalid {kind.value} YAML '{path}': missing top-level key(s): {keys}")

    unexpected = shape.keys() - expected.keys()
    if unexpected:
        keys = ", ".join(sorted(unexpected))
        raise ValueError(f"Invalid {kind.value} YAML '{path}': unexpected top-level key(s): {keys}")

    for key, actual_kind in shape.items():
        expected_kind = expected[key]
        if actual_kind != expected_kind:
            raise ValueError(
                f"Invalid {kind.value} YAML '{path}': top-level key '{key}' "
                f"must contain a {expected_kind.value}, not a {actual_kind.value}"
            )


def _referenced_path(model_path: Path, reference: str) -> Path:
    return model_path.parent / reference


def _selected_experiment(model: dict, experiment: str) -> dict:
    experiments = model.get("experiments", [])
    selected = next((item for item in experiments if item.get("name") == experiment), None)
    if selected is None:
        raise ValueError(f"{experiment} is not in the list of experiments")
    return selected


def validate_yaml_inputs(model_path: str | Path, experiment: str, use: str) -> None:
    """Validate every individual YAML that will participate in consolidation."""

    model_path = Path(model_path)
    validate_yaml_file(model_path, YamlKind.MODEL)
    model = yaml_load(model_path)

    if use == "compile":
        build = model.get("build")
        if not isinstance(build, dict):
            raise ValueError(f"Invalid model YAML '{model_path}': compile use requires a build mapping")
        references = (
            (build.get("compileYaml"), YamlKind.COMPILE),
            (build.get("platformYaml"), YamlKind.PLATFORMS),
        )
    elif use == "pp":
        selected = _selected_experiment(model, experiment)
        references = [
            (selected.get("settings"), YamlKind.SETTINGS),
            *((path, YamlKind.PP) for path in selected.get("pp", [])),
            *((path, YamlKind.ANALYSIS) for path in selected.get("analysis", [])),
        ]
    else:
        return

    for reference, kind in references:
        if not isinstance(reference, str) or not reference:
            if kind in (YamlKind.SETTINGS, YamlKind.ANALYSIS):
                continue
            raise ValueError(f"Invalid model YAML '{model_path}': missing {kind.value} YAML path")
        validate_yaml_file(_referenced_path(model_path, reference), kind)
