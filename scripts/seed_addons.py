# seed_addons.py
from datetime import datetime

from sqlmodel import Session, select

from app.adapters.session import engine
from app.adapters.sql_model_adapter.addon.models.addon import Addon as AddonSQL
from app.adapters.sql_model_adapter.addon.models.addon_price import AddonPrice as AddonPriceSQL
from app.adapters.sql_model_adapter.addon.models.addon_commission import AddonCommission as AddonCommissionSQL
from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory
from app.adapters.sql_model_adapter.user.models.user import User
from app.domain.addon.models.addon_alias import normalize_alias

BUSINESS_ID = 7
CATEGORY_ID = 7  # "Standard Sessions"
EFFECTIVE_FROM = datetime(2026, 1, 1)  # backdate before your earliest appointment

ADDONS = [
    # name, price, photographer_share, has_quantity
    ("Short Video – €30 (30–60 Seconds Portrait Orientation)", 30, 15, False),
    ("All Unedited Photos Full Gallery – €60 (Same-Day Delivery)", 60, 60, False),
    ("Express 1-Day Editing – €70 (Subject To Availability)", 70, 35, False),
    ("Extra Edited Photos – €30 (Per 10 Edited Photos)", 30, 15, True),
    ("Additional Person", 20, 10, True),
    ("Privacy Opt Out Casual", 80, 40, False),
    ("Privacy Opt Out Event", 150, 75, False),
    ("None", 0, 0, False),
    ("To Decide Later", 0, 0, False),
    ("Short Video – €30 (30–60 Seconds Portrait Orientation, Simple Social Media Video.)", 30, 15, False),
    ("Reel Video – €30 (15–60 Seconds Portrait Orientation, Simple Social Media Video.)", 30, 15, False),
]


def main():
    with Session(engine) as db:
        members = db.exec(
            select(BusinessMember).where(BusinessMember.business_id == BUSINESS_ID)
        ).all()
        name_to_addon_id = {}

        for name, price, photog_share, has_quantity in ADDONS:
            alias = normalize_alias(name)  # matches the add-on label from jotform submissions
            addon = db.exec(
                select(AddonSQL).where(AddonSQL.business_id == BUSINESS_ID, AddonSQL.jotform_alias == alias)
            ).first()

            if addon is None:
                addon = AddonSQL(
                    business_id=BUSINESS_ID,
                    category_id=CATEGORY_ID,
                    name=name,
                    jotform_alias=alias,
                    is_active=True,
                    has_quantity=has_quantity,
                    has_duration=False,
                )
                db.add(addon)
                db.commit()
                db.refresh(addon)

                db.add(AddonPriceSQL(addon_id=addon.id, price=price, effective_from=EFFECTIVE_FROM))

                # member commission = what the business keeps: price - photographer share
                for member in members:
                    db.add(AddonCommissionSQL(
                        business_member_id=member.id,
                        addon_id=addon.id,
                        commission_amount=price - photog_share,
                        commission_isPercentage=False,
                        effective_from=EFFECTIVE_FROM,
                    ))
                db.commit()

            name_to_addon_id[name] = addon.id

        print(name_to_addon_id)


if __name__ == "__main__":
    main()
