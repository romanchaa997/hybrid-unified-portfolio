from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class DealStage(enum.Enum):
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True)
    stripe_customer_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    company = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    company = Column(String)
    title = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    contact_id = Column(String, ForeignKey("contacts.id"), index=True)
    title = Column(String, index=True)
    description = Column(String)
    value = Column(Float)
    currency = Column(String, default="PLN")
    stage = Column(SQLEnum(DealStage), default=DealStage.PROSPECT, index=True)
    probability = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    close_date = Column(DateTime)


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    plan = Column(String)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.PENDING, index=True)
    amount = Column(Float)
    currency = Column(String, default="PLN")
    interval = Column(String, default="month")
    start_date = Column(DateTime, default=datetime.utcnow)
    renewal_date = Column(DateTime)
    canceled_at = Column(DateTime)
    payment_method_id = Column(String)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True)
    stripe_payment_id = Column(String, unique=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), index=True)
    amount = Column(Float)
    currency = Column(String, default="PLN")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    description = Column(String)
    payment_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True)
    stripe_invoice_id = Column(String, unique=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), index=True)
    amount = Column(Float)
    currency = Column(String, default="PLN")
    status = Column(String, index=True)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(String, primary_key=True)
    stripe_event_id = Column(String, unique=True, index=True)
    event_type = Column(String, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    payload = Column(String)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    action = Column(String)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    changes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
