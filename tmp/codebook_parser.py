import re
import pandas as pd
from checks import check_continuity, check_unique, check_questions, check_general

'''Lists the cases to be treated. Each case is a way that a row containing data can start
E.g.: The row "Project Manager(s): Pamela Paxton" should be treated as a field called "project_manager"
and populated with "Pamela Paxton" in the variable 3.5.3.11
'''
cases = {
    "Project Manager(s): ": "project_manager",
    "Additional versions: ": "additional_versions",
    "Available versions: ": "additional_versions",
    "Question: ": "question",
    "Clarification: ": "clarification",
    "Scale: ": "scale",
    "Answer-type: ": "answer_type",
    "Source(s): ": "sources",
    "Citation: ": "citation",
    "Default_dates: ": "default_dates",
    "Years: ": "years",
    "Instructions to the coders": "instructions_to_coders",
    "Data release: ": "data_release",
    "Aggregation:": "aggregation",
    "Responses:": "responses",
    "Response: ": "response",
    "Cross-coder aggregation: ": "cross_coder_aggregation",
    "Notes: ": "notes",
    "Date specific: ": "date_specific",
    "Convergence": "convergence",
    "Cleaning:": "cleaning",
    "Ordering:": "ordering",
    "Country-Year Aggregation: ": "cross_year_aggregation",
}



def get_codebook(
    file="codebook_v13.txt",
    st="2.1.1 Electoral democracy index (D) (v2x_polyarchy)\n",
    end="\n10 Bibliography\n",
):
    # Opens the codebook, fixes some issues with the PDF conversion and splits into lines
    with open(file, "r", encoding="utf-8") as f:
        c = f.read()
    return (
        c[c.find(st) : c.find(end)].replace("\n[", "[").replace("\t", " ").splitlines()
    )


def parse_header(header):
    m = re.match(r"(\d+\.(\d+|\.)+) (.*?) \(([^R]{1,3})\) \((.+)\)", header)
    if m:
        return [m.group(1), m.group(3), m.group(5), m.group(4)]

    m = re.match(r"(\d\.\d\.\d) (.*?)\s*(\((.+)\))*", header)
    if m:
        return [m.group(1), m.group(2), None, m.group(4)]

    return None


def treat_exceptions(df):
    pm_na = df.project_manager.isna()
    ext_src, es_msg = df.short_name.str[:2] == "e_", "N/A (External source)"
    dss, dss_msg = df.index.str[:2] == "6.", "N/A (Digital Society Survey)"

    # Treats exceptions
    df.loc[ext_src & pm_na, "project_manager"] = es_msg
    df.loc[dss & pm_na, "project_manager"] = dss_msg

    return df


def parse_single_row(r):
    header = parse_header(r)
    if header is not None:
        return header, "header"

    field = next((k for k in list(cases.keys()) if k in r), None)
    if field is not None:
        return field, "field"

    if re.match("\d+\.\d+ ", r):
        return r, "skip"

    return r, "content"


def parse_rows(cb):
    df = pd.DataFrame(columns=["parent", "type", "or_content", "parsed_content"])
    for i, r in enumerate(cb):
        parsed_r, r_type = parse_single_row(r)
        if r_type == "header":
            df.loc[i] = [parsed_r[0], r_type, r, parsed_r]

        if r_type == "field":
            df.loc[i] = [
                df.iloc[-1]["parent"],
                cases[parsed_r],
                r,
                r.replace(parsed_r, ""),
            ]

        if r_type == "content":
            df.iloc[-1, 3] += "\n" + r
    return df


def build_df(df):
    # pivots df, making the field "parent" the index, type the columns, and parsed_content the values
    df = df.pivot_table(
        index="parent", columns="type", values="parsed_content", aggfunc="first"
    )

    # Assigns values from parsed header to long_name, short_name and var_type
    df["long_name"] = df.header.str[1]
    df["short_name"] = df.header.str[2]
    df["var_type"] = df.header.str[3]

    # removes rows that do not contain variables
    non_var_rows = [
        "3.1.1",
        "3.1.2",
        "3.1.3",
        "3.1.4",
        "3.1.5",
        "3.1.6",
        "3.3.1",
        "3.3.2",
        "3.3.3",
        "3.3.4",
        "3.3.5",
        "3.4.1",
        "3.4.2",
        "3.4.3",
        "3.5.1",
        "3.5.2",
        "3.5.3",
        "3.8.1",
        "3.8.2",
        "3.8.3",
        "3.8.4",
    ]
    df = df[~df.index.isin(non_var_rows)]

    # Fixe year rows that capture  more than just the year
    df.years = df.years.str[:9]

    # Treats exceptions
    return df


cb = get_codebook() + get_codebook(
    st="\n14.1.1 Today's date (C) (v2zzdate)\n",
    end="\n16 Appendix F: Changes Between Previous Versions of the Dataset\n",
)

df = build_df(parse_rows(cb))


# Checks
cols_to_analyze = [
    "project_manager",
    "additional_versions",
    "question",
    "scale",
    "years",
    "data_release",
    "cross_coder_aggregation",
    "var_type",
]
discontinuities = check_continuity(df.index.tolist())
unq = check_unique(df, cols_to_analyze)
qwf = check_questions(df)

for col in cols_to_analyze:
    check_general(df, col)

df.to_excel("codebook_v13_parsed.xlsx")
