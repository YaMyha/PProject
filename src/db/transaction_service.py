from db.ORMmodels import BillingAddress, Customer, Merchant, PaymentDetail, Transaction
from db.database import async_session_factory


class TransactionService:

    @staticmethod
    async def insert_transaction(request):
        async with async_session_factory() as session:
            customer = Customer(
                customer_id=request.merchant.customerID,
            )

            merchant = Merchant(
                merchant_id=request.merchant.merchantID,
            )

            billing_address = BillingAddress(
                customer_id=request.merchant.customerID,
                first_name=request.customer.billingAddress.firstName,
                last_name=request.customer.billingAddress.lastName,
                mobile_no=request.customer.billingAddress.mobileNo,
                email_id=request.customer.billingAddress.emailId,
                address_line_1=request.customer.billingAddress.addressLine1,
                city=request.customer.billingAddress.city,
                state=request.customer.billingAddress.state,
                zip=request.customer.billingAddress.zip,
                country=request.customer.billingAddress.country,
            )

            payment_detail = PaymentDetail(
                card_number=request.transaction.paymentDetail.cardNumber,
                card_type=request.transaction.paymentDetail.cardType,
                exp_year=int(request.transaction.paymentDetail.expYear),
                exp_month=int(request.transaction.paymentDetail.expMonth),
                name_on_card=request.transaction.paymentDetail.nameOnCard,
                save_details=request.transaction.paymentDetail.saveDetails == "true",
                cvv=request.transaction.paymentDetail.cvv
            )
            session.add(customer)
            session.add(merchant)
            session.add(billing_address)
            session.add(payment_detail)
            await session.flush()

            transaction = Transaction(
                txn_amount=request.transaction.txnAmount,
                payment_type=request.transaction.paymentType,
                currency_code=request.transaction.currencyCode,
                txn_reference=request.transaction.txnReference,
                seriestype=request.transaction.seriestype,
                method=request.transaction.method,
                success_url=request.transaction.url.successURL,
                fail_url=request.transaction.url.failURL,
                merchant_id=request.merchant.merchantID,
                customer_id=request.merchant.customerID,
                payment_detail_id=payment_detail.id
            )

            session.add(transaction)
            await session.commit()
