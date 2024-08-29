from db.ORMmodels import BillingAddress, Customer, Merchant, PaymentDetail, Transaction
from db.database import async_session_factory


class TransactionService:

    # TODO: Add checks for customer/merchant existence in db
    @staticmethod
    async def insert_transaction(request):
        """
        Inserts a new transaction into the database, along with creating related records
        for the customer, merchant, billing address, and payment details.

        Arguments:
        request (RequestModel): An object containing transaction data and related information.
        """
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

            # Add the created objects to the session
            session.add(customer)
            session.add(merchant)
            session.add(billing_address)
            session.add(payment_detail)
            # Perform a flush to the database to get the payment detail id
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
