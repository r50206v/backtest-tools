import builtins
import pandas as pd
from .exceptions import RequirementNotMeetException

def _check_params(params, list_to_check):
    if not isinstance(params, dict):
        raise RequirementNotMeetException('params should be a dictionary\n')
        
    for key in list_to_check:
        if key not in params.keys():
            raise RequirementNotMeetException('%s not in params\n' % (key))
        else:
            try:
                if isinstance(params[key], (pd.Series, pd.DataFrame)):
                    cond = any(pd.isnull(params[key]).values)
                else:
                    cond = any(pd.isnull(params[key]))
            except TypeError:
                cond = pd.isnull(params[key])
            if cond:
                raise RequirementNotMeetException('%s does not set value\n' % (key))
    return True

def _convert_type(params, list_to_convert, to):
    for k, v in params.items():
        if k in list_to_convert:
            if isinstance(to, str):
                params[k] = getattr(builtins, to)(v)
            else:
                params[k] = to(v)
    return params

def _valid_id(ID):
    if isinstance(ID, (int, float)):
        ID = str(ID)
    if not isinstance(ID, str):
        raise RequirementNotMeetException('indicator ID should be str(preferred), int, or float\n')
    return ID

def df2series(df):
    if isinstance(df, pd.DataFrame):
        return df.squeeze()
    return df