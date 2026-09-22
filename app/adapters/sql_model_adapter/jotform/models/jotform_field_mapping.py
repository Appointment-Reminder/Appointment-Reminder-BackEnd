from typing import Optional

from sqlalchemy import UniqueConstraint, ForeignKey, Column
from sqlmodel import SQLModel, Field

from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping as JotformFieldMappingEntity

class JotformFieldMapping(SQLModel, table=True):
    __tablename__ = "jotform_field_mapping"
    __table_args__ = (
        UniqueConstraint("form_id", "target_key", "priority", name="uq_form_target_priority"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    form_id: int = Field(sa_column=Column(ForeignKey("jotform_forms.id", ondelete="CASCADE")))
    target_key: str = Field(index=True)
    qid: str
    subkey: Optional[str] = None
    priority: int = Field(default=0)


def mapping_to_domain(sql: JotformFieldMapping) -> JotformFieldMappingEntity:
    return JotformFieldMappingEntity(
        id=sql.id,
        form_id=sql.form_id,
        target_key=sql.target_key,
        qid=sql.qid,
        subkey=sql.subkey,
        priority=sql.priority,
    )
def mapping_apply_sql(sql: JotformFieldMapping, obj: JotformFieldMappingEntity) -> None:
    sql.target_key = obj.target_key
    sql.qid = obj.qid
    sql.subkey = obj.subkey
    sql.priority = obj.priority