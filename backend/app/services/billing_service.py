import stripe

from app.core.config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(email: str):
    """Create a new Stripe customer."""
    try:
        customer = stripe.Customer.create(
            email=email
        )
        return customer
    except stripe.error.InvalidRequestError as e:
        raise ValueError(f"Failed to create Stripe customer: {str(e)}")


def get_or_create_customer(email: str, customer_id: str = None):
    """Get an existing customer or create a new one."""
    if customer_id:
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.InvalidRequestError:
            # Customer doesn't exist, create a new one
            return create_customer(email)
    else:
        return create_customer(email)


def create_checkout_session(
    customer_id: str,
    price_id: str
):
    """Create a Stripe checkout session for subscription."""
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel"
        )
        return session
    except stripe.error.InvalidRequestError as e:
        raise ValueError(f"Failed to create checkout session: {str(e)}")