# Version 1.1.9

1. Adopt lightweight data structure, optimize GUI update mechanism
2. Event push between spread sub-engines no longer passes through the event engine to reduce latency level


# Version 1.1.8

1. Fixed the problem that when loading data for backtesting, the historical data is also prioritized from the data service, so that it is prioritized to be loaded from the local database instead.


# Version 1.1.7

1. Modify the position initialization logic of spread legs to fit the 3.6.0 framework.


# Version 1.1.6

1. Change to use OffsetConverter component provided by OmsEngine.
2. Add the check for burst position when counting performance in backtesting.
3. Add log output when calling data service function.


# Version 1.1.5

1. Replace pytz library with zoneinfo. 2. adjust the installation script setup.
2. Adjust the installation script setup.cfg to add Python version restriction.


# Version 1.1.4

1. Change the icon file information of module to full path string.
2. Add support for parameter optimization algorithms such as Violent Exhaustion and Genetic Algorithm to the backtesting engine.
3. Add optional parameter complie_formula to SpreadData to support non-compilation of formulas for backtest optimization.
