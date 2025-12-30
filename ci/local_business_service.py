#!/usr/bin/env python3
"""Local Business Service: First MVP for Bakhmach-Business-Hub.

Manages local business operations:
- Client/customer database
- Service pricing and availability
- Appointment scheduling
- Local payment processing
- Business metrics tracking
"""

import asyncio, logging, uuid, json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    UNAVAILABLE = "unavailable"

@dataclass
class Client:
    client_id: str
    name: str
    phone: str
    email: str
    created_at: datetime

@dataclass
class Service:
    service_id: str
    name: str
    price: float
    duration_minutes: int
    status: ServiceStatus

class LocalBusinessService:
    """Manage local business operations."""
    
    def __init__(self, business_name: str = "Bakhmach Business"):
        self.business_name = business_name
        self.clients: Dict[str, Client] = {}
        self.services: Dict[str, Service] = {}
        self.appointments: Dict[str, Dict] = {}
        self.revenue = 0.0
    
    async def register_client(self, name: str, phone: str, email: str) -> Client:
        """Register new client."""
        client_id = str(uuid.uuid4())[:8]
        client = Client(
            client_id=client_id,
            name=name,
            phone=phone,
            email=email,
            created_at=datetime.now()
        )
        self.clients[client_id] = client
        logger.info(f"Client registered: {name}")
        return client
    
    async def add_service(self, name: str, price: float, duration: int) -> Service:
        """Add business service."""
        service_id = str(uuid.uuid4())[:8]
        service = Service(
            service_id=service_id,
            name=name,
            price=price,
            duration_minutes=duration,
            status=ServiceStatus.AVAILABLE
        )
        self.services[service_id] = service
        logger.info(f"Service added: {name} - {price} UAH")
        return service
    
    async def book_appointment(self, client_id: str, service_id: str, 
                               time_slot: datetime) -> Dict:
        """Book appointment for client."""
        if client_id not in self.clients:
            return {"error": "Client not found"}
        if service_id not in self.services:
            return {"error": "Service not found"}
        
        appt_id = str(uuid.uuid4())[:8]
        service = self.services[service_id]
        
        appointment = {
            "appointment_id": appt_id,
            "client_id": client_id,
            "service_id": service_id,
            "time_slot": time_slot.isoformat(),
            "price": service.price,
            "created_at": datetime.now().isoformat()
        }
        
        self.appointments[appt_id] = appointment
        logger.info(f"Appointment booked: {appt_id}")
        return appointment
    
    async def complete_payment(self, appointment_id: str, amount: float) -> bool:
        """Process payment for appointment."""
        if appointment_id not in self.appointments:
            logger.error(f"Appointment not found: {appointment_id}")
            return False
        
        self.revenue += amount
        self.appointments[appointment_id]["paid"] = True
        logger.info(f"Payment processed: {amount} UAH")
        return True
    
    async def get_business_metrics(self) -> Dict:
        """Get business performance metrics."""
        total_appointments = len(self.appointments)
        paid_appointments = sum(1 for a in self.appointments.values() if a.get("paid"))
        
        return {
            "business_name": self.business_name,
            "total_clients": len(self.clients),
            "total_services": len(self.services),
            "total_appointments": total_appointments,
            "completed_appointments": paid_appointments,
            "total_revenue": self.revenue,
            "average_transaction": self.revenue / paid_appointments if paid_appointments > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    logging.basicConfig(level=logging.INFO)
    biz = LocalBusinessService("Bakhmach Barbershop")
    
    # Demo
    client = await biz.register_client("Roman", "+380671234567", "roman@example.com")
    service = await biz.add_service("Haircut", 150.0, 30)
    appt = await biz.book_appointment(client.client_id, service.service_id, 
                                      datetime.now() + timedelta(hours=1))
    await biz.complete_payment(appt["appointment_id"], 150.0)
    
    metrics = await biz.get_business_metrics()
    print(json.dumps(metrics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
