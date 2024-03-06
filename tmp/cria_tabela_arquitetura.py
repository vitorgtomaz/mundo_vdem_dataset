import pandas as pd

df = pd.read_csv("../input/dados_vdem_original.csv")


def get_temporal_coverage(column):
    return "{}".format(
        df.loc[~df[column].isnull(), "year"].agg(["min", "max"]).to_list()
    )


# Cria um dataframe com as colunas e os tipos de dados de df
arq_tb = (
    df.dtypes.to_frame()
    .reset_index()
    .rename(columns={"index": "name", 0: "bigquery_type"})
)

# Neater version
arq_tb = arq_tb.assign(
    # Ajusta biguqery_type substituindo "object" por "string"
    bigquery_type=arq_tb["bigquery_type"].astype(str).replace("object", "string"),
    # Cria a coluna description, que sera populada depois
    description="",
    ano_min=arq_tb["name"]
    .apply(lambda coluna: df[["year", coluna]].dropna(subset=[coluna]).min()["year"])
    .astype(str),
    ano_max=arq_tb["name"]
    .apply(lambda coluna: df[["year", coluna]].dropna(subset=[coluna]).max()["year"])
    .astype(str),
)

# Assign quebrado em dois por causa da criacao da coluna temporal_coverage
arq_tb = arq_tb.assign(
    # Cria a coluna temporal_coverage
    temporal_coverage=ano_min + "-" + ano_max,
    # Cria a coluna covered_by_dictionary
    covered_by_dictionary="yes",
    # cria as coluna directory_column e measurement unit que serao populadas depois
    directory_column="",
    measurement_unit="",
    # Cria as has_sensitive_data e observations colunas
    has_sensitive_data="no",
    observations="For more details, check the v-dem codebook at https://v-dem.net/documents/24/codebook_v13.pdf",
)


arq_tb.drop(["ano_min", "ano_max"], axis=1, inplace=True)


# Measurement unit
excecoes_measurement_unit = {
    "country_id": "NA",
    "year": "year",
    "project": "NA",
    "historical": "NA",
    "codingstart": "year",
    "codingend": "year",
    "gap_index": "NA",
}
arq_tb["measurement_unit"] = arq_tb["name"].map(excecoes_measurement_unit)

arq_tb.loc[arq_tb["bigquery_type"] == "string", "measurement_unit"] = "NA"
arq_tb.loc[arq_tb["measurement_unit"].isnull(), "measurement_unit"] = (
    "vdem score, check documentation"
)


def assign_directory_column(target):
    return 0


# Adiciona as questoes como descricoes
# Abre o codebook codebook_v13.txt
import codebook_parser as cp

with open("codebook_v13.txt", "r") as file:
    content = file.read()

arq_tb.loc[arq_tb["description"] == "", "description"] = arq_tb["name"].apply(
    lambda coluna: cp.fetch_one_question(content, coluna)
)


arq_tb.to_excel("../tmp/tabela_arquitetura.xlsx", index=False)
