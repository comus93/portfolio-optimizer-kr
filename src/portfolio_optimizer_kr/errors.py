class PortfolioOptimizerError(Exception):
    """Base exception for portfolio-optimizer-kr."""


class DataValidationError(PortfolioOptimizerError):
    """Raised when input market data cannot satisfy the specification."""


class InfeasibleOptimizationError(PortfolioOptimizerError):
    """Raised when portfolio constraints or an objective are infeasible."""


class SolverError(PortfolioOptimizerError):
    """Raised when a numerical solver does not return a usable solution."""
