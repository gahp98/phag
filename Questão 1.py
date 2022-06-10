#!/usr/bin/env python
# coding: utf-8

# # Questão 1 - Pedro Henrique Arruda Gonçalves

# In[21]:


import pandas as pd


# In[22]:


lst1 = ["Fábrica 1", "Fábrica 2", "Fábrica 3", "Demanda"]
lst2 = [800, 1100, 600, 10]
lst3 = [1300, 1400, 1200, 10]
lst4 = [400, 600, 800, 10]
lst5 = [700, 1000, 900, 10]
lst6 = [12, 17, 11, 0]

df_aux = list(zip(lst1,lst2,lst3,lst4,lst5,lst6))

df = pd.DataFrame(df_aux)

df.columns = ["", "CD1", "CD2", "CD3", "CD4", "Capacidade"]

df # Iniciando o dataframe da questão com as respectivas distâncias das fábricas
   # aos CDs, e também com as capacidades das fábricas e as demandas dos CDs 


# In[23]:


df = df.set_index(df.iloc[0:4,0]) # Alterar o índice
df.drop("", axis=1, inplace = True) # Excluir a primeira coluna
df


# In[24]:


df.iloc[0:3,0] = df.iloc[0:3,0]*0.5 +100
df.iloc[0:3,1] = df.iloc[0:3,1]*0.5 +100
df.iloc[0:3,2] = df.iloc[0:3,2]*0.5 +100
df.iloc[0:3,3] = df.iloc[0:3,3]*0.5 +100

df # Descobrindo o custo total: é a distância multiplicada de 0,5 e depois somada ao um custo fixo de 100


# In[25]:


df.Capacidade.drop("Demanda")


# In[26]:


df_capacidades = df.Capacidade.drop("Demanda")
df_capacidades


# In[27]:


df_demandas = df.loc["Demanda"].drop("Capacidade")
df_demandas


# In[28]:


df_custos = df.iloc[:-1,:-1]
df_custos


# ## Pyomo

# In[29]:


import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory


# In[30]:


modelo = pyo.ConcreteModel()


# ### Criando índices

# In[31]:


modelo.i = Set(initialize= df_custos.index, doc='Fábricas')
modelo.j = Set(initialize= df_custos.columns, doc = "CDs")


# ### Criando os parâmetros

# In[32]:


modelo.capacidades = Param (modelo.i, initialize= df_capacidades, doc='Capacidades')
modelo.demandas = Param(modelo.j, initialize=df_demandas, doc='Demandas')


# In[33]:


dicionario_custos = df_custos.stack().to_dict()
dicionario_custos


# In[34]:


modelo.custos = Param(modelo.i, modelo.j, initialize = dicionario_custos, doc='Custos')


# ### Criando as variáveis

# In[35]:


modelo.x = Var(modelo.i, modelo.j, bounds=(0.0,None), doc='Quantidades Enviadas')


# ### Criando as restrições

# In[36]:


def regra_capacidade(modelo, i):
    return sum(modelo.x[i,j] for j in modelo.j) <= modelo.capacidades[i]

def regra_demanda(modelo, j):
    return sum(modelo.x[i,j] for i in modelo.i) >= modelo.demandas[j]


modelo.restr_capacidade = Constraint(modelo.i, rule = regra_capacidade)
modelo.restr_demanda = Constraint(modelo.j, rule = regra_demanda)


# ### Função Objetivo

# In[37]:


def custo_total(modelo):
    return sum(modelo.custos[i,j] * modelo.x[i,j] for i in modelo.i for j in modelo.j)

modelo.Z = Objective(rule=custo_total, sense=minimize) 


# In[38]:


opt = SolverFactory("gurobi")
opt.solve(modelo)


# In[39]:


for v in modelo.component_data_objects(Var):
    print (str(v), v.value)
    
print("O valor ótimo encontrado foi: R$", modelo.Z())

