import os
from .FlashTest import *
from .Webview import generate_flashx_testview

os.environ['FLASHTEST_BASE'] = os.path.dirname(os.path.abspath(__file__)) + os.sep + "FlashTest"
