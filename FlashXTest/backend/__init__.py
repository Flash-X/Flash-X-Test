import os
from .FlashTest import *

os.environ['FLASHTEST_BASE'] = os.path.dirname(os.path.abspath(__file__)) + os.sep + "FlashTest"
