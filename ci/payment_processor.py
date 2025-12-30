import stripe
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentRequest:
    """Payment request data class"""
    amount: int
    currency: str
    customer_id: str
    description: Optional[str] = None
    metadata: Optional[Dict] = None
    recurring: bool = False
    
    def validate(self) -> Tuple[bool, str]:
        """Validate payment request"""
        if self.amount <= 0:
            return False, "Amount must be positive"
        if not self.customer_id:
            return False, "Customer ID is required"
        if self.currency not in ['usd', 'eur', 'gbp', 'pln']:
            return False, f"Unsupported currency: {self.currency}"
        return True, "Valid"


class StripePaymentProcessor:
    """Payment processor using Stripe API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('STRIPE_API_KEY')
        stripe.api_key = self.api_key
    
    def create_payment_intent(
        self,
        request: PaymentRequest
    ) -> Dict:
        """Create a payment intent"""
        try:
            # Validate request
            is_valid, message = request.validate()
            if not is_valid:
                logger.error(f"Invalid payment request: {message}")
                return {
                    'status': PaymentStatus.FAILED.value,
                    'error': message
                }
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=request.amount,
                currency=request.currency,
                customer=request.customer_id,
                description=request.description,
                metadata=request.metadata or {},
                confirm=False
            )
            
            logger.info(f"Payment intent created: {intent.id}")
            return {
                'status': PaymentStatus.PENDING.value,
                'intent_id': intent.id,
                'client_secret': intent.client_secret,
                'amount': intent.amount,
                'currency': intent.currency
            }
        except stripe.error.CardError as e:
            logger.error(f"Card error: {e.message}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': e.message
            }
        except stripe.error.StripeServerError as e:
            logger.error(f"Stripe server error: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Payment service temporarily unavailable'
            }
    
    def confirm_payment(
        self,
        intent_id: str,
        payment_method_id: str
    ) -> Dict:
        """Confirm and process a payment"""
        try:
            intent = stripe.PaymentIntent.confirm(
                intent_id,
                payment_method=payment_method_id
            )
            
            if intent.status == 'succeeded':
                logger.info(f"Payment succeeded: {intent.id}")
                return {
                    'status': PaymentStatus.SUCCEEDED.value,
                    'intent_id': intent.id,
                    'charge_id': intent.charges.data[0].id if intent.charges.data else None
                }
            elif intent.status == 'requires_action':
                return {
                    'status': 'requires_action',
                    'intent_id': intent.id,
                    'client_secret': intent.client_secret
                }
            else:
                return {
                    'status': PaymentStatus.FAILED.value,
                    'intent_id': intent.id,
                    'error': f'Payment status: {intent.status}'
                }
        except stripe.error.StripeServerError as e:
            logger.error(f"Failed to confirm payment: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Payment confirmation failed'
            }
    
    def refund_payment(
        self,
        charge_id: str,
        amount: Optional[int] = None
    ) -> Dict:
        """Refund a payment"""
        try:
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=amount
            )
            
            logger.info(f"Refund created: {refund.id}")
            return {
                'status': PaymentStatus.REFUNDED.value,
                'refund_id': refund.id,
                'amount': refund.amount
            }
        except stripe.error.StripeServerError as e:
            logger.error(f"Refund failed: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Refund processing failed'
            }
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a recurring subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            
            logger.info(f"Subscription created: {subscription.id}")
            return {
                'status': 'active' if subscription.status == 'active' else 'pending',
                'subscription_id': subscription.id,
                'customer_id': subscription.customer,
                'period_start': subscription.current_period_start,
                'period_end': subscription.current_period_end
            }
        except stripe.error.StripeServerError as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Subscription creation failed'
            }
    
    def cancel_subscription(
        self,
        subscription_id: str
    ) -> Dict:
        """Cancel a subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Subscription cancelled: {subscription.id}")
            return {
                'status': 'cancelled',
                'subscription_id': subscription.id,
                'canceled_at': subscription.canceled_at
            }
        except stripe.error.StripeServerError as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Subscription cancellation failed'
            }
    
    def get_payment_status(
        self,
        intent_id: str
    ) -> Dict:
        """Get payment status"""
        try:
            intent = stripe.PaymentIntent.retrieve(intent_id)
            return {
                'status': intent.status,
                'amount': intent.amount,
                'currency': intent.currency,
                'created': intent.created
            }
        except stripe.error.StripeServerError as e:
            logger.error(f"Failed to retrieve payment status: {str(e)}")
            return {
                'status': PaymentStatus.FAILED.value,
                'error': 'Could not retrieve payment status'
            }
