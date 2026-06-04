from sqlmodel import Session


class PackagesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    #TODO Create package
    #TODO update package
    #TODO delete package

    #TODO get_by_category
    #TODO get_active_by_business
    #TODO find_by_alias


    ## TODO ADD Jotform package alias
    #TODO create alias
    #TODO get aliases for package
    #TODO delete alias
    #TODO update alias