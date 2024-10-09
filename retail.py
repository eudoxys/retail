"""Retail electricity data

Syntax: retail [OPTIONS ...]

Options:

    * -: run with no options

    * --debug: enable traceback output of errors

    * --format={csv}: override output format (see `pandas.DataFrame.to_*`)

    * --group=[KEY:FUNCTION[,...]]: apply aggregate function by group key

    * --header=[pack|unpack|none]: change header output (default 'pack')

    * --index[=pack|unpack|none]: change index output (default 'pack')

    * --keys[=KEY[,...]]: change index from default `Year,Month,State`

    * --output=FILE[,OPTION,...]: output to file (default `stdout`)

    * --precision=INT: change rounding

    * --select=KEY:VALUE[,...]: select records based using keys and values

    * --validate: perform data validation checks

    * --units=glm: change units to GridLAB-D format

Description:

The `retail` utility downloads EIA retail electricity price, sales, revenue, and
customer count data. The data is collated and indexed by default by year,
month, and state. Data is presented by default in multi-level columns for each
data field by sector, e.g., residential, commercial, industrial, transportation
and total.

The indexing can be changed using the `--index=` option.  For example, you can
specify indexing by state, year, and month by using the option
`--index=State,Year,Month`.

Data can be grouped by any the index keys available, e.g., year, month, and/or
sector, using the `--group=...` option. The group keys override the `--index`
options.

To get a list of available key values, use the `--keys=...` option. For example,
`--keys=Year` will return a list of available years.  If multiple keys are
specified, the list of keys is prefixed with the key name, followed by an equal
sign, and each key list is output on a separate line. 

By default all output is generated to `stdout` in Pandas display format. The
output format can be changed using the `--output=...` option. The filename is
used to determine the `Pandas.DataFrame.to_*`. If the extension is not valid,
you can used the `--format=...` option to specify which output function to use.
For example, `--output=file.xlsx` does not have a corresponding Pandas
DataFrame output function named `to_xlsx`. But `to_excel()` handles that
format, so specifying `--format=excel` should be specified as well.

Options for `bool`, `int`, `str`, and `float` parameters of the output functions
are allowed, using comma separated tuples of the format `option:value`. For
example, `--output=file.xlsx,float_format:%g` would result in the output call

    pd.DataFrame.to_excel('file.xlsx',float_format='%g')

Multi headers and indexes may be packed using the `--header=pack` and
`--index=pack` options.  Other valid header and index options are `unpack` and
`none`, which results in multi-index output or no output, respectively, of
headers and indexes.

Using `--units=glm` automatically causes headers to be packed and drops the
units columns.  The index is also packed, so you must use `--index=unpack` to
cause the index to be split into multiple columns.

See also:

* EIA Electricity Data (https://www.eia.gov/electricity/data.php)
"""

import os
import sys
from typing import TypeVar as _TYPEVAR
import datetime as dt
import pandas as pd
import openpyxl

E_OK = 0
E_ERROR =1

def main(argv:list[str]=sys.argv[1:]) -> int:
    """Main CLI

    Runs the main `retail` program. 

    Arguments:
        argv (list[str]): argument list (default is sys.argv)

    Returns:
        int: exit code

    Properties:
        DEBUG (bool): enable debugging traceback on exception

    Exceptions:
        Exception: exceptions are only raised if `DEBUG` is `True`.
        FileNotFoundError: exception raised when an input file is not found.
        RetailError: exception raised when an invalid command argument is encountered.
    """

    main.DATA = RetailElectricity()
    main.DEBUG = False
    main.YEAR = None
    main.MONTH = None
    main.STATE = None
    main.SECTOR = None
    main.VALUE = None
    main.FORMAT = None
    main.INDEX = False
    main.HEADER = 'pack'
    main.PRECISION = 2
    main.OUTPUT = None
    main.UNITS = None
    main.OPTIONS = {"args":[],"kwargs":{}}

    try:

        rc = _main(argv)

    except Exception:

        e_type,e_value,_ = sys.exc_info()
        print(f"ERROR [retail/{os.path.basename(sys.argv[0])}:{e_type.__name__}]:" +
            f" {e_value}",file=sys.stderr,flush=True)
        if main.DEBUG:
            raise
        rc = E_ERROR

    return rc

