from typing import Iterable, List, Set, Tuple
from cjwmodule.util.colnames import Settings, gen_unique_clean_colnames_and_warn


def _create_english_replacement_column_names(
    colnames: List[str], existing_names: Iterable[str]
) -> List[str]:
    """Suggest new column -- _unsafe_ -- names like 'Copy of A'.

    The caller must postprocess the return value with
    gen_unique_clean_colnames_and_warn() to avoid ensure safe output.

    This algorithm is a bit outdated, and it's English-only. If we want to
    tweak it, we need to create an upgrade path: most people who use this
    step _select_ its output columns in a subsequent step. (e.g., They use
    renamecolumns to change 'Copy of A' to 'Something Else'.) So if we change
    this logic, we need to support all those users.
    """
    seen_colnames = set(existing_names)
    ret = []

    for c in colnames:
        new_column_name = f"Copy of {c}"

        # Append numbers if column name happens to exist
        count = 0
        try_column_name = new_column_name
        while try_column_name in seen_colnames:
            count += 1
            try_column_name = f"{new_column_name} {count}"
        ret.append(try_column_name)
        seen_colnames.add(new_column_name)

    return ret


def render(table, params, *, settings: Settings, input_columns):
    # we'll modify `table` in-place and build up `column_formats`
    column_formats = {}

    new_english_colnames = _create_english_replacement_column_names(
        params["colnames"], table.columns
    )
    new_colnames, errors = gen_unique_clean_colnames_and_warn(
        new_english_colnames, existing_names=table.columns, settings=settings
    )

    for old_colname, new_colname in zip(params["colnames"], new_colnames):
        # Add new column next to reference column
        # `table.columns` changes with each iteration of this list
        column_idx = table.columns.tolist().index(old_colname)
        table.insert(column_idx + 1, new_colname, table[old_colname])
        column_formats[new_colname] = input_columns[old_colname].format

    return {"dataframe": table, "column_formats": column_formats, "errors": errors}


def _migrate_params_v0_to_v1(params):
    """
    v0: 'colnames' is comma-separated str. v1: 'colnames' is List.
    """
    if params["colnames"]:
        return {"colnames": params["colnames"].split(",")}
    else:
        return {"colnames": []}


def migrate_params(params):
    if isinstance(params["colnames"], str):
        params = _migrate_params_v0_to_v1(params)
    return params
