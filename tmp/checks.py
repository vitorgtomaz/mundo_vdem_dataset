import numpy as np


def check_continuity(indices):  # WORKING
    """Takes the list of indices from the codebook and returns an array with discontinuities.
    If the length of the array is 0, the indices are continuous.
    A discontinuous index is defined by one that does not immediately succeed the previous one.
    E.g.: 3.1.2.3 -> 3.1.2.5 is a discontinuity, because 3.1.2.4 is missing
    As of 18/03/2024, the codebook processed is perfectly continuous after a few corrections to the .txt
    version produced from the .pdf
    The first block of code splits the indices on the "." and converts them to integers and Transforms into a len(idx) x n np.array
    Then it pads each row with a 1, if needed, so that all rows have the same length
    Finally, it hstacks the index, the next index, the difference between the two, and a placeholder for the discontinuity code
    The second block starts with the for statement, where each i captures a change in a different level.For example, from 3.2.3.15 to 3.2.4.1,
    column 12 of idx will receive a 3, because the change was in the 3rd level
    ft_n finds the 1 in each column, ft_0s checks that everything to the left of the 1 is 0,
    and ft_geq_1 checks that everything to the right of the 1 is smaller than 0
    If all conditions are met, the discontinuity is in the i-th level

    Args:
        indices (list of strings): list of indices in thee format 3.2.5.1 from v-dem codebook

    Returns:
        np.array: Array with the discontinuities. Columns [0:3] are the index, [4:7] are the next index, [8:11] are the difference between the two, [12] is the code of the discontinuity
    """

    idx = [[int(x) for x in index.split(".")] for index in indices]
    idx = np.array([i + [0] if len(i) < 4 else i for i in idx])

    # sorts idx byt the first 4 columns
    idx = idx[np.lexsort(idx[:, ::-1].T)]

    idx = np.hstack(
        [
            idx,  # original array
            np.roll(idx, -1, axis=0),  # array with the next row
            np.vstack([np.diff(idx, axis=0), [0, 0, 0, 0]]),  # difference between rows
            np.zeros(len(idx)).reshape(-1, 1),
        ]
    )[
        :-1
    ]  # Removes the last row

    for i in [0, 1, 2, 3]:
        ft_n = (idx[:, 11 - i] == 1).flatten()
        ft_0s = np.all(idx[:, 8 : 11 - i] == 0, axis=1)
        ft_geq_1 = idx[:, 8 + i] <= 0
        idx[ft_n & ft_0s & ft_geq_1, 12] = i + 1

    # Exceptions: the few cases where level 3 is skipped in the index, e.g. 3.2.0.13
    idx[np.all(idx[:, [2, 6, 12]] == [0, 1, 0], axis=1)] = 4
    # 2.2.21.0 -> 3.1.0.1
    idx[np.all(idx[:, [0, 1, 2, 3]] == [2, 2, 21, 0], axis=1)] = 4
    idx[np.all(idx[:, [0, 1, 2, 3]] == [9, 7, 5, 0], axis=1)] = 4

    discontinuities = idx[idx[:, 12] == 0]

    if len(discontinuities) == 0:
        print("Continuity: \tNo discontinuities found in the indices\n")
    else:
        print("Continuity: \tThere are n exceptions: ", len(discontinuities))
        print("####### The exceptions are: ", discontinuities)
        print("\n")

    return discontinuities


def check_unique(df, columns_to_analyse):
    # Unique values. As of 18/03/2024, the number of unique values for each column is as follows:
    # {'project_manager': 55, 'additional_versions': 10, 'question': 625, 'clarification': 464, 'scale': 19, 'sources': 249, 'aggregation': 87, 'citation': 79, 'years': 66, 'data_release': 32, 'responses': 4, 'cross_coder_aggregation': 9}

    unq = {col: df[col].unique() for col in columns_to_analyse}
    n_unq = {key: len(value) for key, value in unq.items()}

    print("Unique values: \t", n_unq)
    print("\t\tUse the dictionary unq to check for inconsistencies in the columns\n")
    return unq


