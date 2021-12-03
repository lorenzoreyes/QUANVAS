import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import BCRA

auth_token, head = BCRA.auth_token, BCRA.head

circ = requests.get(BCRA.coins, headers=head)
circulation = pd.DataFrame(circ.json())
circulation.index = circulation.d
del circulation['d']
circulation = circulation.rename(columns={'v':'circulante'})

cuentas = requests.get(BCRA.cuentas_corrientes, headers=head)
ctas = pd.DataFrame(cuentas.json())
ctas.index = ctas.d
del ctas['d']
ctas = ctas.rename(columns={'v':'ctascorrientes'})

M1 = circulation.circulante + ctas.ctascorrientes

dep = requests.get(BCRA.deposits, headers=head)
deposits = pd.DataFrame(dep.json())
deposits.index = deposits.d
del deposits['d']
deposits = deposits.rename(columns={'v':'depositos'})
inst = requests.get(BCRA.deposits_institutions, headers=head)
instdeps = pd.DataFrame(inst.json())
instdeps.index = instdeps.d
del instdeps['d']
instdeps = instdeps.rename(columns={'v':'depositosinstitucionales'})

M2 = M1 + (deposits.depositos + instdeps.depositosinstitucionales)

peso = requests.get(BCRA.base, headers=head)
basep = pd.DataFrame(peso.json())
basep.index = basep.d
del basep['d']
basep = basep.rename(columns={'v':'basepesos'})
dolar = requests.get(BCRA.base_usd, headers=head)
usd = pd.DataFrame(dolar.json())
usd.index = usd.d
del usd['d']
usd = usd.rename(columns={'v':'baseusd'})7

tc = basep.basepesos / usd.baseusd

basecorregida = basep.basepesos / tc
