import re


def find_position(content, target):
    """
    Find the position of the target in the content.

    Args:
        content (str): The content to search within.
        target (str): The target to search for.

    Returns:
        int: The position of the target in the content.

    """
    try:
        return re.search(target, content, re.DOTALL).start()
    except AttributeError:
        return -1


def fetch_question(content, target):
    try:
        start_pos = content.find("(" + target + ")\n")
    except AttributeError:
        return "Question not found"

    context = content[start_pos : start_pos + 500]
    return re.search(target + r".*?Question:\s*(.*?\n)", context, re.DOTALL).group(1)


def fetch_question_option(content, target):
    """
    Fetches the question option from the given content.

    Args:
        content (str): The content to search in.
        target (str): The target option to search for.

    Returns:
        str: The question option if found, otherwise "Question not found".
    """
    try:
        return re.search(
            r"\n[0-9]{1,2}:\s*([^\\n]*)\[" + target + r"\]\n",
            content,
            re.DOTALL,
        ).group(1)
    except AttributeError:
        return "Question not found"


def parse_multi_answer_var(content, target):
    """
    Formats the question option from the given content to include the question and the option

    Args:
        content (str): The content to search in.
        target (str): The target option to search for.

    Returns:
        str: The formatted question option if found, otherwise "Question not found".
    """
    try:
        option = fetch_question_option(content, target)
        question = fetch_question(content, target)

        return question + ": " + option
    except AttributeError:
        return "Question not found"


def parse_general(content, target):
    variable_parser = {
        "_3C": "Versão ordinalizada em 3 niveis da variável ",
        "_4C": "Versão ordinalizada em 4 niveis da variável ",
        "_5C": "Versão ordinalizada em 5 niveis da variável ",
        "_mean": "Média aritmética das respostas da variável ",
        "_nr": "Número de respostas da variável ",
        "_osp_codelow": "Limite inferior da escala original (Linearized Original Scale Posterior Prediction) da variável ",
        "_osp_codehigh": "Limite superior da escala original (Linearized Original Scale Posterior Prediction) da variável ",
        "_osp_sd": "Desvio padrão da escala original (Linearized Original Scale Posterior Prediction) da variável ",
        "_osp": "Escala original (Linearized Original Scale Posterior Prediction) da variável ",
        "_ord_codelow": "Limite inferior da escala ordinal da variável ",
        "_ord_codehigh": "Limite superior da escala ordinal da variável ",
        "_ord_sd": "Desvio padrão da escala ordinal da variável ",
        "_ord": "Escala ordinal (Measurement Model Estimates of Original Scale Value) da variável ",
        "_codehigh": "Limite superior da escala de estimativa de ponto da variável ",
        "_codelow": "Limite inferior da escala de estimativa de ponto da variável ",
        "_sd": "Desvio padrão da escala da variável ",
        "_[0-9]{1,2}": parse_multi_answer_var,
        "": fetch_question,
    }

    result = [
        item for item in variable_parser.items() if re.match(".*" + item[0], target)
    ][0]
    parent_var = re.sub(result[0], "", target)

    try:
        return result[1](content, parent_var)
    except:
        return result[1] + parent_var
