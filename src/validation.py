from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, conint


class BillingAddress(BaseModel):
    firstName: str
    lastName: str
    mobileNo: str
    emailId: EmailStr
    addressLine1: str
    city: str
    state: Optional[str]
    zip: str
    country: constr(max_length=2)


class PaymentDetail(BaseModel):
    cardNumber: str
    cardType: str
    expYear: int
    expMonth: int
    nameOnCard: str
    saveDetails: bool
    cvv: str


class Url(BaseModel):
    successURL: str
    failURL: str


class Transaction(BaseModel):
    txnAmount: float
    paymentType: str
    currencyCode: str
    txnReference: str
    seriestype: Optional[str]
    method: Optional[str]
    paymentDetail: PaymentDetail
    url: Url


class Customer(BaseModel):
    billingAddress: BillingAddress


class Merchant(BaseModel):
    merchantID: str
    customerID: str


class RequestModel(BaseModel):
    lang: str
    merchant: Merchant
    customer: Customer
    transaction: Transaction
