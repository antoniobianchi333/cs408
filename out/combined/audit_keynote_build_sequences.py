#!/usr/bin/env python3
"""Decode slide order, skip flags, and animation build/chunk order from .key.

This is a read-only structural audit for modern Apple iWork ZIP packages. It
uses Python's standard library plus the system Snappy shared library via
ctypes; it does not install a Python package or modify the Keynote file.
The field numbers are the reverse-engineered Keynote 14.4 schema. Treat this
as a locator and verify unfamiliar/version-specific records against the
rendered deck and reference PDF before using the result for conversion.

Example:
  python3 out/combined/audit_keynote_build_sequences.py \
    --key slides/01-408st-introduction.key \
    --page-map out/.build/batch-01/01-introduction-page-candidates.csv \
    --output out/combined/final-batches/batch-01-introduction-build-sequences.csv
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import ctypes.util
import re
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path


TYPE_DOCUMENT = 1
TYPE_SHOW = 2
TYPE_SLIDE_NODE = 4
TYPE_SLIDE = 5
TYPE_BUILD = 8
TYPE_BUILD_CHUNK = 153

SLIDE_ORDER_FIELD = 2
NODE_SLIDE_FIELD = 2
NODE_SKIPPED_FIELD = 4
NODE_HAS_BUILDS_FIELD = 6
NODE_HAS_TRANSITION_FIELD = 7
NODE_HAS_NOTE_FIELD = 8
NODE_BUILD_EVENT_COUNT_FIELD = 15
NODE_HAS_EXPLICIT_BUILDS_FIELD = 20
SLIDE_BUILDS_FIELD = 2
SLIDE_TRANSITION_FIELD = 4
SLIDE_BUILD_CHUNKS_FIELD = 43
SLIDE_LEGACY_BUILD_CHUNKS_FIELD = 3

ASCII_RE = re.compile(rb"[ -~]{4,}")


@dataclass
class Message:
    number: int
    wire: int
    value: int | bytes


@dataclass
class Archive:
    identifier: int
    messages: list[tuple[int, bytes]]


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7
        if shift > 70:
            break
    raise ValueError("invalid or truncated protobuf varint")


def protobuf_fields(data: bytes) -> list[Message]:
    fields: list[Message] = []
    offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError("protobuf field number zero")
        if wire == 0:
            value, offset = read_varint(data, offset)
        elif wire == 1:
            end = offset + 8
            if end > len(data):
                raise ValueError("truncated fixed64 field")
            value, offset = data[offset:end], end
        elif wire == 2:
            length, offset = read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise ValueError("truncated length-delimited field")
            value, offset = data[offset:end], end
        elif wire == 5:
            end = offset + 4
            if end > len(data):
                raise ValueError("truncated fixed32 field")
            value, offset = data[offset:end], end
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        fields.append(Message(number, wire, value))
    return fields


class Snappy:
    def __init__(self) -> None:
        library = ctypes.util.find_library("snappy")
        if not library:
            raise RuntimeError(
                "system libsnappy was not found; install/use the system Snappy "
                "library or run this audit on a host that provides it"
            )
        self.lib = ctypes.CDLL(library)
        self.length = self.lib.snappy_uncompressed_length
        self.length.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.length.restype = ctypes.c_int
        self.decompress = self.lib.snappy_uncompress
        self.decompress.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self.decompress.restype = ctypes.c_int

    def decode(self, chunk: bytes) -> bytes:
        uncompressed_size = ctypes.c_size_t()
        if self.length(chunk, len(chunk), ctypes.byref(uncompressed_size)) != 0:
            raise ValueError("Snappy could not read the IWA chunk length")
        output = ctypes.create_string_buffer(uncompressed_size.value)
        output_size = ctypes.c_size_t(uncompressed_size.value)
        if self.decompress(chunk, len(chunk), output, ctypes.byref(output_size)) != 0:
            raise ValueError("Snappy could not decompress the IWA chunk")
        return output.raw[: output_size.value]


def decompress_iwa(data: bytes, snappy: Snappy) -> bytes:
    offset = 0
    chunks: list[bytes] = []
    while offset < len(data):
        if offset + 4 > len(data):
            raise ValueError("truncated IWA chunk header")
        chunk_type = data[offset]
        chunk_size = int.from_bytes(data[offset + 1 : offset + 4], "little")
        offset += 4
        end = offset + chunk_size
        if end > len(data):
            raise ValueError("truncated IWA chunk payload")
        if chunk_type != 0:
            raise ValueError(f"unexpected IWA chunk type {chunk_type}")
        chunks.append(snappy.decode(data[offset:end]))
        offset = end
    return b"".join(chunks)


def parse_archives(data: bytes, snappy: Snappy) -> list[Archive]:
    stream = decompress_iwa(data, snappy)
    offset = 0
    archives: list[Archive] = []
    while offset < len(stream):
        header_size, offset = read_varint(stream, offset)
        header_end = offset + header_size
        if header_end > len(stream):
            raise ValueError("truncated IWA ArchiveInfo header")
        header = protobuf_fields(stream[offset:header_end])
        offset = header_end
        identifiers = [f.value for f in header if f.number == 1 and f.wire == 0]
        if len(identifiers) != 1 or not isinstance(identifiers[0], int):
            raise ValueError("IWA ArchiveInfo has no unique identifier")
        infos: list[tuple[int, int]] = []
        for field in header:
            if field.number != 2 or field.wire != 2 or not isinstance(field.value, bytes):
                continue
            info = protobuf_fields(field.value)
            types = [f.value for f in info if f.number == 1 and f.wire == 0]
            lengths = [f.value for f in info if f.number == 3 and f.wire == 0]
            if len(types) != 1 or len(lengths) != 1:
                raise ValueError("IWA MessageInfo has no unique type/length")
            infos.append((int(types[0]), int(lengths[0])))

        messages = []
        for message_type, payload_size in infos:
            payload_end = offset + payload_size
            if payload_end > len(stream):
                raise ValueError("IWA message payload exceeds stream length")
            messages.append((message_type, stream[offset:payload_end]))
            offset = payload_end
        archives.append(Archive(int(identifiers[0]), messages))
    return archives


def values(fields: list[Message], number: int, wire: int | None = None) -> list[int | bytes]:
    return [
        field.value
        for field in fields
        if field.number == number and (wire is None or field.wire == wire)
    ]


def first_int(fields: list[Message], number: int, default: int = 0) -> int:
    found = values(fields, number, 0)
    return int(found[0]) if found else default


def reference_id(data: bytes) -> int | None:
    refs = values(protobuf_fields(data), 1, 0)
    return int(refs[0]) if len(refs) == 1 else None


def optional_string(fields: list[Message], number: int) -> str:
    raw = values(fields, number, 2)
    if not raw or not isinstance(raw[0], bytes):
        return ""
    return raw[0].decode("utf-8", "replace")


def optional_double(fields: list[Message], number: int) -> str:
    raw = values(fields, number, 1)
    if not raw or not isinstance(raw[0], bytes) or len(raw[0]) != 8:
        return ""
    return f"{struct.unpack('<d', raw[0])[0]:g}"


def record_of_type(archives: list[Archive], message_type: int) -> dict[int, bytes]:
    result: dict[int, bytes] = {}
    for archive in archives:
        for kind, payload in archive.messages:
            if kind == message_type:
                result[archive.identifier] = payload
    return result


def slide_component_index(names: set[str]) -> dict[int, list[str]]:
    index: dict[int, list[tuple[int, str]]] = {}
    pattern = re.compile(r"^Index/Slide-(\d+)(?:-(\d+))?\.iwa$")
    for name in names:
        match = pattern.fullmatch(name)
        if match:
            identifier = int(match.group(1))
            suffix_order = int(match.group(2)) if match.group(2) else 0
            index.setdefault(identifier, []).append((suffix_order, name))
    return {
        identifier: [name for _, name in sorted(candidates)]
        for identifier, candidates in index.items()
    }


def first_record_of_type(archives: list[Archive], message_type: int) -> tuple[int, bytes] | None:
    for archive in archives:
        for kind, payload in archive.messages:
            if kind == message_type:
                return archive.identifier, payload
    return None


def parse_page_map(path: Path | None) -> dict[int, tuple[int, int]]:
    if path is None:
        return {}
    with path.open(newline="", encoding="utf-8") as source:
        return {
            int(row["reference_pdf_page"]): (
                int(row["converted_pptx_slide"]), int(row["reference_pdf_page"])
            )
            for row in csv.DictReader(source)
        }


def visible_excerpt(data: bytes, limit: int = 300) -> str:
    parts = [chunk.decode("ascii", "replace") for chunk in ASCII_RE.findall(data)]
    text = " | ".join(dict.fromkeys(part.strip() for part in parts))
    return text[:limit]


def unpack_refs(fields: list[Message], number: int) -> list[int]:
    refs = []
    for raw in values(fields, number, 2):
        if isinstance(raw, bytes):
            ref = reference_id(raw)
            if ref is not None:
                refs.append(ref)
    return refs


def transition_effect(fields: list[Message]) -> tuple[str, str]:
    transition = values(fields, SLIDE_TRANSITION_FIELD, 2)
    if not transition or not isinstance(transition[0], bytes):
        return "", ""
    attrs_fields = protobuf_fields(transition[0])
    attrs = values(attrs_fields, 2, 2)
    if not attrs or not isinstance(attrs[0], bytes):
        return "", ""
    animation = values(protobuf_fields(attrs[0]), 8, 2)
    if not animation or not isinstance(animation[0], bytes):
        return "", ""
    animation_fields = protobuf_fields(animation[0])
    return optional_string(animation_fields, 2), optional_double(animation_fields, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument(
        "--page-map", type=Path,
        help="optional PDF-page → LibreOffice-slide map, used to verify source order",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    snappy = Snappy()
    with zipfile.ZipFile(args.key) as package:
        names = set(package.namelist())
        slide_components = slide_component_index(names)
        document_name = "Index/Document.iwa"
        if document_name not in names:
            raise ValueError(f"{args.key} has no {document_name}")
        document_archives = parse_archives(package.read(document_name), snappy)
        generic_slide_archives = (
            parse_archives(package.read("Index/Slide.iwa"), snappy)
            if "Index/Slide.iwa" in names else []
        )
        document = first_record_of_type(document_archives, TYPE_DOCUMENT)
        if document is None:
            raise ValueError("could not find KN.DocumentArchive")
        _, document_payload = document
        document_fields = protobuf_fields(document_payload)
        show_id_values = unpack_refs(document_fields, 2)
        if len(show_id_values) != 1:
            raise ValueError("KN.DocumentArchive has no unique show reference")
        show = record_of_type(document_archives, TYPE_SHOW).get(show_id_values[0])
        if show is None:
            raise ValueError("could not find KN.ShowArchive")
        show_fields = protobuf_fields(show)
        trees = values(show_fields, 3, 2)
        if len(trees) != 1 or not isinstance(trees[0], bytes):
            raise ValueError("KN.ShowArchive has no inline slide tree")
        ordered_node_ids = unpack_refs(protobuf_fields(trees[0]), SLIDE_ORDER_FIELD)
        nodes = record_of_type(document_archives, TYPE_SLIDE_NODE)
        page_map = parse_page_map(args.page_map)

        rows: list[dict[str, str]] = []
        visible_order = 0
        for source_order, node_id in enumerate(ordered_node_ids, start=1):
            node_payload = nodes.get(node_id)
            if node_payload is None:
                raise ValueError(f"slide order refers to missing SlideNode {node_id}")
            node_fields = protobuf_fields(node_payload)
            slide_ids = unpack_refs(node_fields, NODE_SLIDE_FIELD)
            if len(slide_ids) != 1:
                raise ValueError(f"SlideNode {node_id} has no unique slide reference")
            slide_id = slide_ids[0]
            component_name = ""
            all_payloads: list[bytes] = []
            component_archives: list[Archive] = []
            for candidate_name in slide_components.get(slide_id, []):
                candidate_archives = parse_archives(package.read(candidate_name), snappy)
                if slide_id in record_of_type(candidate_archives, TYPE_SLIDE):
                    component_name = candidate_name
                    component_archives = candidate_archives
                    all_payloads = [payload for rec in component_archives for _, payload in rec.messages]
                    break
            if not component_archives and slide_id in record_of_type(generic_slide_archives, TYPE_SLIDE):
                component_name = "Index/Slide.iwa"
                component_archives = generic_slide_archives
                all_payloads = [payload for rec in component_archives for _, payload in rec.messages]

            slide_payload = record_of_type(component_archives, TYPE_SLIDE).get(slide_id)
            slide_fields = protobuf_fields(slide_payload) if slide_payload else []
            build_ids = unpack_refs(slide_fields, SLIDE_BUILDS_FIELD)
            chunk_ids = unpack_refs(slide_fields, SLIDE_BUILD_CHUNKS_FIELD)
            chunk_entries: list[tuple[str, bytes, str]] = []
            for chunk_id in chunk_ids:
                raw_chunk = record_of_type(component_archives, TYPE_BUILD_CHUNK).get(chunk_id)
                if raw_chunk is not None:
                    chunk_entries.append((str(chunk_id), raw_chunk, "referenced"))
            if not chunk_entries:
                for legacy_order, field in enumerate(
                    (f for f in slide_fields if f.number == SLIDE_LEGACY_BUILD_CHUNKS_FIELD and f.wire == 2),
                    start=1,
                ):
                    if isinstance(field.value, bytes):
                        chunk_entries.append((f"legacy-{legacy_order}", field.value, "legacy inline"))
            for _, raw_chunk, _ in chunk_entries:
                chunk_fields = protobuf_fields(raw_chunk)
                chunk_refs = values(chunk_fields, 1, 2)
                chunk_build_id = reference_id(chunk_refs[0]) if chunk_refs else None
                if chunk_build_id is not None and chunk_build_id not in build_ids:
                    build_ids.append(chunk_build_id)
            build_payloads = record_of_type(component_archives, TYPE_BUILD)
            build_records: dict[int, dict[str, str]] = {}
            for build_order, build_id in enumerate(build_ids, start=1):
                raw_build = build_payloads.get(build_id)
                if raw_build is None:
                    continue
                build_fields = protobuf_fields(raw_build)
                attrs = values(build_fields, 4, 2)
                attr_fields = protobuf_fields(attrs[0]) if attrs and isinstance(attrs[0], bytes) else []
                animation = values(attr_fields, 18, 2)
                animation_fields = (
                    protobuf_fields(animation[0])
                    if animation and isinstance(animation[0], bytes)
                    else []
                )
                build_records[build_id] = {
                    "slide_build_order": str(build_order),
                    "build_id": str(build_id),
                    "drawable_id": str(reference_id(values(build_fields, 1, 2)[0]) or "")
                    if values(build_fields, 1, 2)
                    else "",
                    "delivery": optional_string(build_fields, 2),
                    "effect": optional_string(animation_fields, 2),
                    "animation_type": optional_string(animation_fields, 1),
                    "build_duration_seconds": optional_double(animation_fields, 3),
                    "event_trigger": str(first_int(attr_fields, 4))
                    if values(attr_fields, 4, 0) else "",
                    "text_delivery_enum": str(first_int(attr_fields, 20))
                    if values(attr_fields, 20, 0) else "",
                    "delivery_option_enum": str(first_int(attr_fields, 21))
                    if values(attr_fields, 21, 0) else "",
                }

            transition, transition_duration = transition_effect(slide_fields)
            skipped = str(first_int(node_fields, NODE_SKIPPED_FIELD, 0))
            reference_page = ""
            candidate_slide = ""
            sequence_alignment = "not checked"
            if skipped == "0":
                visible_order += 1
                if args.page_map:
                    candidate, mapped_page = page_map.get(visible_order, (0, 0))
                    reference_page = str(mapped_page) if mapped_page else ""
                    candidate_slide = str(candidate) if candidate else ""
                    sequence_alignment = (
                        "unskipped source order matches candidate slide"
                        if candidate == source_order
                        else "review: source order and candidate slide differ"
                    )

            chunk_rows: list[dict[str, str]] = []
            for chunk_order, (chunk_id, raw_chunk, chunk_source) in enumerate(chunk_entries, start=1):
                chunk_fields = protobuf_fields(raw_chunk)
                chunk_build_refs = values(chunk_fields, 1, 2)
                chunk_build_id = reference_id(chunk_build_refs[0]) if chunk_build_refs else None
                identifier_payloads = values(chunk_fields, 7, 2)
                identifier_fields = (
                    protobuf_fields(identifier_payloads[0])
                    if identifier_payloads and isinstance(identifier_payloads[0], bytes)
                    else []
                )
                chunk_index = values(identifier_fields, 2, 0) or values(chunk_fields, 2, 0)
                chunk_rows.append({
                    "build_chunk_order": str(chunk_order),
                    "build_chunk_archive_id": str(chunk_id),
                    "build_chunk_source": chunk_source,
                    "build_chunk_index": str(int(chunk_index[0])) if chunk_index else "",
                    "chunk_build_id": str(chunk_build_id or ""),
                    "chunk_delay_seconds": optional_double(chunk_fields, 3),
                    "chunk_duration_seconds": optional_double(chunk_fields, 4),
                    "chunk_automatic": str(first_int(chunk_fields, 5, -1))
                    if values(chunk_fields, 5, 0) else "",
                    "chunk_referent": str(first_int(chunk_fields, 6, -1))
                    if values(chunk_fields, 6, 0) else "",
                })

            common = {
                "keynote_source": args.key.name,
                "source_slide_order": str(source_order),
                "reference_pdf_page": reference_page,
                "candidate_pptx_slide": candidate_slide,
                "source_candidate_alignment": sequence_alignment,
                "slide_component": component_name,
                "slide_node_id": str(node_id),
                "source_slide_id": str(slide_id),
                "is_skipped": skipped,
                "node_has_builds_cache": str(first_int(node_fields, NODE_HAS_BUILDS_FIELD, 0)),
                "node_build_event_count_cache": str(first_int(node_fields, NODE_BUILD_EVENT_COUNT_FIELD)),
                "node_has_explicit_builds_cache": str(first_int(node_fields, NODE_HAS_EXPLICIT_BUILDS_FIELD, 0)),
                "node_has_transition_cache": str(first_int(node_fields, NODE_HAS_TRANSITION_FIELD, 0)),
                "node_has_notes_cache": str(first_int(node_fields, NODE_HAS_NOTE_FIELD, 0)),
                "transition_effect": transition,
                "transition_duration_seconds": transition_duration,
                "decoded_build_count": str(len(build_ids)),
                "decoded_build_chunk_count": str(len(chunk_entries)),
                "slide_iwa_text_excerpt": visible_excerpt(b"\n".join(all_payloads)),
            }

            build_order_by_id = {build_id: index for index, build_id in enumerate(build_ids, start=1)}
            emitted_builds: set[int] = set()
            for chunk in chunk_rows:
                build_id = int(chunk["chunk_build_id"]) if chunk.get("chunk_build_id") else None
                build = build_records.get(build_id, {}) if build_id is not None else {}
                if build_id is not None:
                    emitted_builds.add(build_id)
                rows.append({
                    **common,
                    **build,
                    "slide_build_order": str(build_order_by_id.get(build_id, ""))
                    if build_id is not None else "",
                    "build_id": str(build_id or ""),
                    **chunk,
                })
            for build_id in build_ids:
                if build_id not in emitted_builds and build_id in build_records:
                    rows.append({
                        **common,
                        **build_records[build_id],
                        "build_chunk_note": "build has no listed build chunk",
                    })
            if not chunk_rows and not build_ids:
                rows.append({**common, "slide_build_order": "", "build_id": ""})

    columns = [
        "keynote_source", "source_slide_order", "reference_pdf_page", "candidate_pptx_slide",
        "source_candidate_alignment", "slide_component", "slide_node_id", "source_slide_id", "is_skipped",
        "node_has_builds_cache", "node_build_event_count_cache", "node_has_explicit_builds_cache",
        "node_has_transition_cache", "node_has_notes_cache", "transition_effect",
        "transition_duration_seconds", "decoded_build_count", "decoded_build_chunk_count",
        "slide_build_order", "build_id", "drawable_id",
        "delivery", "effect", "animation_type", "build_duration_seconds", "event_trigger",
        "text_delivery_enum", "delivery_option_enum", "build_chunk_order", "build_chunk_archive_id",
        "build_chunk_index", "build_chunk_source", "chunk_build_id", "chunk_delay_seconds",
        "chunk_duration_seconds", "chunk_automatic", "chunk_referent", "build_chunk_note",
        "slide_iwa_text_excerpt",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    slide_count = len({row["source_slide_order"] for row in rows})
    build_row_count = sum(bool(row.get("build_chunk_order")) for row in rows)
    slide_rows = {row["source_slide_order"]: row for row in rows}
    active_rows = [row for row in slide_rows.values() if row["is_skipped"] == "0"]
    mismatches = sum(row["source_candidate_alignment"].startswith("review:") for row in active_rows)
    print(f"Decoded {slide_count} ordered slide nodes and {build_row_count} ordered build chunks.")
    if args.page_map:
        mapped_count = sum(bool(row["reference_pdf_page"]) for row in active_rows)
        print(
            f"Mapped {mapped_count}/{len(active_rows)} unskipped slides; "
            f"candidate sequence mismatches: {mismatches}."
        )
    print(f"Structural build audit: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
