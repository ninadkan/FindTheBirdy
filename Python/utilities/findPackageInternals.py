
import importlib.util
from pathlib import Path
import os
MODULE_EXTENSIONS = '.py'

def package_contents(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return set()

    pathname = Path(spec.origin).parent
    ret = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith('__'):
                continue
            current = '.'.join((package_name, entry.name.partition('.')[0]))
            if entry.is_file():
                if entry.name.endswith(MODULE_EXTENSIONS):
                    ret.add(current)
            elif entry.is_dir():
                ret.add(current)
                ret |= package_contents(current)


    return ret

def getMethods():
    import inspect
    from pydocumentdb import document_client as client

 
    lstFnNames = inspect.getmembers(client.DocumentClient.QueryCollections(), predicate=inspect.ismethod)
    for it in lstFnNames:
        print(it)

    method_list = [func for func in dir(client.DocumentClient) if callable(getattr(client.DocumentClient, func))]

def displayResults(packageName): 
    rv = package_contents(packageName)
    lst = list(rv)

    for item in lst:
        print(item)

getMethods()

# displayResults('pydocumentdb')
# getMethods('pydocumentdb')

#displayResults('azure-cosmos')
# getMethods('azure-cosmos')
displayResults('azure-cosmosdb-table')
displayResults('azure-common')