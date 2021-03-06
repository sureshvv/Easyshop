import os
from setuptools import setup, find_packages
from xml.dom.minidom import parse

def readversion():
    mdfile = os.path.join(os.path.dirname(__file__), 'easyshop', 'discounts', 
                          'profiles', 'default', 'metadata.xml')
    metadata = parse(mdfile)
    assert metadata.documentElement.tagName == "metadata"
    return metadata.getElementsByTagName("version")[0].childNodes[0].data

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

setup(name='easyshop.discounts',
      version=readversion(),
      description="Discount management for EasyShop",
      long_description='\n'.join([
        read("README.txt"),
        read("docs", "HISTORY.txt"),
      ]),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone e-commerce online-shop',
      author='Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://iqpp.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['easyshop'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
