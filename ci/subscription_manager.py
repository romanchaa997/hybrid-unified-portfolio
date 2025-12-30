from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class SubscriptionPlan(Enum):
    """Subscription plan tiers"""
    STARTER = {"name": "Starter", "price": 10, "features": 5}
    PROFESSIONAL = {"name": "Professional", "price": 50, "features": 20}
    ENTERPRISE = {"name": "Enterprise", "price": 200, "features": "unlimited"}


class SubscriptionStatus(Enum):
    """Subscription status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class Subscription:
    """Subscription data class"""
    subscription_id: str
    customer_id: str
    plan: str
    status: SubscriptionStatus
    start_date: datetime
    renewal_date: datetime
    payment_method_id: str
    auto_renew: bool = True
    
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE and datetime.now() < self.renewal_date
    
    def days_until_renewal(self) -> int:
        return (self.renewal_date - datetime.now()).days


class SubscriptionManager:
    """Manage customer subscriptions"""
    
    def __init__(self, payment_processor=None):
        self.payment_processor = payment_processor
        self.subscriptions: Dict[str, Subscription] = {}
    
    def create_subscription(
        self,
        customer_id: str,
        plan: str,
        payment_method_id: str
    ) -> Dict:
        """Create new subscription"""
        try:
            subscription_id = f"sub_{customer_id}_{datetime.now().timestamp()}"
            
            subscription = Subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan=plan,
                status=SubscriptionStatus.PENDING,
                start_date=datetime.now(),
                renewal_date=datetime.now() + timedelta(days=30),
                payment_method_id=payment_method_id
            )
            
            self.subscriptions[subscription_id] = subscription
            logger.info(f"Subscription created: {subscription_id}")
            
            return {
                "status": "success",
                "subscription_id": subscription_id,
                "plan": plan,
                "start_date": str(subscription.start_date)
            }
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel subscription"""
        if subscription_id not in self.subscriptions:
            return {"status": "error", "error": "Subscription not found"}
        
        subscription = self.subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.CANCELED
        logger.info(f"Subscription canceled: {subscription_id}")
        
        return {
            "status": "success",
            "subscription_id": subscription_id,
            "canceled_at": str(datetime.now())
        }
    
    def pause_subscription(self, subscription_id: str) -> Dict:
        """Pause subscription"""
        if subscription_id not in self.subscriptions:
            return {"status": "error", "error": "Subscription not found"}
        
        subscription = self.subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.PAUSED
        logger.info(f"Subscription paused: {subscription_id}")
        
        return {"status": "success", "subscription_id": subscription_id}
    
    def resume_subscription(self, subscription_id: str) -> Dict:
        """Resume paused subscription"""
        if subscription_id not in self.subscriptions:
            return {"status": "error", "error": "Subscription not found"}
        
        subscription = self.subscriptions[subscription_id]
        if subscription.status != SubscriptionStatus.PAUSED:
            return {"status": "error", "error": "Subscription is not paused"}
        
        subscription.status = SubscriptionStatus.ACTIVE
        logger.info(f"Subscription resumed: {subscription_id}")
        
        return {"status": "success", "subscription_id": subscription_id}
    
    def upgrade_plan(self, subscription_id: str, new_plan: str) -> Dict:
        """Upgrade subscription plan"""
        if subscription_id not in self.subscriptions:
            return {"status": "error", "error": "Subscription not found"}
        
        subscription = self.subscriptions[subscription_id]
        old_plan = subscription.plan
        subscription.plan = new_plan
        
        logger.info(f"Plan upgraded from {old_plan} to {new_plan}")
        
        return {
            "status": "success",
            "subscription_id": subscription_id,
            "old_plan": old_plan,
            "new_plan": new_plan
        }
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        if subscription_id not in self.subscriptions:
            return None
        
        sub = self.subscriptions[subscription_id]
        return {
            "subscription_id": sub.subscription_id,
            "customer_id": sub.customer_id,
            "plan": sub.plan,
            "status": sub.status.value,
            "is_active": sub.is_active(),
            "days_until_renewal": sub.days_until_renewal(),
            "renewal_date": str(sub.renewal_date)
        }
    
    def get_customer_subscriptions(self, customer_id: str) -> List[Dict]:
        """Get all subscriptions for customer"""
        customer_subs = [
            sub for sub in self.subscriptions.values()
            if sub.customer_id == customer_id
        ]
        return [self.get_subscription(sub.subscription_id) for sub in customer_subs]
    
    def renew_subscription(self, subscription_id: str) -> Dict:
        """Renew subscription"""
        if subscription_id not in self.subscriptions:
            return {"status": "error", "error": "Subscription not found"}
        
        subscription = self.subscriptions[subscription_id]
        subscription.renewal_date = datetime.now() + timedelta(days=30)
        subscription.status = SubscriptionStatus.ACTIVE
        
        logger.info(f"Subscription renewed: {subscription_id}")
        
        return {
            "status": "success",
            "subscription_id": subscription_id,
            "new_renewal_date": str(subscription.renewal_date)
        }
