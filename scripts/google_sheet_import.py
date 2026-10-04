# scripts/import_appointments.py
import pandas as pd
from datetime import datetime
from sqlmodel import Session, select


from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission
from app.adapters.sql_model_adapter.user.models.user import User
from app.adapters.sql_model_adapter.package.models.package import Package
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment
from app.adapters.sql_model_adapter.jotform.models.jotform import JotformCredential, JotformForm, JotformFormAssignment
from app.adapters.sql_model_adapter.jotform.models.jotform_field_mapping import JotformFieldMapping


from app.adapters.session import engine
from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice as PackagePriceSQL
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment as AppointmentSQL
from app.adapters.sql_model_adapter.addon.models.unresolved_addon import UnresolvedAddon as UnresolvedAddonSQL

BUSINESS_ID = 7

# fill from business_members table (SELECT id, user_id FROM business_members WHERE business_id=1)
PHOTOGRAPHER_MEMBER_MAP = {
    "Gabby Sy": 7,
    "Jessica Malmenaide": 8,
    "Pinhas Cohen": 9,
    "Carolina Evanno": 10,
}

def parse_date(raw):
    try:
        dt = pd.to_datetime(raw)
        if dt.year < 2000:
            return None  # garbage jotform export date (1/9/1900, 1970-01-01, etc.)
        return dt.to_pydatetime()
    except Exception:
        return None

def get_price_at_date(db: Session, package_id: int, at_date: datetime) -> PackagePriceSQL | None:
    return db.exec(
        select(PackagePriceSQL)
        .where(PackagePriceSQL.package_id == package_id)
        .where(PackagePriceSQL.effective_from <= at_date)
        .order_by(PackagePriceSQL.effective_from.desc())
        .limit(1)
    ).first()

def main(path: str):
    df = pd.read_excel(path)

    with Session(engine) as db:
        packages_by_alias = {
            p.jotform_alias.strip(): p
            for p in db.exec(select(PackageSQL).where(PackageSQL.business_id == BUSINESS_ID)).all()
        }

        skipped = []
        imported = 0

        for _, row in df.iterrows():
            photographer_name = f"{row.iloc[5]} {row.iloc[6]}".strip()
            member_id = PHOTOGRAPHER_MEMBER_MAP.get(photographer_name)

            package_name = normalize(str(row["Name"]))
            package = packages_by_alias.get(package_name)

            appt_date = parse_date(row["Appointment Date"])

            if member_id is None or package is None or appt_date is None:
                skipped.append((row.get("appointment ID"), photographer_name, package_name, appt_date))
                continue

            price_row = get_price_at_date(db, package.id, appt_date)

            sql_obj = AppointmentSQL(
                business_id=BUSINESS_ID,
                member_id=member_id,
                form_id=None,

                package_id=package.id,
                package_price_id=price_row.id if price_row else None,

                client_first_name=str(row.iloc[9]),
                client_last_name=str(row.iloc[10]),
                client_phone=str(row["phone"]),
                client_email=str(row["email"]),

                price_at_booking=float(row["Price"]),
                deposit_amount=float(row["depositAmount"]),
                remaining_amount=float(row["Price"]) - float(row["depositAmount"]),
                commission_percent_at_booking=None,
                commision_amount_at_booking=float(row["businessOwnerShare"]),  # flat amount, per your earlier note

                appointment_date=appt_date,
                appointment_location=None,
                appointment_duration=int(row["duration"]),
                appointment_note=None,
                number_of_persons=0,
                privacy_opt_out=None,

                status="confirmed",
                created_at=parse_date(row["Submission Date"]) or datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(sql_obj)
            # the sheet's add-ons are free text: keep each as an Unresolved Add-on for staff to resolve
            raw_addons = row["Add-ons"]
            if raw_addons not in (None, "None") and str(raw_addons).strip() not in ("", "nan"):
                db.flush()
                for label in str(raw_addons).splitlines():
                    if label.strip():
                        db.add(UnresolvedAddonSQL(appointment_id=sql_obj.id, raw_label=label.strip()))
            imported += 1

        db.commit()
        print(f"Imported {imported}. Skipped {len(skipped)}:")

        # add near the top of main(), before the loop — rules out cause #2 immediately
        existing = db.exec(select(PackageSQL).where(PackageSQL.business_id == BUSINESS_ID)).all()
        print(f"Packages found for business {BUSINESS_ID}: {[(p.id, repr(p.jotform_alias)) for p in existing]}")
        if not existing:
            raise RuntimeError(
                "No packages seeded for this business_id — run seed_business.py first / check BUSINESS_ID")

        for s in skipped:
            print(s)

def normalize(s: str) -> str:
    return s.strip().replace("\u00a0", " ").strip()

if __name__ == "__main__":

    main("appointments.xlsx")