def check_questions(df):
    # Identified exceptions that do not end in a question mark
    question_no_q_mark = [
        "3.7.0.2",
        "3.7.0.4",
        "3.7.0.7",
        "3.10.0.4",
        "3.11.0.6",
        "4.9.14",
        "4.9.15",
        "5.6.1",
        "5.6.2",
        "5.6.3",
        "5.6.4",
        "5.6.5",
    ]

    # Identified exceptions that are posed as requests "Please provide..."
    questions_not_q = [
        "3.4.2",
        "3.4.3",
        "4.5.3",
        "4.9.14",
        "8.3.1",
        "8.3.2",
        "8.3.3",
        "8.3.4",
        "8.4.1",
        "8.4.2",
        "8.4.3",
        "8.4.4",
        "8.4.5",
        "8.4.6",
        "8.6.1",
        "8.7.1",
        "8.7.2",
        "8.9.1",
        "8.9.2",
        "8.9.3",
        "9.3.3",
        "9.3.4",
        "9.3.6",
        "14.1.25",
        "14.1.26",
        "14.1.27",
        "14.1.29",
        "15.1.10",
        "15.1.11",
        "15.1.12",
        "15.1.2",
        "15.1.4",
        "15.1.6",
        "15.1.7",
        "15.1.8",
        "15.1.9",
        "15.2.1",
        "15.2.2",
        "15.2.3",
        "15.2.4",
        "15.2.5",
        "15.2.6",
    ]
    # Check for questions that do not have a single question mark and ends with it
    qwf = df[~df.question.fillna("").str.match(r"[A-Z][^?]*\?")].question
    qwf = qwf[~qwf.index.isin(question_no_q_mark + questions_not_q)]
    qwf = qwf[~qwf.isna()]
    if len(qwf) == 0:
        print("Questions: \tNo exceptions found\n")
    else:
        print(
            "Questions: \t"
            + str(len(qwf))
            + " out of "
            + str(len(df))
            + " questions start with a capital letter and end with a question mark or are not identified exceptions. Check the dataframe qwf for details\n",
        )

    return qwf


def check_years(df):
    # Checks if year is of the form \d{4}-\d{4} or one of the known exceptions
    exceptions = [
        "3.1.6.12",
        "3.1.6.14",
        "3.4.2.5",
        "3.4.2.7",
        "3.4.3.5",
        "3.4.3.7",
        "6.5.2",
        "6.5.7",
    ]
    years = df.loc[~df.index.isin(exceptions), "years"]
    exceptions = years[~years.fillna("").str.match(r"\d{4}-\d{4}") & years.notna()]
    if len(exceptions) == 0:
        print("Year: \t\tNo exceptions found")
    else:
        print("Years: \tExceptions found: ", exceptions)

    return exceptions


