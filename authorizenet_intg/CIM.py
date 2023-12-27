import os, sys, random

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *

class CustomerInformationManager:
    
    def __init__(self):
        self.api_login_id = os.environ['API_LOGIN_ID']
        self.transaction_key = os.environ['TRANSACT_KEY']
        self.merchantAuth = apicontractsv1.merchantAuthenticationType()
        self.merchantAuth.name = self.api_login_id
        self.merchantAuth.transactionKey = self.transaction_key


    def create_customer_profile(self, cusid, cusname, cusemail):

        createCustomerProfile = apicontractsv1.createCustomerProfileRequest()
        createCustomerProfile.merchantAuthentication = self.merchantAuth
        createCustomerProfile.profile = apicontractsv1.customerProfileType(cusid, cusname, cusemail)

        controller = createCustomerProfileController(createCustomerProfile)
        controller.execute()

        response = controller.getresponse()

        if (response.messages.resultCode=="Ok"):
            print("Successfully created a customer profile with id: %s" % response.customerProfileId)
        else:
            print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

        return response
    
    def create_customer_payment_profile(self, customerProfileId):
        creditCard = apicontractsv1.creditCardType()
        creditCard.cardNumber = "4111111111111111"
        creditCard.expirationDate = "2035-12"

        payment = apicontractsv1.paymentType()
        payment.creditCard = creditCard

        billTo = apicontractsv1.customerAddressType()
        billTo.firstName = "John"
        billTo.lastName = "Snow"

        profile = apicontractsv1.customerPaymentProfileType()
        profile.payment = payment
        profile.billTo = billTo

        createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
        createCustomerPaymentProfile.merchantAuthentication = self.merchantAuth
        createCustomerPaymentProfile.paymentProfile = profile
        print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" %customerProfileId)
        createCustomerPaymentProfile.customerProfileId = str(customerProfileId)

        controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
        controller.execute()

        response = controller.getresponse()

        if (response.messages.resultCode=="Ok"):
            print("Successfully created a customer payment profile with id: %s" % response.customerPaymentProfileId)
        else:
            print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

        return response
    

    
if __name__ == "__main__":
    customer_manager = CustomerInformationManager()
    response = customer_manager.create_customer_profile("baba22", "blacksheep", "colorblind")
