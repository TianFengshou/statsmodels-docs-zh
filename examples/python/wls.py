# coding: utf-8

# DO NOT EDIT
# Autogenerated from the notebook wls.ipynb.
# Edit the notebook and then sync the output with this file.
#
# flake8: noqa
# DO NOT EDIT

# # Weighted Least Squares

import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.iolib.table import (SimpleTable, default_txt_fmt)
np.random.seed(1024)

# ## WLS Estimation
#
# ### Artificial data: Heteroscedasticity 2 groups
#
# Model assumptions:
#
#  * Misspecification: true model is quadratic, estimate only linear
#  * Independent noise/error term
#  * Two groups for error variance, low and high variance groups

nsample = 50
x = np.linspace(0, 20, nsample)
X = np.column_stack((x, (x - 5)**2))
X = sm.add_constant(X)
beta = [5., 0.5, -0.01]
sig = 0.5
w = np.ones(nsample)
w[nsample * 6 // 10:] = 3
y_true = np.dot(X, beta)
e = np.random.normal(size=nsample)
y = y_true + sig * w * e
X = X[:, [0, 1]]

# ### WLS knowing the true variance ratio of heteroscedasticity
#
# In this example, `w` is the standard deviation of the error.  `WLS`
# requires that the weights are proportional to the inverse of the error
# variance.

mod_wls = sm.WLS(y, X, weights=1. / (w**2))
res_wls = mod_wls.fit()
print(res_wls.summary())

# ## OLS vs. WLS
#
# Estimate an OLS model for comparison:

res_ols = sm.OLS(y, X).fit()
print(res_ols.params)
print(res_wls.params)

# Compare the WLS standard errors to  heteroscedasticity corrected OLS
# standard errors:

se = np.vstack([[res_wls.bse], [res_ols.bse], [res_ols.HC0_se],
                [res_ols.HC1_se], [res_ols.HC2_se], [res_ols.HC3_se]])
se = np.round(se, 4)
colnames = ['x1', 'const']
rownames = ['WLS', 'OLS', 'OLS_HC0', 'OLS_HC1', 'OLS_HC3', 'OLS_HC3']
tabl = SimpleTable(se, colnames, rownames, txt_fmt=default_txt_fmt)
print(tabl)

# Calculate OLS prediction interval:

covb = res_ols.cov_params()
prediction_var = res_ols.mse_resid + (X * np.dot(covb, X.T).T).sum(1)
prediction_std = np.sqrt(prediction_var)
tppf = stats.t.ppf(0.975, res_ols.df_resid)

prstd_ols, iv_l_ols, iv_u_ols = wls_prediction_std(res_ols)

# Draw a plot to compare predicted values in WLS and OLS:

prstd, iv_l, iv_u = wls_prediction_std(res_wls)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, y, 'o', label="Data")
ax.plot(x, y_true, 'b-', label="True")
# OLS
ax.plot(x, res_ols.fittedvalues, 'r--')
ax.plot(x, iv_u_ols, 'r--', label="OLS")
ax.plot(x, iv_l_ols, 'r--')
# WLS
ax.plot(x, res_wls.fittedvalues, 'g--.')
ax.plot(x, iv_u, 'g--', label="WLS")
ax.plot(x, iv_l, 'g--')
ax.legend(loc="best")

# ## 可行的加权最小二乘(2-stage FWLS)
#
#  比如 `w` 和  `w_est` 是关于标准偏差呈正比的，因此必须平方。

resid1 = res_ols.resid[w == 1.]
var1 = resid1.var(ddof=int(res_ols.df_model) + 1)
resid2 = res_ols.resid[w != 1.]
var2 = resid2.var(ddof=int(res_ols.df_model) + 1)
w_est = w.copy()
w_est[w != 1.] = np.sqrt(var2) / np.sqrt(var1)
res_fwls = sm.WLS(y, X, 1. / ((w_est**2))).fit()
print(res_fwls.summary())
