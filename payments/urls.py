from django.urls import path
from . import views


urlpatterns = [

    # stripe payment
    path(
        "stripe/pay/<int:appointment_id>/",
        views.initiate_stripe_payment,
        name="stripe_payment"
    ),

    # stripe success
    path(
        "stripe/success/",
        views.stripe_success,
        name="stripe_success"
    ),

    # stripe cancel
    path(
        "stripe/cancel/",
        views.stripe_cancel,
        name="stripe_cancel"
    ),

    #invoice

    path(
        "invoice/<int:transaction_id>/",
        views.my_invoice,
        name="my_invoice",
    ),


    # patient invoice
    path(
        "invoice/<int:transaction_id>/",
        views.my_invoice,
        name="my_invoice",
    ),

    # patient receipt
    path(
        "receipt/<int:transaction_id>/",
        views.my_receipt,
        name="my_receipt",
    ),
    #patient receipt
    path(
        "receipt/<int:transaction_id>/",
        views.my_receipt,
        name="my_receipt",
    ),
    
    #patient payment history

    path(
        "my-payments/",
        views.my_payments,
        name="my_payments",
    ),

]