from typing import Optional, Annotated
from sqlalchemy import String, Integer, Numeric, ForeignKey, Boolean, MetaData
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship

Base = declarative_base()
metadata = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]


class Customer(Base):
    __tablename__ = "customer"
    metadata = metadata

    id: Mapped[intpk]
    customer_id: Mapped[str] = mapped_column(String, unique=True)
    billing_address: Mapped["BillingAddress"] = relationship(
        "BillingAddress", back_populates="customer"
    )
    transaction: Mapped["Transaction"] = relationship(
        "Transaction", back_populates="customer"
    )


class Merchant(Base):
    __tablename__ = "merchant"
    metadata = metadata

    id: Mapped[intpk]
    merchant_id: Mapped[str] = mapped_column(String, unique=True)
    transaction: Mapped["Transaction"] = relationship(
        "Transaction", back_populates="merchant"
    )


class BillingAddress(Base):
    __tablename__ = "billing_address"
    metadata = metadata

    id: Mapped[intpk]
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customer.customer_id", ondelete="CASCADE")
    )
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    mobile_no: Mapped[str] = mapped_column(String)
    email_id: Mapped[str] = mapped_column(String)
    address_line_1: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String, nullable=True)
    zip: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="billing_address"
    )


class PaymentDetail(Base):
    __tablename__ = "payment_detail"
    metadata = metadata

    id: Mapped[intpk]

    card_number: Mapped[str] = mapped_column(String)
    card_type: Mapped[str] = mapped_column(String)
    exp_year: Mapped[int] = mapped_column(Integer)
    exp_month: Mapped[int] = mapped_column(Integer)
    name_on_card: Mapped[str] = mapped_column(String)
    save_details: Mapped[bool] = mapped_column(Boolean)
    cvv: Mapped[str] = mapped_column(String)

    transaction: Mapped["Transaction"] = relationship(
        "Transaction", back_populates="payment_detail"
    )


class Transaction(Base):
    __tablename__ = "transaction"
    metadata = metadata

    id: Mapped[intpk]
    txn_amount: Mapped[Numeric] = mapped_column(Numeric)
    payment_type: Mapped[str] = mapped_column(String)
    currency_code: Mapped[str] = mapped_column(String)
    txn_reference: Mapped[str] = mapped_column(String)
    seriestype: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    success_url: Mapped[str] = mapped_column(String)
    fail_url: Mapped[str] = mapped_column(String)
    merchant_id: Mapped[str] = mapped_column(
        ForeignKey("merchant.merchant_id", ondelete="CASCADE")
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customer.customer_id", ondelete="CASCADE")
    )
    payment_detail_id: Mapped[int] = mapped_column(
        ForeignKey("payment_detail.id", ondelete="CASCADE")
    )

    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="transaction")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="transaction")
    payment_detail: Mapped["PaymentDetail"] = relationship(
        "PaymentDetail", uselist=False, back_populates="transaction"
    )
