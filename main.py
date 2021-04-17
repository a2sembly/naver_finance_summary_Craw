from datetime import datetime
from parser_finance_Item import *

if __name__ == "__main__":
    code_list = get_item_code()
    for code in code_list:
        get_html(code)