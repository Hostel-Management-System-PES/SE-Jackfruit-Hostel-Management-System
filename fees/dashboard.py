"""Dashboard summary cards supplied by the Fees module (REQ-13: student sees outstanding balance)."""
from .models import Fee
from .services import get_outstanding, rupees


def student_fee_card(user):
    fee = Fee.objects.filter(student=user).first()
    if fee is None:
        return {"label": "Outstanding fee", "value": "Not set"}
    return {
        "label": "Outstanding fee",
        "value": rupees(get_outstanding(user)),
        "sub": f"of {rupees(fee.amount)}",
    }
