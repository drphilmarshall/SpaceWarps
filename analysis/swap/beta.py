
# Testing the beta function for PD and PL of the Toy classifiers.
# Original 1D demo was from http://en.wikipedia.org/wiki/File:Beta_distribution_pdf.svg
# by Krishnavedala, and distributed under the This file is licensed under the 
# Creative Commons Attribution-Share Alike 3.0 Unported license. This file is 
# therefore distributed under the same license, which you can read about 
# here: http://en.wikipedia.org/wiki/Creative_Commons


from matplotlib.pyplot import *
import numpy as np
from scipy.stats import beta
 
x = np.linspace(0,1,75)
 
fig = figure(figsize=(8,8),dpi=300)
ax = fig.add_subplot(111)

# # 1D demo:

# ax.plot(x,beta.pdf(x,1.25,1.25),label=r"$\alpha=1/0.8, \beta=1/0.8$")
# ax.plot(x,beta.pdf(x,1.25,2.0), label=r"$\alpha=1/0.8, \beta=1/0.5$")
# ax.plot(x,beta.pdf(x,1.25,5.0), label=r"$\alpha=1/0.8, \beta=1/0.2$")
# ax.plot(x,beta.pdf(x,2.0,1.25),label=r"$\alpha=1/0.5, \beta=1/0.8$")
# ax.plot(x,beta.pdf(x,2.0,2.0), label=r"$\alpha=1/0.5, \beta=1/0.5$")
# ax.plot(x,beta.pdf(x,2.0,5.0), label=r"$\alpha=1/0.5, \beta=1/0.2$")
# ax.plot(x,beta.pdf(x,5.0,1.25),label=r"$\alpha=1/0.2, \beta=1/0.8$")
# ax.plot(x,beta.pdf(x,5.0,2.0), label=r"$\alpha=1/0.2, \beta=1/0.5$")
# ax.plot(x,beta.pdf(x,5.0,5.0), label=r"$\alpha=1/0.2, \beta=1/0.2$")
# loc = 9
# ymax = 2.6
# ylabel = 'PDF'
# filename = "beta.png"

# 2D demo:

N = 2000

alpha = 1.0/0.25
beta = 1.0/0.8
R = 0.48*np.random.beta(alpha,beta,size=N)

alpha = 1.0/0.25
beta = 1.0/0.3
phi = -0.5*np.pi + 1.5*np.pi*np.random.beta(alpha,beta,size=N)

limit = 0.99
x = 0.5 + R*np.cos(phi) + 0.03*np.random.randn(N)
x[np.where(x>limit)] = limit
y = 0.5 + R*np.sin(phi) + 0.03*np.random.randn(N)
y[np.where(y>limit)] = limit

ax.scatter(x,y,s=5,label=r"ToyDB 2D Beta")
ax.set_xlim(0.0,1.0)
ax.set_ylim(0.0,1.0)

loc = 3
ymax = 1.0
ylabel = 'y'
filename = "beta2D.png"



ax.grid(True)
ax.minorticks_on()
ax.legend(loc=loc)
setp(ax.get_legend().get_texts(),fontsize='small')
ax.set_ylim(0,ymax)
ax.set_xlabel("x")
ax.set_ylabel(ylabel)
 
fig.savefig(filename)
