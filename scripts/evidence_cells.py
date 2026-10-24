"""Cell identities for an unchanged, already-selected financial evidence packet.

Preserves legacy quantity IDs/values while making table coordinates explicit.
Coordinates identify a source, not whether it answers the question. No QA labels,
annotated spans, or value-based cell selection are accepted by this interface.
"""
from copy import deepcopy
import re

from evidence_atoms import atom_catalog, compile_plan
from evidence_calculator import execute


def cell_catalog(evidence, table):
    if not isinstance(table, list) or any(not isinstance(row, list) or
            any(not isinstance(cell, str) for cell in row) for row in table):
        raise ValueError("Expected source table as rows of strings")
    legacy = atom_catalog(evidence)
    catalog, cell_evidence = {}, {}
    header = table[0] if table else []
    for span, text in evidence.items():
        selected = [(key, atom) for key, atom in legacy.items() if atom["span_id"] == span]
        if not span.startswith("table_"):
            cell_evidence[span] = text
            for key, atom in selected:
                catalog[key] = {**atom, "cell_id": span, "location": None,
                                "identity_scope": "text_span"}
            continue
        if not re.fullmatch(r"table_[1-9]\d*", span):
            raise ValueError("Invalid table source ID")
        index = int(span[6:])
        if index >= len(table):
            raise ValueError("Selected table row is missing")
        row = table[index]
        labels = [header[j] if j < len(header) else "column " + str(j) for j in range(len(row))]
        if any(" ; " in cell for cell in row + labels):
            raise ValueError("Ambiguous flattened cell delimiter")
        rendered = " ; ".join(f"{label}: {cell}" for label, cell in zip(labels, row))
        if rendered != text:
            raise ValueError("Selected row differs from source table")
        cursor = 0
        for column, (label, cell) in enumerate(zip(labels, row)):
            cell_id = f"{span}/cell/{column}"
            cell_evidence[cell_id] = cell
            # Use the legacy parser per cell; never change selectable values/IDs.
            local = atom_catalog({span: f"{label}: {cell}"})
            for occurrence, local_atom in enumerate(local.values()):
                if cursor >= len(selected) or local_atom["value"] != selected[cursor][1]["value"]:
                    raise ValueError("Cell mapping differs from legacy quantity catalog")
                key, atom = selected[cursor]
                catalog[key] = {**atom, "cell_id": cell_id, "identity_scope": "table_cell",
                                "location": {"row": index, "column": column, "occurrence": occurrence},
                                "row_label": row[0] if row else "", "column_label": label,
                                "cell_text": cell, "cell_role": "row_label" if column == 0 else "data"}
                cursor += 1
        if cursor != len(selected):
            raise ValueError("Incomplete cell mapping")
    if list(catalog) != list(legacy):
        raise ValueError("Source quantity order changed")
    return {"catalog": catalog, "cell_evidence": cell_evidence,
            "identity_note": "Table coordinates are exact; narrative quantities retain span-level identity. Semantic relevance is unverified."}


def compile_cells(plan, view):
    """Execute selected references with cell-level rather than row-level support."""
    atoms = {key: {**atom, "span_id": atom["cell_id"]} for key, atom in view["catalog"].items()}
    compiled = compile_plan(plan, atoms)
    bindings = []
    for index, step in enumerate(plan["steps"]):
        for side in ("left", "right"):
            ref = step[side]
            if ref in atoms:
                atom = view["catalog"][ref]
                bindings.append({"step": index, "side": side, "quantity_id": ref,
                                 "cell_id": atom["cell_id"], "location": deepcopy(atom["location"])})
    execution = execute(compiled["steps"], view["cell_evidence"]) if compiled.get("decision") == "ANSWER" else None
    return {"compiled": compiled, "bindings": bindings, "execution": execution}
