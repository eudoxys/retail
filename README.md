[![Validate main](https://github.com/eudoxys/retail/actions/workflows/validate-main.yml/badge.svg)](https://github.com/eudoxys/retail/actions/workflows/validate-main.yml)

# US Retail Electricity Data

US retail electricity data collected from EIA.

Installation
------------

To install from the repository

  python3 -m pip install git+https://github.com/eudoxys/retail

Documentation
-------------

See https://www.eudoxys.com/retail for online documentation.

Shell Usage
-----------

Command line help:

    retail help

Generate a GridLAB-D tape in CSV format for California retail electricity in 2020:

    retail --select=State:CA,Year:2020

which outputs the following

       State  Year  Month  RESIDENTIAL:Revenue:Thousand Dollars  RESIDENTIAL:Sales:Megawatthours  RESIDENTIAL:Customers:Count  RESIDENTIAL:Price:Cents/kWh  COMMERCIAL:Revenue:Thousand Dollars  COMMERCIAL:Sales:Megawatthours  COMMERCIAL:Customers:Count  COMMERCIAL:Price:Cents/kWh  INDUSTRIAL:Revenue:Thousand Dollars  INDUSTRIAL:Sales:Megawatthours  INDUSTRIAL:Customers:Count  INDUSTRIAL:Price:Cents/kWh  TRANSPORTATION:Revenue:Thousand Dollars  TRANSPORTATION:Sales:Megawatthours  TRANSPORTATION:Customers:Count  TRANSPORTATION:Price:Cents/kWh  TOTAL:Revenue:Thousand Dollars  TOTAL:Sales:Megawatthours  TOTAL:Customers:Count  TOTAL:Price:Cents/kWh
    0     CA  2020      1                             1567287.9                        7872768.5                     14006188                        19.91                            1390870.1                       9098349.5                     1753839                       15.29                            416443.09                       3527734.8                      150915                       11.80                                  5417.11                            63394.16                              13                            8.55                       3380018.2                 20562247.0               15910955                  16.44
    1     CA  2020      2                             1196237.9                        5521113.2                     13303050                        21.67                            1214366.6                       7694220.9                     1667930                       15.78                            416000.26                       3508313.8                      137675                       11.86                                  5348.05                            60123.29                              13                            8.90                       2831952.8                 16783771.0               15108668                  16.87
    2     CA  2020      3                             1290407.6                        6346745.2                     14023539                        20.33                            1382912.6                       9168761.9                     1755927                       15.08                            457949.54                       3758855.3                      150479                       12.18                                  5356.93                            60633.72                              13                            8.83                       3136626.7                 19334996.0               15929958                  16.22
    3     CA  2020      4                             1135523.3                        5558151.3                     13784664                        20.43                            1183667.4                       7947627.2                     1724810                       14.89                            405143.86                       3413903.9                      147631                       11.87                                  3938.01                            43797.75                              13                            8.99                       2728272.6                 16963480.0               15657118                  16.08
    4     CA  2020      5                             1380365.8                        7415614.2                     13689995                        18.61                            1267676.0                       7652001.1                     1691672                       16.57                            519881.23                       3847446.3                      144851                       13.51                                  3889.57                            41632.25                              13                            9.34                       3171812.6                 18956694.0               15526531                  16.73
    5     CA  2020      6                             1582682.9                        8031150.5                     13903947                        19.71                            1721482.2                       9063849.5                     1753579                       18.99                            690681.28                       4314973.8                      151862                       16.01                                  5062.86                            49897.44                              13                           10.15                       3999909.2                 21459871.0               15809401                  18.64
    6     CA  2020      7                             2090564.9                       10437989.0                     14269087                        20.03                            2110973.1                      10803135.0                     1775431                       19.54                            783161.21                       4811033.1                      156783                       16.28                                  4933.95                            46163.11                              12                           10.69                       4989633.1                 26098320.0               16201313                  19.12
    7     CA  2020      8                             2135542.9                       10320595.0                     13645186                        20.69                            1894663.0                       9019860.1                     1696379                       21.01                            752285.57                       4614581.4                      145829                       16.30                                  5158.76                            46868.76                              12                           11.01                       4787650.2                 24001906.0               15487406                  19.95
    8     CA  2020      9                             2110707.3                        9974045.9                     13841284                        21.16                            1904302.5                       9507679.6                     1721157                       20.03                            718052.66                       4441725.1                      148936                       16.17                                  6183.84                            51913.05                              12                           11.91                       4739246.3                 23975364.0               15711389                  19.77
    9     CA  2020     10                             1908989.8                        9184571.0                     13840040                        20.78                            1856381.9                      10075936.0                     1723272                       18.42                            669493.66                       4280454.8                      147735                       15.64                                  5441.23                            47013.79                              12                           11.57                       4440306.6                 23587976.0               15711059                  18.82
    10    CA  2020     11                             1253709.9                        5648239.9                     13371272                        22.20                            1297304.5                       7434806.2                     1664014                       17.45                            517467.22                       3597637.9                      139905                       14.38                                  4623.37                            43020.06                              12                           10.75                       3073105.0                 16723704.0               15175203                  18.38
    11    CA  2020     12                             1761294.0                        8623579.0                     14338358                        20.42                            1532801.1                       9540120.3                     1778372                       16.07                            450655.53                       3514221.8                      154952                       12.82                                  5328.08                            48422.63                              12                           11.00                       3750078.7                 21726344.0               16271694                  17.26

Python Usage
------------

Import the module

    import retail

Get a list of valid keys:

    retail.keys()

Get the data for California in 2020:

    retail[("CA",2020)]

Contributions
-------------

Don't forget to update the documentation if you modify `retail.py`:

    qdox -
    git commit -a -m "Update documentation"
    git push
