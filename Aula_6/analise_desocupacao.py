import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------
# 1) ABRIR AS DUAS TABELAS 5 (composição da desocupação por sexo)
# ---------------------------------------------------------------
t2012 = pd.read_csv(
    "Tabela5-sem_emprego_2012.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)
t2026 = pd.read_csv(
    "Tabela5-sem_emprego_2026.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)

# renomear as colunas de valor para ficar mais simples de referenciar
t2012 = t2012.rename(columns={
    "Desocupados - homens (2012 T1)": "homens_2012",
    "Desocupados - mulheres (2012 T1)": "mulheres_2012",
})
t2026 = t2026.rename(columns={
    "Desocupados - homens (2026 T1)": "homens_2026",
    "Desocupados - mulheres (2026 T1)": "mulheres_2026",
})

# ---------------------------------------------------------------
# 2) TRATAR A TABELA 1.1.1 (aula 2) -> ficar só com os ESTADOS
# ---------------------------------------------------------------
# a aba "2022" traz o número médio de horas semanais dedicadas a
# cuidados de pessoas e/ou afazeres domésticos
tab11_raw = pd.read_excel("Tabela_1_1_1__2_.xlsx", sheet_name="2022", header=None)

# a coluna 0 tem os nomes (regiões + UFs) e a coluna 1 o total geral de horas
tab11 = tab11_raw.iloc[8:, [0, 1]].copy()
tab11.columns = ["Estado", "Horas_cuidados_domesticos_2022"]

# remove linhas de total Brasil e das Grandes Regiões, ficando só com os estados
regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
tab11 = tab11[~tab11["Estado"].isin(regioes)].reset_index(drop=True)

# ---------------------------------------------------------------
# 3) JUNTAR AS TABELAS
# ---------------------------------------------------------------
comp = t2012.merge(t2026, on=["Sigla", "Código", "Estado"], how="inner")
comp = comp.merge(tab11, on="Estado", how="inner")

print(comp.head())

# ---------------------------------------------------------------
# 4) GRÁFICO 1 — participação das mulheres na desocupação, 2012 vs 2026
# ---------------------------------------------------------------
ordem = comp.sort_values("mulheres_2026")["Estado"]

longo = comp.melt(
    id_vars=["Sigla", "Código", "Estado"],
    value_vars=["mulheres_2012", "mulheres_2026"],
    var_name="Ano",
    value_name="Participacao_mulheres",
)
longo["Ano"] = longo["Ano"].map({"mulheres_2012": "2012 T1", "mulheres_2026": "2026 T1"})

fig, ax = plt.subplots(figsize=(10, 10))
sns.barplot(
    data=longo,
    y="Estado",
    x="Participacao_mulheres",
    hue="Ano",
    order=ordem,
    ax=ax,
)
ax.axvline(50, color="black", linestyle="--", linewidth=1)
ax.set_xlabel("Participação das mulheres entre as pessoas desocupadas (%)")
ax.set_ylabel("")
ax.set_title("Desocupação: participação feminina em 2012 T1 e 2026 T1")
ax.legend(title="Trimestre")
fig.tight_layout()
fig.savefig("grafico_participacao_mulheres.png", dpi=150)
plt.show()

# ---------------------------------------------------------------
# 5) GRÁFICO 2 — cruzamento com a Tabela 1.1.1 (afazeres domésticos)
# ---------------------------------------------------------------
comp["variacao_pp_mulheres"] = comp["mulheres_2026"] - comp["mulheres_2012"]

fig2, ax2 = plt.subplots(figsize=(9, 7))
sns.scatterplot(
    data=comp,
    x="Horas_cuidados_domesticos_2022",
    y="mulheres_2026",
    ax=ax2,
)
for _, row in comp.iterrows():
    ax2.annotate(row["Sigla"], (row["Horas_cuidados_domesticos_2022"], row["mulheres_2026"]),
                 fontsize=8, xytext=(3, 3), textcoords="offset points")
ax2.axhline(50, color="gray", linestyle="--", linewidth=1)
ax2.set_xlabel("Horas semanais médias em cuidados/afazeres domésticos (2022)")
ax2.set_ylabel("Participação das mulheres na desocupação (2026 T1, %)")
ax2.set_title("Afazeres domésticos (2022) x participação feminina na desocupação (2026)")
fig2.tight_layout()
fig2.savefig("grafico_cruzamento_tabela11.png", dpi=150)
plt.show()

comp.to_csv("comp_final.csv", index=False)
