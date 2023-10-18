from enum import Enum

class Split(str, Enum):
  EQUAL_AMTS = 'Equal Amounts'
  EXACT_AMTS = 'Exact Amounts'
  PERCENTAGES = 'Percentages'
  SHARES = 'Shares'