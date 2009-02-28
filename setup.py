from setuptools import setup, find_packages
import os

version = '0.1rc6'

setup(name='collective.z3cform.datepicker',
      version=version,
      description="calendar widget for z3c.form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone z3c.form plone.z3cform collective datepicker calendar jquery',
      author='Rok Garbas',
      author_email='rok.garbas@gmail.com',
      url='http://github.com/garbas/collective.z3cform.datepicker',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.z3cform',
          'collective.jqueryui',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
