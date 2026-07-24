from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import stripe
from notifications.services import create_notification

from appointment.models import Appointment
from .models import Transaction

stripe.api_key = settings.STRIPE_SECRET_KEY


# create stripe checkout session
def initiate_stripe_payment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    transaction = get_object_or_404(
        Transaction,
        appointment=appointment
    )

    if transaction.payment_status == "completed":

        messages.success(
            request,
            "This appointment has already been paid."
        )

        return redirect(
            "patient_dashboard"
        )

    checkout_session = stripe.checkout.Session.create(

        payment_method_types=[
            "card"
        ],

        mode="payment",

        line_items=[

            {

                "price_data": {

                    "currency": "npr",

                    "product_data": {

                        "name":
                        f"Appointment with Dr. {appointment.doctor.name}"

                    },

                    "unit_amount": int(
                        float(transaction.amount) * 100
                    ),

                },

                "quantity": 1,

            }

        ],

        success_url=request.build_absolute_uri(

            reverse(
                "stripe_success"
            )

        ) + f"?transaction_id={transaction.id}",

        cancel_url=request.build_absolute_uri(

            reverse(
                "stripe_cancel"
            )

        ),

        metadata={

            "transaction_id": transaction.id,
            "appointment_id": appointment.appointment_id,

        }

    )

    transaction.stripe_session_id = checkout_session.id

    transaction.save()

    return redirect(
        checkout_session.url
    )


# payment success
def stripe_success(request):

    transaction_id = request.GET.get(
        "transaction_id"
    )

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id
    )

    session = stripe.checkout.Session.retrieve(
        transaction.stripe_session_id
    )

    if session.payment_status == "paid":

        transaction.payment_status = "completed"

        transaction.stripe_payment_id = session.payment_intent

        transaction.save()

    return render(

        request,

        "payments/payment_success.html",

        {

            "transaction": transaction,
            "appointment": transaction.appointment,

        }

    )


# payment cancelled
# payment cancelled
def stripe_cancel(request):

    return render(
        request,
        "payments/payment_cancel.html"
    )

# mark cash payment as completed
# @login_required
# def mark_cash_payment(request, transaction_id):

#     if not hasattr(request.user, "doctor"):
#         messages.error(
#             request,
#             "Permission denied."
#         )

#         return redirect("home")

#     transaction = get_object_or_404(
#         Transaction,
#         id=transaction_id
#     )

#     if transaction.payment_method != "cash":

#         messages.error(
#             request,
#             "Only cash payments can be updated."
#         )

#         return redirect(
#             "doctor_appointments"
#         )

#     transaction.payment_status = "completed"

#     transaction.save()

    # create payment notification
    # create payment notification
    appointment = transaction.appointment

    create_notification(
        patient=appointment.patient,
        appointment=appointment,
        title="Payment Successful",
        message=(
            f"Your payment of "
            f"Rs. {transaction.amount} "
            f"has been received."
        ),
        notification_type="payment",
        reminder_type="general"
    )
    
    messages.success(
        request,
        "Cash payment marked as completed."
    )

    return redirect(
        "doctor_appointments"
    )



@login_required
def my_receipt(request, transaction_id):

    transaction = get_object_or_404(
        Transaction.objects.select_related(
            "appointment",
            "appointment__doctor",
            "appointment__patient",
            "appointment__doctor__hospital",
        ),
        id=transaction_id,
        appointment__patient=request.user,
    )

    if transaction.payment_status != "completed":
        return render(
            request,
            "payments/payment_not_completed.html",
            status=403,
        )

    return render(
        request,
        "payments/receipt.html",
        {
            "transaction": transaction,
            "is_admin": False,
        },
    )


# patients payment history


@login_required
def my_payments(request):

    transactions = (
        Transaction.objects.select_related(
            "appointment",
            "appointment__doctor",
        )
        .filter(appointment__patient=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "payments/my_payments.html",
        {
            "transactions": transactions,
        },
    )


#invoice

@login_required
def my_invoice(request, transaction_id):

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        appointment__patient=request.user,
    )

    return render(
        request,
        "payments/invoice.html",
        {
            "transaction": transaction,
        },
    )



# patients invoice

@login_required
def my_invoice(request, transaction_id):

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        appointment__patient=request.user,
    )

    return render(
        request,
        "payments/invoice.html",
        {
            "transaction": transaction,
        },
    )