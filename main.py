from speckle_automate import execute_automate_function

from src.function import automate_function
from src.inputs import FunctionInputs

if __name__ == "__main__":
    print("---------")
    print("| BEGIN |")
    print("---------")

    # Entry point: Execute the automate function with defined inputs.
    execute_automate_function(automate_function, FunctionInputs)
