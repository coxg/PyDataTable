"""
Mimics functionality of R's data.table in Python.

Authors: Gaven Cox <coxg@dnb.com>
"""


import pandas as pd
import numpy as np
import numbers
import re

# ============================================================================
# Constants
# ============================================================================

elemTypes = (basestring, numbers.Number)
vectorTypes = (pd.Series, np.ndarray, pd.Index, list, tuple)

# ============================================================================
# Classes
# ============================================================================

class DataTable(pd.DataFrame):
    """
    Mimics functionality of R's data.table. Inherits from pandas DataFrames,
    but replaces how one interacts with the objects.

    Parameters
    ----------
    Same as pandas DataFrame.
    """

    # ========================================================================
    # Basic methods
    # ========================================================================

    def __init__(self, data=None, index=None, columns=None, dtype=None,
                 copy=False):

        # Support for single element input
        if isinstance(data, elemTypes):
            data = [data]

        # Force all columns to be strings
        if isinstance(columns, basestring):
            columns = [columns]
        elif columns is not None:
            columns = [str(column) for column in columns]

        # Plugs into DataFrame
        pd.DataFrame.__init__(self, data=data, index=index, columns=columns,
                              dtype=dtype, copy=copy)

        # Defaults to 1-indexed
        # TODO: Pass this into pd.DataFrame - previous attempt produced NaNs
        if index is None:
            self.index = np.arange(1, nrow(data) + 1)

        # If columns is None, force to be strings starting at '1'
        # TODO: Pass this into pd.DataFrame
        if columns is None:
            self.columns = [str(column + 1)
                            if isinstance(column, numbers.Number)
                            else str(column) for column in self.columns]

    def __getitem__(self, key):

        # Handling slices, including column names!
        if isinstance(key, slice):
            if isinstance(key.start, basestring) or isinstance(key.stop,
                                                               basestring):
                return DataTable(self.ix[:, key])
            else:
                try:
                    key = slice(key.start, key.stop + 1, key.step)
                except:
                    pass
                return DataTable(self._getitem_slice(key).reset_index(
                    drop=True))

        # Handling column name
        elif key in self.columns:
            return DataTable(self._getitem_column(key))

        # Handling vector data
        if isinstance(key, vectorTypes):
            if len(key) > 0 and isinstance(key[0], basestring):
                return DataTable(self._getitem_array(key).reset_index(
                    drop=True))
            else:
                return DataTable(self.iloc[list(key)].reset_index(drop=True))

        # Handling DataFrames
        elif isinstance(key, pd.DataFrame):
            return DataTable(self._getitem_frame(key))

        # Handling queries
        elif isinstance(key, basestring):
            return DataTable(self.query(key).reset_index(drop=True))

        # Handling numbers and anything else
        else:
            return DataTable(self.loc[[key]].reset_index(drop=True))

    # Adds colons to output
    def __str__(self):
        # TODO: Find a better way to do this
        dfStr =  pd.DataFrame.__str__(self)
        colon_indices = [location.start() + len(str(index + 1)) + 1
                         for index, location
                         in enumerate(re.finditer('\n', dfStr))]
        for colon_index in colon_indices:
            dfStr = dfStr[:colon_index] + ':' + dfStr[(colon_index + 1):]
        return dfStr

    # ========================================================================
    # Comparison methods
    # ========================================================================

    # For "if DT", if it's not ambiguous then return bool
    def __nonzero__(self):

        # TODO: Return float between 0.0 and 1.0 to determine data similarity
        if self.all(skipna=False).all():
            return True
        elif (-self).all(skipna=False).all():
            return False
        else:
            raise ValueError("The truth value of this "
                             + self.__class__.__name__
                             + " is ambiguous. Use a.empty, a.bool(), "
                             + "a.item(), a.any(), or a.all() for more "
                             + "granularity.")

    # For Python 3.x
    def __bool__(self):
        return self.__nonzero__()

    # TODO: Make these not shit!

    def __eq__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__eq__(self, other)
        else:
            return DataTable(pd.DataFrame.__eq__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    def __ne__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__ne__(self, other)
        else:
            return DataTable(pd.DataFrame.__ne__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    def __lt__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__lt__(self, other)
        else:
            return DataTable(pd.DataFrame.__lt__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    def __le__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__le__(self, other)
        else:
            return DataTable(pd.DataFrame.__le__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    def __gt__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__gt__(self, other)
        else:
            return DataTable(pd.DataFrame.__gt__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    def __ge__(self, other):
        if not isinstance(other, DataTable):
            return pd.DataFrame.__ge__(self, other)
        else:
            return DataTable(pd.DataFrame.__ge__(pd.DataFrame(self),
                                                 pd.DataFrame(other)))

    # ========================================================================
    # Custom methods
    # ========================================================================

    def nrow(self):
        return nrow(self)

    def ncol(self):
        return ncol(self)

    def list_reduce(self):
        return list_reduce(self)

# ============================================================================
# Functions
# ============================================================================

def nrow(table):
    if isinstance(table, elemTypes):
        return 1

    if table is None:
        return 0

    try:
        return len(table.index)

    except:
        return len(table)


def ncol(table):
    if isinstance(table, elemTypes):
        return 1

    if table is None:
        return 0

    try:
        return len(table.columns)

    except:
        return len(table[0])

def list_reduce(table):

    # Check for element data
    if isinstance(table, elemTypes):
        return table

    # Checking for table data
    elif isinstance(table, pd.DataFrame):

        # Initialize dimensions
        numRow = nrow(table)
        numCol = ncol(table)

        # If either are 0 return None
        if numRow == 0 or numCol == 0:
            return None

        # If both are 1 return value
        elif numRow == 1 and numCol == 1:
            return table.iloc[0, 0]

        # If numRow is 1 return list
        elif numRow == 1:
            return list(table.iloc[0])

        # If numCol is 1 return list
        elif numCol == 1:
            return list(table.iloc[:, 0])

        # Else return list of lists
        else:
            return table.values.tolist()

    # If not one of the above, try to convert
    else:
        try:
            return list_reduce(DataTable(table))
        except:
            return table
