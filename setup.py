from distutils.core import setup

from setuptools import find_packages

setup(name="steamy-trivia",
      version="1.0",
      description="Steam based multi-player trivia game "
                  "using the Open Trivia Database",
      author='Adam Englander',
      # url='https://www.python.org/sigs/distutils-sig/',
      package_dir={"": "src"},
      packages=find_packages(where="src", exclude=["_cffi_src", "_cffi_src.*"]),
      entry_points={
          "console_scripts": [
              "steamy-trivia=steamy_trivia.app:run"
          ]
      },
      install_requires=[
          "click~=7.1",
          "requests~=2.24",
          "cffi~=1.14",
      ],
      )
