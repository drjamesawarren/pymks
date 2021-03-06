import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import numpy as np

def draw_microstructure_discretization(M, a=0, s=0, Nbin=6, bound=0.016, height=1.7):
    ax = plt.axes()
    dx = 1. / (Nbin - 1.)

    cm = plt.get_cmap('cubehelix')
    cNorm  = colors.Normalize(vmin=0, vmax=Nbin - 1)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

    for i in range(Nbin - 1):
        color = scalarMap.to_rgba(i)
        r = plt.Rectangle((i * dx, 0), dx, dx, lw=4, ec='k',color=color)
        ax.add_patch(r)

    plt.yticks(())

    plt.ylim(ymax=dx * height, ymin=-bound)
    plt.xlim(xmin=-bound, xmax=1 + bound)

    ax.set_aspect('equal')
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(16) 

    for line in ax.xaxis.get_ticklines():
        line.set_markersize(0)

    all_spines = ['top', 'bottom', 'right', 'left']
    for spline in all_spines:
        ax.spines[spline].set_visible(False)

    plt.xlabel(r'$\chi^h \;\; \left( H = 6 \right)$', fontsize=16)

    v = M[a, s]

    H = np.linspace(0, 1, Nbin)
    m = np.maximum(1 - abs(v - H) / dx, 0)
    Mstring = r'$m_{{{a},{s}}}={v:1.2g}$'.format(a=a, s=s ,v=v)
    arr = r'{0:1.2g}'.format(m[0])
    for i in range(1, len(m)):
        arr += r', {0:1.2g}'.format(m[i])
    mstring = r'$m_{{{a},{s}}}^h=\left({arr}\right)$'.format(a=a, s=s, arr=arr)
    
    plt.plot((v, v), (0, dx * height), 'r--', lw=3)
    plt.text(v + 0.02, dx * (1 + 0.65 * (height - 1)), Mstring, fontsize=16, color='r')
    plt.text(v + 0.02, dx * (1 + 0.2 * (height - 1)), mstring, fontsize=16, color='r')
