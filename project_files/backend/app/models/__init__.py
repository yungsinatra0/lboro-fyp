from .user import *

from .vaccine import *
from .medication import *
from .healthdata import *
from .allergy import *

from .medhistory import *
from .other import *
from .share import *

from sqlmodel import SQLModel
SQLModel.model_rebuild()