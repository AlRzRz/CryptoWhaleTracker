class Position:
  def __init__(self, asset, leverage, short, pnl, pnlPerc, collateral, liq, entry) -> None:
    self.asset = asset
    self.leverage = leverage
    self.short = short
    self.pnl = pnl
    self.pnlPerc = pnlPerc
    self.collateral = collateral
    self.size = int(collateral * leverage)
    self.liq = liq
    self.entry = entry

  def __str__(self) -> str:
    direction = "Short" if self.short else "Long"
    return (f"Position({self.asset}, Leverage: {self.leverage}x, {direction}, "
            f"PnL: {self.pnl} ({self.pnlPerc}%), Collateral: {self.collateral}, "
            f"Size: {self.size}, Liquidation Price: {self.liq}, Entry Price: {self.entry})")


class Order:
  def __init__(self, asset, short, orderType, size, trigger) -> None:
    self.asset = asset
    self.short = short
    self.orderType = orderType
    self.size = size
    self.trigger = trigger

  def __str__(self) -> str:
    direction = "Short" if self.short else "Long"
    return (f"Order({self.asset}, {direction}, Type: {self.orderType}, "
            f"Size: {self.size}, Trigger: {self.trigger})")


class Trader:
  def __init__(self, traderID, url) -> None:
    self.traderID = traderID
    self.url = url
    self.positions = []
    self.orders = []

  def addPosition(self, position):
    self.positions.append(position)

  def addPositionLst(self, positionLst):
    self.positions.extend(positionLst)

  def addOrder(self, order):
    self.orders.append(order)

  def addOrderLst(self, orderLst):
    self.orders.extend(orderLst)

  def __str__(self) -> str:
    return (f"Trader(ID: {self.traderID}, URL: {self.url}, "
            f"Positions: {len(self.positions)}, Orders: {len(self.orders)})")