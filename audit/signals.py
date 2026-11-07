"""
Signal handlers that write the audit log (SEC-6).

Each handler listens to a Django signal, so the other modules do not need to
call the audit module at all. pre_save remembers the old value of a status
field, and post_save logs only when the value actually changed.
The handlers use model labels ("rooms.Allocation") so the audit module still
works when a module is not installed yet.
"""
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .services import log_event


# ---- Logins and logouts -------------------------------------------------------------

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    log_event(action="login", user=user, request=request, details="Logged in")


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is not None:
        log_event(action="logout", user=user, request=request, details="Logged out")


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    # Only the typed email/SRN is kept. The password is never written anywhere.
    identifier = str(credentials.get("username") or credentials.get("email") or "")
    log_event(
        action="login_failed",
        identifier=identifier,
        request=request,
        details="Wrong email/SRN or password",
    )


# ---- Remember old values before a save ---------------------------------------------

TRACKED_FIELDS = {
    "accounts.User": "registration_status",
    "complaints.Complaint": "status",
    "complaints.LeaveRequest": "status",
    "fees.Fee": "amount",
}


@receiver(pre_save)
def remember_old_value(sender, instance, **kwargs):
    field = TRACKED_FIELDS.get(sender._meta.label)
    if field is None or instance._state.adding:
        return
    old = sender._default_manager.filter(pk=instance.pk).values_list(field, flat=True).first()
    instance._audit_old_value = old


def _changed(instance, field):
    old = getattr(instance, "_audit_old_value", None)
    return old, getattr(instance, field)


def _money(amount):
    return f"₹ {amount:,.2f}"


# ---- Log changes after a save -------------------------------------------------------

@receiver(post_save)
def on_saved(sender, instance, created, **kwargs):
    label = sender._meta.label
    handler = SAVE_HANDLERS.get(label)
    if handler:
        handler(instance, created)


def _user_saved(user, created):
    if created:
        return
    old, new = _changed(user, "registration_status")
    if old != new and new != get_user_model().Status.PENDING:
        log_event(action="registration", details=f"{user} registration {new}")


def _room_saved(room, created):
    if created:
        log_event(action="room_created", details=f"Room {room} added (capacity {room.capacity})")


def _allocation_saved(allocation, created):
    if created:
        log_event(action="allocated", details=f"{allocation.student} allocated to {allocation.room}")


def _fee_saved(fee, created):
    old, new = _changed(fee, "amount")
    if created or old != new:
        log_event(action="fee_set", details=f"Fee for {fee.student} set to {_money(new)}")


def _payment_saved(payment, created):
    if created:
        log_event(
            action="payment",
            details=f"Payment of {_money(payment.amount)} for {payment.student} on {payment.payment_date:%d %b %Y}",
        )


def _complaint_saved(complaint, created):
    if created:
        return
    old, new = _changed(complaint, "status")
    if old != new:
        log_event(action="complaint_status", details=f"Complaint by {complaint.student}: {old} -> {new}")


def _leave_saved(leave, created):
    if created:
        return
    old, new = _changed(leave, "status")
    if old != new:
        log_event(
            action="leave_decision",
            details=f"Leave of {leave.student} ({leave.start_date:%d %b %Y} to {leave.end_date:%d %b %Y}) {new}",
        )


SAVE_HANDLERS = {
    "accounts.User": _user_saved,
    "rooms.Room": _room_saved,
    "rooms.Allocation": _allocation_saved,
    "fees.Fee": _fee_saved,
    "fees.PaymentRecord": _payment_saved,
    "complaints.Complaint": _complaint_saved,
    "complaints.LeaveRequest": _leave_saved,
}


@receiver(post_delete)
def on_deleted(sender, instance, **kwargs):
    if sender._meta.label == "rooms.Allocation" and apps.is_installed("rooms"):
        log_event(action="deallocated", details=f"{instance.student} removed from {instance.room}")