class RetailError(Exception):
    """Retail electricity data exception"""

class RetailElectricity:
    """Retail electricity data class

    This class is used to select retail electricity supply data. 

    Examples:

    Create an accessor object

      from retail import RetailElectricity
      data = RetailElectricity()

    To read the data for 2020, use

      data[2020]

    To read the data for August 2020, use

      data[(2020,7)]

    To read the data for August 2020 for California, use

      data[(2020,7,"CA")]

    To read the residential data for August 2020 for California, use

      data[(2020,7,"CA","RESIDENTIAL")]

    To read the residential price data for August 2020 for California, use

      data[(2020,7,"CA","RESIDENTIAL","Price")]

    To get the units of `Price`, use

      data.units()["Price"]

    To get a list of available sectors, use

      data.keys(KEY_SECTOR)

    To get a list of available values, use

      data.key(KEY_VALUE)    
    """
    URL = "https://www.eia.gov/electricity/data/eia861m/xls/sales_revenue.xlsx"
    REFRESH = 86400 # refresh every day
    CACHE = None

    def __init__(self:_TYPEVAR("RetailElectricity"),url:str=None):
        """Class constructor 

        Arguments:

            url (str): URL from which data is downloaded (default is `RetailElectricity.URL`)
        """
        if url:
            self.URL = url

        cache = os.path.basename(self.URL)
        expires = dt.datetime.now() - dt.timedelta(seconds=self.REFRESH)
        if self.CACHE is None \
                or dt.datetime.fromtimestamp(os.path.getctime(cache)) < expires:
            if not os.path.exists(cache):
                file = self.URL
            else:
                file = cache
            self.CACHE = pd.read_excel(file,
                header=[0,1,2],
                index_col=[0,1,2],
                skipfooter=1 if file == self.URL else 0,
                ).sort_index()
            if file != cache:
                try:
                    self.CACHE.to_excel(cache)
                except:
                    os.remove(cache)
                    raise
            self.CACHE.index.names = ["Year","Month","State"]
            self.CACHE.columns.names = ["Sector","Value","Unit"]
            self.CACHE.drop([x for x in self.CACHE.columns if 'Data Status' in x],axis=1,inplace=True)
        self.DATA = self.CACHE.copy()
            
    def __getitem__(self:_TYPEVAR("RetailElectricity"),index):
        if isinstance(index,int) or len(index) <= 3:
            return self.DATA.loc[index]
        if len(index) == 4:
            return self.DATA.loc[index[:3]][index[3]]
        if len(index) == 5:
            return self.DATA.loc[index[:3]][index[3]][index[4]]
        raise KeyError("too many indexers")

    def keys(self:_TYPEVAR("RetailElectricity"),key:str=None,unique:bool=False) -> set|list:
        """Get keys used for indexing data

        Arguments:

            key (str): the key level for which the keys are sought (default None)

            unique (bool): specifies whether to return the distinct values

        Returns:

            set|list: keys at that level or all keys if level is None

        """
        if key is None:
            return {"rows":list(self.DATA.index),"columns":list(self.DATA.columns)}
        if key in self.DATA.index.names:
            values = self.DATA.reset_index()[key]
        elif key in self.DATA.columns.names:
            column = [n for n,x in enumerate(self.DATA.columns.names) if x==key]
            if column == []:
                raise RetailError(f"{key} is not valid")
            values = [x[column[0]] for x in self.DATA.columns]
        else:
            raise KeyError(f"invalid key = {key}")
        return set(values) if unique else list(values)

    def units(self) -> dict:
        """Get units of data

        Returns:

            dict: mapping of value keys to units of values

        """
        return {x[1]:x[2] for x in self.DATA.columns[1:]}

KEY_YEAR = "Year"
KEY_MONTH = "Month"
KEY_STATE = "State"
KEY_SECTOR = "Sector"
KEY_VALUE = "Value"

