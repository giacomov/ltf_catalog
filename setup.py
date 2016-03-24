from distutils.core import setup

setup(
    
    name="ltf_catalog",
    
    packages = ["pyggop","pyggop/config"],
    
    package_data = { "pyggop/config": ['configuration.json'] },
    
    version = 'v1.0.0',
    
    description = "Generates templates for pair production opacity in relativistic sources",
    
    author = 'Johann Cohen-Tanugi, Giacomo Vianello, Jonathan Granot',
    
    author_email = 'giacomo.vianello@gmail.com',
        
    ext_modules=  cythonize(extensions, 
                            compiler_directives={'cdivision': True}),
    
    
    scripts=['bin/makeggtemplate.py'],
    
    headers=[],
    
    install_requires=['numpy',
                      'scipy',
                      'cython']

)
