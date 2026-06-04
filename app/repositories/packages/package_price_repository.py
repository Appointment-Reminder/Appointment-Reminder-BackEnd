from sqlmodel import Session


class PackagePriceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    ##TODO create new price
    #TODO update price
    #TODO Delete price

    #TODO get_price at date
    #TODO Get current price
