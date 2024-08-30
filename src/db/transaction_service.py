from sqlalchemy import select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from configs.config import logger
from db.ORMmodels import BillingAddress, Customer, Merchant, PaymentDetail, Transaction
from db.database import async_session_factory
from validation import RequestModel


class TransactionService:
    @staticmethod
    async def insert_transaction(request: RequestModel):
        """
        Inserts a new transaction into the database, along with creating related records
        for the customer, merchant, billing address, and payment details.

        Args:
            request (RequestModel): An object containing transaction data and related information.
        Returns:
            None.
        """
        logger.info('Starting transaction insertion process.')
        try:
            async with async_session_factory() as session:
                logger.info('Created new database session.')
                await TransactionService.process_customer(session, request)
                await TransactionService.process_merchant(session, request)

                await TransactionService.create_billing_address(session, request)
                payment_detail = await TransactionService.create_payment_detail(session, request)

                # Perform a flush to the database to get the payment detail id
                await session.flush()
                logger.info('Added records to session and flushed.')

                await TransactionService.create_transaction(session, request, payment_detail)

                await session.commit()
                logger.info('Information was successfully committed to the database.')

        except Exception as e:
            logger.exception('An error occurred while inserting the transaction. Starting rollback...')
            await session.rollback()

            raise DatabaseError("Transaction insertion failed.")

    @staticmethod
    async def check_customer(session: AsyncSession, request: RequestModel):
        """
        Checks if a customer with the specified customer ID exists in the database.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing customer information.

        Returns:
            Customer or None: The `Customer` object if found, otherwise `None`.
        """
        customer_id = request.merchant.customerID
        logger.debug(f'Checking customer: {customer_id}')
        query = select(Customer).select_from(Customer).filter_by(customer_id=customer_id)
        customer = await session.execute(query)
        result = customer.scalars().first()
        if result:
            logger.debug(f'Customer was found: {customer_id}')
            return result

        logger.debug(f"Customer doesn't exist: {customer_id}")
        return None

    @staticmethod
    async def process_customer(session: AsyncSession, request: RequestModel):
        """
        Processes the customer data by checking if the customer exists in the database.
        If the customer does not exist, creates a new customer record.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing customer information.

        Returns:
            None.
        """
        customer = await TransactionService.check_customer(session, request)
        if customer:
            return

        customer = Customer(
            customer_id=request.merchant.customerID,
        )
        logger.debug(f'Created customer: {customer}')
        session.add(customer)
        return

    @staticmethod
    async def check_merchant(session: AsyncSession, request: RequestModel):
        """
        Checks if a merchant with the specified merchant ID exists in the database.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing merchant information.

        Returns:
            Merchant or None: The `Merchant` object if found, otherwise `None`.
        """
        merchant_id = request.merchant.merchantID
        logger.debug(f'Checking merchant: {merchant_id}')
        query = select(Merchant).select_from(Merchant).filter_by(merchant_id=merchant_id)
        merchant = await session.execute(query)
        result = merchant.scalars().first()
        if result:
            logger.debug(f'Merchant was found: {merchant_id}')
            return result

        logger.debug(f"Merchant doesn't exist: {merchant_id}")
        return None

    @staticmethod
    async def process_merchant(session: AsyncSession, request: RequestModel):
        """
        Processes the merchant data by checking if the merchant exists in the database.
        If the merchant does not exist, creates a new merchant record.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing merchant information.

        Returns:
            None
        """
        merchant = await TransactionService.check_merchant(session, request)
        if merchant:
            return

        merchant = Merchant(
            merchant_id=request.merchant.merchantID,
        )
        logger.debug(f'Created merchant: {merchant}')
        session.add(merchant)
        return

    @staticmethod
    async def create_billing_address(session: AsyncSession, request: RequestModel):
        """
        Creates a new billing address record in the database.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing billing address information.

        Returns:
            None
        """
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
        logger.debug(f'Created billing address: {billing_address}')
        session.add(billing_address)
        return

    @staticmethod
    async def create_payment_detail(session: AsyncSession, request: RequestModel):
        """
        Creates a new payment detail record in the database.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing payment detail information.

        Returns:
            PaymentDetail: The created `PaymentDetail` object.
        """
        payment_detail = PaymentDetail(
            card_number=request.transaction.paymentDetail.cardNumber,
            card_type=request.transaction.paymentDetail.cardType,
            exp_year=int(request.transaction.paymentDetail.expYear),
            exp_month=int(request.transaction.paymentDetail.expMonth),
            name_on_card=request.transaction.paymentDetail.nameOnCard,
            save_details=request.transaction.paymentDetail.saveDetails == "true",
            cvv=request.transaction.paymentDetail.cvv
        )
        logger.debug(f'Created payment detail: {payment_detail}')
        session.add(payment_detail)
        return payment_detail

    @staticmethod
    async def create_transaction(session: AsyncSession, request, payment_detail):
        """
        Creates a new transaction record in the database.

        Args:
            session (AsyncSession): The database session used to execute the query.
            request (RequestModel): The request object containing transaction information.
            payment_detail (PaymentDetail): The payment detail associated with the transaction.

        Returns:
            None.
        """
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
        logger.debug(f'Created transaction: {transaction}')
        session.add(transaction)


    # @staticmethod
    # async def insert_transaction(request: RequestModel):
    #     """
    #     Inserts a new transaction into the database, along with creating related records
    #     for the customer, merchant, billing address, and payment details.
    #
    #     Arguments:
    #     request (RequestModel): An object containing transaction data and related information.
    #     """
    #     logger.info('Starting transaction insertion process.')
    #     try:
    #         async with async_session_factory() as session:
    #             logger.info('Created new database session.')
    #             customer = Customer(
    #                 customer_id=request.merchant.customerID,
    #             )
    #             logger.debug(f'Created customer: {customer}')
    #
    #             merchant = Merchant(
    #                 merchant_id=request.merchant.merchantID,
    #             )
    #             logger.debug(f'Created merchant: {merchant}')
    #
    #             billing_address = BillingAddress(
    #                 customer_id=request.merchant.customerID,
    #                 first_name=request.customer.billingAddress.firstName,
    #                 last_name=request.customer.billingAddress.lastName,
    #                 mobile_no=request.customer.billingAddress.mobileNo,
    #                 email_id=request.customer.billingAddress.emailId,
    #                 address_line_1=request.customer.billingAddress.addressLine1,
    #                 city=request.customer.billingAddress.city,
    #                 state=request.customer.billingAddress.state,
    #                 zip=request.customer.billingAddress.zip,
    #                 country=request.customer.billingAddress.country,
    #             )
    #             logger.debug(f'Created billing address: {billing_address}')
    #
    #             payment_detail = PaymentDetail(
    #                 card_number=request.transaction.paymentDetail.cardNumber,
    #                 card_type=request.transaction.paymentDetail.cardType,
    #                 exp_year=int(request.transaction.paymentDetail.expYear),
    #                 exp_month=int(request.transaction.paymentDetail.expMonth),
    #                 name_on_card=request.transaction.paymentDetail.nameOnCard,
    #                 save_details=request.transaction.paymentDetail.saveDetails == "true",
    #                 cvv=request.transaction.paymentDetail.cvv
    #             )
    #             logger.debug(f'Created payment detail: {payment_detail}')
    #
    #             # Add the created objects to the session
    #             session.add(customer)
    #             session.add(merchant)
    #             session.add(billing_address)
    #             session.add(payment_detail)
    #             # Perform a flush to the database to get the payment detail id
    #             await session.flush()
    #             logger.info('Added records to session and flushed.')
    #
    #             if request.transaction.txnAmount == 0:
    #                 raise Exception
    #
    #             transaction = Transaction(
    #                 txn_amount=request.transaction.txnAmount,
    #                 payment_type=request.transaction.paymentType,
    #                 currency_code=request.transaction.currencyCode,
    #                 txn_reference=request.transaction.txnReference,
    #                 seriestype=request.transaction.seriestype,
    #                 method=request.transaction.method,
    #                 success_url=request.transaction.url.successURL,
    #                 fail_url=request.transaction.url.failURL,
    #                 merchant_id=request.merchant.merchantID,
    #                 customer_id=request.merchant.customerID,
    #                 payment_detail_id=payment_detail.id
    #             )
    #             logger.debug(f'Created transaction: {transaction}')
    #
    #             session.add(transaction)
    #             await session.commit()
    #             logger.info('Transaction successfully committed to the database.')
    #
    #     except Exception as e:
    #         logger.exception('An error occurred while inserting the transaction. Starting rollback...')
    #         await session.rollback()
    #
    #         raise DatabaseError("Transaction insertion failed.")