def check_general(df, col):
    def find_list_exceptions(col):
        exceptions = [value for value in df[col].unique() if value not in lists[col]]
        if not exceptions:
            print(col + ": \t\tNo exceptions found")
        else:
            print(col + ": \t\tExceptions found: ", exceptions)
        return exceptions

    if col == "years":
        return check_years(df)

    if col == "question":
        return check_questions(df)

    lists = {}
    lists["project_manager"] = [
        "Jan Teorell",
        "Rachel Sigman, Staffan Lindberg",
        "Svend-Erik Skaaning, Jan Teorell",
        "Allen Hicken, Michael Bernhard, Jan Teorell",
        "Svend-Erik Skaaning",
        "Staffan Lindberg, Jan Teorell",
        "Michael Bernhard",
        "David Altman",
        "Kelly McMann, Jan Teorell",
        "Staffan I. Lindberg",
        "Pamela Paxton, Megan Reif",
        "Pamela Paxton",
        "Megan Reif",
        "Michael Coppedge",
        "Carl Henrik Knutsen",
        "Staffan I. Lindberg, Carl Henrik Knutsen, Jan Teorell",
        "Allen Hicken",
        "Kelly McMann",
        "Jan Teorell, Pamela Paxton",
        "Nils Düpont",
        "Pamela Paxton, Jan Teorell",
        "Carl Henrik Knutsen, Tore Wig, Vilde Lunnan Djuve",
        "Sirianne Dahlum, Tore Wig",
        "Steven Fish, Matthew Kroenig",
        "Michael Coppedge, John Gerring, Staffan Lindberg",
        "Jeffrey Staton",
        "Pamela Paxton, Svend-Erik Skaaning",
        "Agnes Cornell",
        "Agnes Cornell, Jan Teorell",
        "Jan Teorell, Agnes Cornell",
        "Svend-Erik Skaaning, Michael Bernhard",
        "Pamela Paxton, Michael Coppedge",
        "John Gerring",
        "Rachel Sigman",
        "Marcus Tannenberg",
        "Sebastian Hellmeier",
        "Katrin Kinzelbach",
        "Alicja Polakiewicz, Janika Spannagel",
        "John Gerring, Brendan Apfeld",
        "Katrin Kinzelbach, Janika Spannagel",
        "Katrin Kinzelbach, Ilyas Saliba, Janika Spannagel",
        "Katrin Kinzelbach, Alicja Polakiewicz, Janika Spannagel",
        "Daniel Ziblatt",
        "John Gerring, Carl Henrik Knutsen",
        "John GerringQuestion: Is serfdom legal?",
        "Jan Teorell, Thomas Brambor, Agustín Goenaga, Johannes Lindvall",
        "Marcus Tannenberg, Staffan I Lindberg",
        "Marcus Tannenberg, Staffan I Lindberg, Valeriya Mechkova",
        "Kyle L. Marquardt and Valeriya Mechkova",
        "Svend-Erik Skaaning and Jeffrey Staton",
        "Staffan I. Lindberg, Jan Teorell",
        "Michael Coppedge, Svend-Erik Skaaning",
        "N/A (Digital Society Survey)",
        "Anja Neundorf",
        "N/A (External source)",
        "Brigitte Seim, Daniel Pemstein",
        "Brigitte Seim, Daniel Pemstein, Kyle L. Marquardt",
        "Pamela Paxton, Svend-Erik Skaaning, and Kelly McMann",
        "Michael Bernhard, Michael Coppedge",
        np.nan,
    ]
    lists["scale"] = [
        "Interval, from low to high (0-1)",
        "Interval",
        "Series of dichotomous scales",
        "Ordinal",
        "Nominal",
        "Ordinal, converted to interval by the measurement model",
        "Dichotomous",
        "Dichotomous, converted to interval by the measurement model",
        "Nominal (v2expathhs), or a series of dichotomous scales",
        "Nominal (v2expathhg), or a series of dichotomous scales",
        "Nominal, but categories 2-6 constitute Ordinal",
        "We provide two versions of this index. The first is the normalized output from the the hierarchical latent variable analysis. It is on an unbounded interval scale. The second, denoted by *_osp, is a version of this output which we scale using a standard normal cumulative distribution function. It is thus scaled low to high (0-1)",
        "Interval, from low to high",
        "yes/no",
        "Text",
        "Binary, converted to interval by the measurement model",
        "Continuous",
        "Numeric",
        np.nan,
    ]
    lists["additional_versions"] = [
        "*_codelow, *_codehigh, *_sd",
        np.nan,
        "*_osp, *_ord, *_codelow, *_codehigh, *_sd, *_mean, *_nr",
        "*_nr",
        "*_codelow, *_codehigh, *_sd, *_mean, *_nr",
        "*_codelow, *_codehigh",
        "*_osp, *_codelow, *_codehigh",
        "*_osp, *_ord, *_codelow, *_codehigh, *_sd, *_mean, *_mode, *_nr",
        "*_3C, *_4C, *_5C",
        "*_mean, *_pct025, *_pct975",
        "*_sd",
    ]
    lists["cross_coder_aggregation"] = [
        np.nan,
        "Bayesian item response theory measurement model (see V-Dem Methodology)",
        "Mode from country experts' coding, cross-checked by research assistants in cases where a single mode was not generated because of expert disagreement",
        "Mean",
        "Bootstrapped",
        "Bayesian item response theory measurement model (see V-Dem Methodology, posted at V-Dem.net)",
        "Mode. 'Ties' between categories receive the value 4",
        "Mode. 'Ties' between categories are resolved so that the corresponding category in v2regoppgroups with the highest mean for the same country-date is chosen",
        "Mode. 'Ties' between categories are resolved so that the corresponding category in v2regsupgroups with the highest mean for the same country-date is chosen",
        "Bayesian item response theory measurement model (see V-Dem Methodology, posted at v-dem.net)",
    ]
    lists["data_release"] = [
        "1-13. Available upon request, subject to review and approval",
        "1-13. Available in coder-level dataset",
        "9-13. Available in coder-level dataset",
        "8-13. Available upon request, subject to review and approval",
        "8-13. Available upon request, subject to review and approval\n15 Appendix E: Comments Section\nCoders are provided with the possibility to leave comments in the end of the surveys. This section lists how the request for comments were phrased in each survey. Comments made by coders are not included in the V-Dem Dataset but may be provided on request (subject to review and ethics approval)",
        "9-13. Available upon request, subject to review and approval",
        "1-13. Release 1-5 used a different, preliminary aggregation formula",
        "1-13. Release 1, 2, and 3 used a different, preliminary aggregation formula",
        "1-13. Release 1-3 used a different, preliminary aggregation formula",
        "1-13. Release 1-4 used a different, preliminary aggregation formula",
        "6-13",
        "1-13",
        "1-13. New aggregation formula in version 7",
        "1-13. Release 1-4 used a different, preliminary aggregation formula, 5-8 modified aggregation formula including v2xeg_eqaccess",
        "5-13. Release 7 modified excluding v2xcl_acjst",
        "7-13",
        "5, 7-13. Release 7 modified: v2pepwrses, v2pepwrsoc and v2pepwrgen now form a separate subcomponent index",
        "4-13",
        "1-13. Release 1-3 used a different aggregation formula for the thinner index v2x_frassoc",
        "1-13. 1-3 preliminary aggregation formula, 4-6 as v2x_accex, 7 renamed to v2x_elecoff and modified aggregation, 8",
        np.nan,
        "5-13",
        "1-6, 10-13",
        "9-13",
        "3-13",
        "3-13. Available upon request, subject to review and approval",
        "10-13",
        "3, 7-13",
        "11-13",
        "8-13",
        "12-13",
        "13",
        "5, 7-13.",
        "2-13",
        "1-13. Release 1-6 Party system institutionalization index, release 7 changed to Party institutionalization index",
        "6-13. For Version 6 as Divided party control of legislature index v2x_lgdivparctrl, 7 modified to Divided party control index",
        "5-13. Release 7 (new aggregation formula)",
        "2-3, 7-13",
    ]
    lists["var_type"] = ["C", "D", "A*", "A", "A,C", None, "E"]

    return find_list_exceptions(col)
