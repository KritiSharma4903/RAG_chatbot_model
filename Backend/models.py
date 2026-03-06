from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class InvoiceItem(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

    model_config = ConfigDict(extra="allow")


class InvoiceSchema(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    items: Optional[List[InvoiceItem]] = None

    model_config = ConfigDict(extra="allow")
