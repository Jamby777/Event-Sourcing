class InsufficientFundsError(Exception):
    """Se lanza cuando se intenta retirar más dinero del disponible."""
    pass

class InvalidAmountError(Exception):
    """Se lanza cuando el monto ingresado no es válido (ej. <= 0)."""
    pass