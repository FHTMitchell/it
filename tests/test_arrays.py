#! /usr/bin/env python3
# test_arrays.py

import numpy as np
import matplotlib.pyplot as plt
from it import arrays


arrays.plot_colormap(np.linspace(0, 10, 50), np.linspace(-5, 5, 50),
                     lambda x, y: x + y)
plt.show()
