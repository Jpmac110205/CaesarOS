from typing import TypedDict

class CodeState(TypedDict):
    coder_output: dict
    testing_output: dict
    critiquing_output: dict

codeState = CodeState