def _validate():

    data = RetailElectricity()

    main.DEBUG = True

    assert min(data.keys(KEY_YEAR,True))==2010
    assert data.keys(KEY_MONTH,True)==set(range(1,13))
    assert data.keys(KEY_STATE,True)=={
        'DC', 'FL', 'OK', 'KY', 'MI', 'TN', 'WA', 'SC', 'CT', 'NV', 'IA', 'CA', 
        'DE', 'GA', 'AK', 'NY', 'SD', 'AR', 'UT', 'MA', 'NC', 'NJ', 'OH', 'ND', 
        'RI', 'CO', 'IN', 'MT', 'WV', 'WY', 'NH', 'AL', 'VT', 'OR', 'NM', 'VA', 
        'MS', 'IL', 'AZ', 'HI', 'WI', 'MN', 'MO', 'MD', 'LA', 'KS', 'PA', 'NE', 
        'TX', 'ID', 'ME'}
    assert data.keys(KEY_SECTOR,True)=={
        'TOTAL', 'INDUSTRIAL', 'RESIDENTIAL', 'TRANSPORTATION', 'COMMERCIAL'
        }
    assert data.keys(KEY_VALUE,True)=={'Customers', 'Sales', 'Price', 'Revenue'}
    assert data.units()=={
        'Revenue': 'Thousand Dollars', 
        'Sales': 'Megawatthours', 
        'Customers': 'Count', 
        'Price': 'Cents/kWh',
        }

    assert len(data[2020])==612
    assert len(data[(2020)])==612
    assert len(data[(2020,7)])==51
    assert len(data[(2020,7,"CA")])==20
    assert len(data[(2020,7,"CA","RESIDENTIAL")])==4
    assert len(data[(2020,7,"CA","RESIDENTIAL","Revenue")])==1

    try:
        for test in """--debug --stdout=keys.txt,w --keys
    --stdout=keys.txt,a --keys=State
    --stdout=keys.txt,mode:a --keys=Year,Sector
    --output=test.xlsx,sheet_name:test --format=excel --units=glm --index=unpack --header=unpack
    --output=test.json,indent:4
    --units=glm --index=unpack --output=test.csv,float_format:%.1f,index:true,chunksize:1000 --precision=-2
    """.split("\n"):
            main(test.split())
    except:
        for file in ["keys.txt","test.csv","test.xlsx","test.json","sales_revenue.xlsx"]:
            if os.path.exists(file):
                os.remove(file)
        raise

