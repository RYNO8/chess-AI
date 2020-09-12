from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("functions.py")
)
setup(
    ext_modules = cythonize("minimax.py")
)
