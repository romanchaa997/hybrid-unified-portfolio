import stripe
import json
import logging
from typing import Dict, Callable
from enum import Enum
import os

logger = logging.getLogger(__name__)


class WebhookEventType(Enum):
    """Stripe webhook event types"""
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_DELETED = "customer.deleted"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    CHARGE_REFUNDED = "charge.refunded"
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"


class StripeWebhookHandler:
    """Handle Stripe webhook events"""
    
    def __init__(self, endpoint_secret: str):
        self.endpoint_secret = endpoint_secret or os.getenv('STRIPE_WEBHOOK_SECRET')
        self.event_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Stripe"""
        try:
            stripe.Webhook.construct_event(payload, signature, self.endpoint_secret)
            return True
        except ValueError:
            logger.error("Invalid payload")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            return False
    
    def handle_event(self, event: Dict) -> Dict:
        """Handle webhook event"""
        event_type = event.get('type')
        event_id = event.get('id')
        
        logger.info(f"Processing webhook event: {event_type} ({event_id})")
        
        if event_type in self.event_handlers:
            try:
                handler = self.event_handlers[event_type]
                result = handler(event)
                logger.info(f"Event {event_id} processed successfully")
                return {"status": "success", "event_id": event_id}
            except Exception as e:
                logger.error(f"Error processing event {event_id}: {str(e)}")
                return {"status": "error", "error": str(e)}
        else:
            logger.warning(f"No handler for event type: {event_type}")
            return {"status": "unhandled", "event_type": event_type}


# Default event handlers
def handle_payment_intent_succeeded(event: Dict) -> None:
    """Handle successful payment"""
    payment_intent = event['data']['object']
    logger.info(f"Payment succeeded: {payment_intent['id']} - Amount: {payment_intent['amount']}")
    # Update customer account, send confirmation email, etc.


def handle_payment_intent_payment_failed(event: Dict) -> None:
    """Handle failed payment"""
    payment_intent = event['data']['object']
    logger.error(f"Payment failed: {payment_intent['id']}")
    # Send failure notification, retry logic, etc.


def handle_customer_subscription_created(event: Dict) -> None:
    """Handle subscription creation"""
    subscription = event['data']['object']
    logger.info(f"Subscription created: {subscription['id']} for customer {subscription['customer']}")
    # Update subscription database, send welcome email, etc.


def handle_customer_subscription_updated(event: Dict) -> None:
    """Handle subscription update"""
    subscription = event['data']['object']
    logger.info(f"Subscription updated: {subscription['id']}")
    # Update subscription status, plan changes, etc.


def handle_customer_subscription_deleted(event: Dict) -> None:
    """Handle subscription cancellation"""
    subscription = event['data']['object']
    logger.info(f"Subscription cancelled: {subscription['id']}")
    # Update subscription status, clean up customer data, etc.


def handle_charge_refunded(event: Dict) -> None:
    """Handle refund"""
    charge = event['data']['object']
    logger.info(f"Charge refunded: {charge['id']} - Amount: {charge['amount_refunded']}")
    # Update order status, send refund notification, etc.


def handle_invoice_paid(event: Dict) -> None:
    """Handle invoice payment"""
    invoice = event['data']['object']
    logger.info(f"Invoice paid: {invoice['id']} for customer {invoice['customer']}")
    # Send invoice receipt, update subscription status, etc.


def handle_invoice_payment_failed(event: Dict) -> None:
    """Handle invoice payment failure"""
    invoice = event['data']['object']
    logger.error(f"Invoice payment failed: {invoice['id']}")
    # Send payment failure notification, retry logic, etc.


# Create default webhook handler with all event handlers registered
def create_webhook_handler(endpoint_secret: str) -> StripeWebhookHandler:
    """Create and configure webhook handler"""
    handler = StripeWebhookHandler(endpoint_secret)
    
    # Register all event handlers
    handler.register_handler(
        WebhookEventType.PAYMENT_INTENT_SUCCEEDED.value,
        handle_payment_intent_succeeded
    )
    handler.register_handler(
        WebhookEventType.PAYMENT_INTENT_PAYMENT_FAILED.value,
        handle_payment_intent_payment_failed
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_CREATED.value,
        handle_customer_subscription_created
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_UPDATED.value,
        handle_customer_subscription_updated
    )
    handler.register_handler(
        WebhookEventType.SUBSCRIPTION_DELETED.value,
        handle_customer_subscription_deleted
    )
    handler.register_handler(
        WebhookEventType.CHARGE_REFUNDED.value,
        handle_charge_refunded
    )
    handler.register_handler(
        WebhookEventType.INVOICE_PAID.value,
        handle_invoice_paid
    )
    handler.register_handler(
        WebhookEventType.INVOICE_PAYMENT_FAILED.value,
        handle_invoice_payment_failed
    )
    
    logger.info("Webhook handler initialized with all event handlers")
    return handler
