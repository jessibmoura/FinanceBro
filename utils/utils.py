def parse_message(msg: str):
    """
    Functions takes the expense message and extracts three values from it: the float value 
    for the expense, the description - which is optional - and the category for the expense. 
    Both value and category are necessary.

    Parameters
    ----------
    msg: str
        Expense message sent to the bot
    """
    lines = [line.strip() for line in msg.strip().split('\n') if line.strip()]
    
    if len(lines) == 3:
        str_value, description, category = lines
    elif len(lines) == 2:
        str_value, category = lines
        description = None  # value None if no description is given
    else:
        raise ValueError("Invalid format: Use:\n<value>\n[description: optional]\n<category>")

    # Validação e conversão do valor
    try:
        float_value = float(str_value.replace(',', '.'))
    except ValueError:
        raise ValueError("Invalid value: Please only use numbers for the values.")

    return float_value, description, category

def parse_income_message(msg: str):
    """
    Functions takes the income message and extracts two values from it: the float value 
    for the income and the description - which is optional. 
    The value is necessary.

    Parameters
    ----------
    msg: str
        Expense message sent to the bot
    """
    lines = [line.strip() for line in msg.strip().split('\n') if line.strip()]
    
    if len(lines) == 2:
        str_value, description = lines
    elif len(lines) == 1:
        str_value = lines[0]
        description = None  # value None if no description is given
    else:
        raise ValueError("Invalid format: Use:\n<value>\n[description: optional]")

    # Validação e conversão do valor
    try:
        float_value = float(str_value.replace(',', '.'))
    except ValueError:
        raise ValueError("Invalid value: Please only use numbers for the values.")

    return float_value, description