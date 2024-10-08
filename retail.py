"""Retail electricity data

Syntax: retail [OPTIONS ...]

Options:

    * --debug: enable traceback output of errors

    * --validate: perform data validation checks

    * --year=YEAR: output data for YEAR only

    * --month=MONTH: output data for MONTH only

    * --state=STATE: output data for STATE only

    * --sector=SECTOR: output data for SECTOR only

    * --keys[=INDEX]: output keys for INDEX (default all keys)

See also:

* EIA Electricity Data (https://www.eia.gov/electricity/data.php)
"""

import os
import sys
from typing import TypeVar as _TYPEVAR
import datetime as dt
import pandas as pd

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
    DATA = None

    def __init__(self:_TYPEVAR("RetailElectricity"),url:str=None):
        """Class constructor 

        Arguments:

            url (str): URL from which data is downloaded (default is `RetailElectricity.URL`)

        """
        if url:
            self.URL = url

        cache = os.path.basename(self.URL)
        expires = dt.datetime.now() - dt.timedelta(seconds=self.REFRESH)
        if self.DATA is None \
                or dt.datetime.fromtimestamp(os.path.getctime(cache)) < expires:
            if not os.path.exists(cache):
                file = self.URL
            else:
                file = cache
            self.DATA = pd.read_excel(file,
                header=[0,1,2],
                index_col=[0,1,2],
                skipfooter=1 if file == self.URL else 0,
                ).sort_index()
            if file != cache:
                try:
                    self.DATA.to_excel(cache)
                except:
                    os.remove(cache)
                    raise
            self.DATA.index.names = ["Year","Month","State"]
            self.DATA.columns.names = ["Sector","Value","Unit"]
            self.DATA.drop([x for x in self.DATA.columns if 'Data Status' in x],axis=1,inplace=True)
            
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
    assert len(data[(2020,7,"CA")].index)==21
    assert len(data[(2020,7,"CA","RESIDENTIAL")])==4
    assert len(data[(2020,7,"CA","RESIDENTIAL","Revenue")])==1

def _main(argv:list[str]) -> int:

    main.DEBUG = False
    main.YEAR = None
    main.MONTH = None
    main.STATE = None
    main.SECTOR = None
    main.VALUE = None
    main.FORMAT = "csv"
    main.INDEX = False
    main.HEADER = 'pack'
    main.PRECISION = 2

    if len(argv) == 0:

        print([x for x in __doc__.split("\n") if x.startswith("Syntax: ")][0])
        return E_OK

    if argv[0] in ["-h","--help","help"]:

        print(__doc__)
        return E_ERROR

    retail = RetailElectricity()
    data = retail.DATA.reset_index()

    for arg in argv:
        key,value = arg.split("=",1) if "=" in arg else (arg,None)
        
        if arg == "--debug":
        
            main.DEBUG = True
        
        elif arg == "--validate":
        
            _validate()
            return E_OK
        
        elif key == "--select":

            select = {x:y for x,y in [z.split(':',1) for z in value.split(",")]}
            data.set_index(list(select.keys()),inplace=True)
            data.sort_index(inplace=True)
            data = data.loc[tuple(select.values())]

        elif key == "--index":

            main.INDEX = True if not value else value

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

        elif key == "--keys":

            valid = [globals()[x] for x in globals() if x.startswith("KEY_")]
            for k in ( value.split(",") if value else valid ):
                if k in valid:
                    vals = ",".join(sorted([str(x) for x in retail.keys(k,unique=True)]))
                    print(f"{k}={vals}" if value is None or "," in value else vals)
                else:
                    raise RetailError(f"key {k} not found in indexes")

            return E_OK

        elif key == "--format":

            if not value:
                main.FORMAT = "csv"
            elif not value in [x[3:] for x in dir(pd.DataFrame) if x.startswith("to_")]:
                raise RetailError(f"{value} is not a valid output format")
            else:
                main.FORMAT = value

        elif key == "--precision":

            main.PRECISION = int(value)

        elif arg != "-":
        
            raise RetailError(f"invalid option '{arg}'")

    if main.HEADER == "pack":
        pack = [":".join([y for y in x if y]) for x in data.columns]
        data.columns.droplevel([1,2])
        data.columns = pack

    if main.INDEX == "pack":
        name = ":".join(data.index.names)
        data[name] = [":".join([str(y) for y in x if x]) for x in data.index]
        data.set_index(name,inplace=True)

    print(data.round(main.PRECISION).to_csv(
        header=True if main.HEADER else False,
        index=True if main.INDEX else False,
        ))

    return E_OK

if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
