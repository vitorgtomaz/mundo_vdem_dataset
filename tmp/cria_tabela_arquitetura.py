import importlib
import pandas as pd
import codebook_parser as cp

description_dict = {
    # Complementos de variaveis comlementares
    "3C": "3-levels ordinalized version of the variable ",
    "4C": "4-levels ordinalized version of the variable ",
    "5C": "5-levels ordinalized version of the variable ",
    "6C": "6-levels ordinalized version of the variable ",
    "mean": "Arithmetic mean of the variable responses ",
    "nr": "Number of responses of the variable ",
    "osp_codelow": "Lower limit of the original scale (Linearized Original Scale Posterior Prediction) of the variable ",
    "osp_codehigh": "Upper limit of the original scale (Linearized Original Scale Posterior Prediction) of the variable ",
    "osp_sd": "Standard deviation of the original scale (Linearized Original Scale Posterior Prediction) of the variable ",
    "osp": "Original scale (Linearized Original Scale Posterior Prediction) of the variable ",
    "ord_codelow": "Lower limit of the ordinal scale of the variable ",
    "ord_codehigh": "Upper limit of the ordinal scale of the variable ",
    "ord_sd": "Standard deviation of the ordinal scale of the variable ",
    "ord": "Ordinal scale (Measurement Model Estimates of Original Scale Value) of the variable ",
    "codehigh": "Upper limit of the point estimate scale of the variable ",
    "codelow": "Lower limit of the point estimate scale of the variable ",
    "sd": "Standard deviation of the variable scale ",
    "mode": "Mode of the variable responses ",
    "mean": "Mean of the variable ",
    "pct025": "2,5 posterior percentile of the variable ",
    "pct975": "97,5 posterior percentile of the variable ",
}

df = pd.read_csv("../input/dados_vdem_original.csv")
content = cp.get_content(
    "codebook_v13.txt", "\n2 V-Dem Democracy Indices\n", "\n10 Bibliography\n"
)


def parse_var(var_name):
    # Matches vars with description_dict to break them
    k = next((k for k in description_dict.keys() if k in var_name), "")
    return [var_name.replace(k, ""), k]


def get_temporal_coverage(df, column):
    # Retorna o intervalo de anos cobertos pela coluna no df
    return "{}".format(
        df.loc[~df[column].isnull(), "year"].agg(["min", "max"]).to_list()
    )


# Cria um dataframe com as colunas e os tipos de dados de df
arq_tb = (
    df.dtypes.to_frame()
    .reset_index()
    .rename(columns={"index": "name", 0: "bigquery_type"})
)

# Cria as colunas da tabela_arquitetura
arq_tb = arq_tb.assign(
    new_name=arq_tb["name"].apply(lambda x: cp.get_var_data(content, x)["new_name"]),
    # Ajusta biguqery_type substituindo "object" por "string"
    bigquery_type=arq_tb["bigquery_type"].astype(str).replace("object", "string"),
    # Cria a coluna description, que sera populada depois
    description=arq_tb["name"].apply(lambda x: cp.get_var_data(content, x)["desc"]),
    # Cria a coluna temporal_coverage
    temporal_coverage=arq_tb["name"].apply(
        lambda column: get_temporal_coverage(df, column)
    ),
    # Cria a coluna covered_by_dictionary
    covered_by_dictionary="yes",
    # cria as coluna directory_column e measurement unit que serao populadas depois
    directory_column=arq_tb["name"].apply(lambda x: cp.get_var_data(content, x)["dir"]),
    measurement_unit=arq_tb["name"].apply(lambda x: cp.get_var_data(content, x)["mu"]),
    # Cria as has_sensitive_data e observations colunas
    has_sensitive_data="no",
    observations="For more details, check the v-dem codebook at https://v-dem.net/documents/24/codebook_v13.pdf",
)

# Manual fixes


# Salva em excel
arq_tb.to_excel("../tmp/tabela_arquitetura.xlsx", index=False)