def _main(argv:list[str]) -> int:

    if len(argv) == 0:

        print([x for x in __doc__.split("\n") if x.startswith("Syntax: ")][0],file=sys.stderr)
        return E_OK

    if argv[0] in ["-h","--help","help"]:

        print(__doc__,file=main.OUTPUT if main.OUTPUT else sys.stdout)
        return E_ERROR

    data = main.DATA.DATA

    for arg in argv:
        key,value = arg.split("=",1) if "=" in arg else (arg,None)
        
        if arg == "--debug":
        
            main.DEBUG = True
        
        elif arg == "--validate":
        
            _validate()
            return E_OK
        
        elif key == "--select":

            astype = {
                "Year" : int,
                "Month" : int,
                "State" : str,
            }
            select = {x:astype[x](y) for x,y in [z.split(':',1) for z in value.split(",")]}
            data.reset_index(inplace=True)
            data.set_index(list(select.keys()),inplace=True)
            data.sort_index(inplace=True)
            result = data.loc[tuple(select.values())]
            if isinstance(result,pd.Series):
                data = data.loc[[list(select.values())]]
            else:
                data = result

        elif key == "--index":

            main.INDEX = True if not value else value
            if value.lower() == "none":
                main.INDEX = False
            elif value.lower() == "unpack":
                main.INDEX = True

        elif key == "--group":

            for group,aggregate in [x.split(':',1) for x in value.split(",")]:
                data = data.groupby(group)
                data = getattr(data,aggregate)()

        elif key == "--header":

            if value == "pack":
                main.HEADER = "pack"
            elif value == "unpack":
                main.HEADER = True
            elif value == "none":
                main.HEADER = False
            main.HEADER=True if not value else value

        elif key == "--stdout":

            args = []
            kwargs = {}
            for arg in [x.split(":",2) for x in value.split(",")]:
                if len(arg) == 2:
                    kwargs[arg[0]] = arg[1]
                else:
                    args.append(arg[0])
            sys.stdout = open(*args,**kwargs)

        elif key == "--stderr":

            args = []
            kwargs = {}
            for arg in [x.split(":",2) for x in value.split(",")]:
                if len(arg) == 2:
                    kwargs[arg[0]] = arg[1]
                else:
                    args.append(arg[0])
            sys.stderr = open(*args,**kwargs)

        elif key == "--keys":

            valid = [globals()[x] for x in globals() if x.startswith("KEY_")]
            for k in ( value.split(",") if value else valid ):
                if k in valid:
                    vals = ",".join(sorted([str(x) for x in main.DATA.keys(k,unique=True)]))
                    print(f"{k}={vals}" if value is None or "," in value else vals,
                        file=main.OUTPUT if main.OUTPUT else sys.stdout,
                        **main.OPTIONS["kwargs"])
                else:
                    raise RetailError(f"key {k} not found in indexes")

            sys.exit(E_OK)

        elif key == "--format":

            if not value:
                main.FORMAT = "csv"
            elif not value in [x[3:] for x in dir(pd.DataFrame) if x.startswith("to_")]:
                raise RetailError(f"{value} is not a valid output format")
            else:
                main.FORMAT = value

        elif key == "--precision":

            main.PRECISION = None if value is None else int(value)

        elif key == "--units":

            if len(data.index.names) < 3:

                raise RetailError("--units must be specified first")
               
            if main.UNITS:

                raise RetailError("--units have already been specified") 
                
            if value == "glm":

                lookup = {
                    'Revenue': '$k', 
                    'Sales': 'MWh', 
                    'Customers': 'unit', 
                    'Price': '0.01$/kWh',
                }
                columns = list(data.columns)
                for n,values in enumerate(columns):
                    values = list(values)
                    if values[1] in lookup:
                        values[2] = lookup[values[1]]
                    columns[n] = tuple(values)
                data.columns = pd.MultiIndex.from_tuples(columns)
                for column,unit in lookup.items():
                    data.loc[data.index,column] = unit
                main.INDEX = "pack"
                main.UNITS = "glm"

        elif key in ["-o","--output"]:

            for arg in [x.split(":",2) for x in value.split(",")]:
                if len(arg) == 2:
                    main.OPTIONS["kwargs"][arg[0]] = arg[1]
                else:
                    main.OPTIONS["args"].append(arg[0])
            main.OUTPUT = main.OPTIONS["args"][0]
            main.FORMAT = os.path.splitext(main.OUTPUT)[1].split(".")[-1]

        elif arg != "-":
        
            raise RetailError(f"invalid option '{arg}'")

    if main.HEADER == "pack":
        pack = [":".join([y for y in x if y]) for x in data.columns]
        data.columns.droplevel([1,2])
        drop = []
        if main.UNITS == "glm":
            for n,item in enumerate(pack):
                item = item.split(":",3)
                if len(item) == 3:
                    item = f"{item[0]}_{item[1]}[{item[2]}]"
                    pack[n] = item
                else:
                    drop.append(":".join(item))
        data.columns = pack
        for item in drop:
            data = data.drop(item,axis=1)

    if main.INDEX == "pack":
        name = ":".join(data.index.names)
        data.loc[name] = [":".join([str(y) for y in x if x]) for x in data.index]
        data.set_index(name,inplace=True)
    elif not main.INDEX:
        data.reset_index(inplace=True)

    if not main.PRECISION is None:
        data = data.round(main.PRECISION)

    if main.FORMAT in [x[3:] for x in dir(data) if x.startswith("to_")]:

        call = getattr(data,f"to_{main.FORMAT}")
        def bool_t(x):
            if x in ["true","1"]:
                return True
            elif x in ["false","0"]:
                return False
            else:
                raise ValueError(f"{x} is a not boolean")

        for name,spec in call.__annotations__.items(): # cast to expected type
            if name in list(main.OPTIONS["kwargs"]):
                for method in [x for x in spec.split("|") if x.strip() in ["int","float","bool_t"]]:
                    try:
                        main.OPTIONS["kwargs"][name] = eval(method.strip())(main.OPTIONS["kwargs"][name])
                        break
                    except:
                        continue
        call(*main.OPTIONS["args"],**main.OPTIONS["kwargs"])

    elif main.FORMAT is None:

        pd.options.display.width = None
        pd.options.display.max_rows = None
        pd.options.display.max_columns = None
        print(data,file=main.OUTPUT if main.OUTPUT else sys.stdout)

    else:

        raise RetailError(f"{main.FORMAT} is an invalid output format")

    return E_OK

if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
