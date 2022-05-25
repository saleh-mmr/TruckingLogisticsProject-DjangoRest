from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import models
from .Authorization import IsDriver, IsApplicant
from .Authentication import token_expire_handler
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from stream_chat import StreamChat


# AUTHENTICATION SERVICE
@api_view(['POST'])
@permission_classes(())
def signUp(request):
    try:
        data = request.data
        data_first_name = data['firstname']
        data_last_name = data['lastname']
        data_username = data['pnumber']
        data_phone_number = data['pnumber']
        data_type = data['type']
        data_password = data['password']
        data_confirm_password = data['cpassword']
        if data_confirm_password == data_password:
            if data_type == "1":
                newUser = models.MyUser.objects.create(first_name=data_first_name, last_name=data_last_name,
                                                       username=data_username, phone=data_phone_number,
                                                       type=True)
            else:
                newUser = models.MyUser.objects.create(first_name=data_first_name, last_name=data_last_name,
                                                       username=data_username, phone=data_phone_number,
                                                       type=False)
            newUser.set_password(data_password)
            newUser.save()
            if newUser.type:
                newDriver = models.Driver.objects.create(user=newUser, can_accept=True)
            else:
                newApplicant = models.Applicant.objects.create(user=newUser)
            if newUser:
                return Response({"flag": True}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "Something might be Wrong!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# AUTHENTICATION SERVICE
@api_view(['POST'])
@permission_classes(())
def signIn(request):
    try:
        params = request.data
        user = authenticate(username=params['user'], password=params['pass'], )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            is_expired, token = token_expire_handler(token)
            if models.Driver.objects.filter(user=user):
                userType = True
            else:
                userType = False
            tmp_response = {
                'type': userType,
                'access': token.key,
                'userid': token.user_id
            }
            return Response(tmp_response, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong username or password"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# AUTHENTICATION SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signOut(request):
    try:
        django_logout(request)
        Token.objects.filter(key=request.headers.get('Authorization')[7:]).delete()
        return Response({"message": "Logout Successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs in logout!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# AUTHENTICATION SERVICE
@api_view(['POST'])
@permission_classes(())
def isRegistered(request):
    try:
        data = request.data
        data_phone = data['pnumber']
        found_user = models.MyUser.objects.filter(phone=data_phone)
        if found_user:
            return Response({"flag": True}, status=status.HTTP_200_OK)
        return Response({"flag": False}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# AUTHENTICATION SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkUserType(request):
    try:
        if models.Driver.objects.filter(user=request.user):
            return Response({"flag": True}, status=status.HTTP_200_OK)
        else:
            return Response({"flag": False}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TEST SERVICE
@api_view(['POST'])
@permission_classes(())
def isValid(request):
    try:
        data = request.data
        data_code = data['code']
        list = [5219, 4950, 8655, 1361, 7081]
        if data_code in list:
            return Response({"flag": True}, status=status.HTTP_200_OK)
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# FORMS SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def getDriverInfo(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        rsp = {"driverId": current_driver.id,
               "driverName": current_driver.user.first_name + " " + current_driver.user.last_name,
               "driverPhone": current_driver.user.phone
               }
        print()
        return Response({"list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# FORMS SERVICE
@api_view(['GET'])
@permission_classes(())
def getNumbers(request):
    try:
        driverNum = models.Driver.objects.filter().count()
        applicantNum = models.Applicant.objects.filter().count()
        unloaded = models.TripStatus.objects.get(title="تخلیه شده")
        tripNum = models.Trip.objects.filter(status=unloaded).count()
        carrierNum = models.Carrier.objects.count()
        rsp = {"driverNum": driverNum, "applicantNum": applicantNum, "tripNum": tripNum, "carrierNum": carrierNum}
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# FORMS SERVICE
@api_view(['GET'])
@permission_classes(())
def getLoadType(request):
    try:
        rsp = []
        for i in models.LoadType.objects.filter():
            rsp.append(i.title)
        return Response({"list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# FORMS SERVICE
@api_view(['GET'])
@permission_classes(())
def getClassifications(request):
    try:
        rsp = []
        for i in models.Classification.objects.filter():
            rsp.append(i.title)
        return Response({"list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def showCarriers(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        carriers = models.Carrier.objects.filter(driver=current_driver)
        rsp = []
        flag = False
        for i in carriers:
            rsp.append({"model": i.model, "year": i.year, "tag": i.tag,
                        "classification": i.classification.title})
            flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def newCarrier(request):
    try:
        data = request.data
        current_user = request.user
        model = data["model"]
        tag = data["tag"]
        year = data["year"]
        classification = data["classification"]
        current_driver = models.Driver.objects.get(user=current_user)
        isSubmitted = models.Carrier.objects.filter(tag=tag)
        if not isSubmitted:
            if models.Classification.objects.filter(title=classification):
                carrierClassification = models.Classification.objects.get(title=classification)
                models.Carrier.objects.create(driver=current_driver, model=model, tag=tag, year=year,
                                              classification=carrierClassification)
                return Response({"message": "New Truck added Successfully!", "flag": True}, status=status.HTTP_200_OK)
            return Response({"message": "class", "flag": False}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "tag", "flag": False}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def showRequestList(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        carriers = models.Carrier.objects.filter(driver=current_driver)
        rsp = []
        flag = False
        for carrier in carriers:
            if models.RequiredClass.objects.filter(classification=carrier.classification):
                for i in models.RequiredClass.objects.filter(classification=carrier.classification):
                    if not models.Trip.objects.filter(request=i.request):
                        rsp.append({"reqid": i.request.id, "origin": i.request.origin,
                                    "destination": i.request.destination, "loading_date": i.request.loading_date,
                                    "unloading_date": i.request.unloading_date,
                                    "proposed_price": i.request.proposed_price})
                        flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def showRequestDetail(request):
    try:
        data = request.data
        current_user = request.user
        request_id = data["request_id"]
        current_request = models.Request.objects.get(id=request_id)
        rsp = {"reqid": current_request.id,
               "origin": current_request.origin,
               "destination": current_request.destination,
               "loadingDate": current_request.loading_date,
               "unloadingDate": current_request.unloading_date,
               "loadType": current_request.load_type.title,
               "weight": current_request.weight,
               "value": current_request.value,
               "description": current_request.description,
               "proposedPrice": current_request.proposed_price,
               "receiverName": current_request.receiver_name,
               "receiverPhone": current_request.receiver_phone,
               "senderPhone": current_request.applicant.user.phone,
               "senderName": current_request.applicant.user.first_name + " " + current_request.applicant.user.last_name,
               }
        return Response({"rsp": rsp, "flag": True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def acceptRequest(request):
    try:
        data = request.data
        current_user = request.user
        request_id = data["request_id"]
        current_driver = models.Driver.objects.get(user=current_user)
        current_driver_carriers = models.Carrier.objects.filter(driver=current_driver)
        if models.Request.objects.filter(id=request_id):
            current_request = models.Request.objects.get(id=request_id)
            if current_driver.can_accept:
                if not models.Trip.objects.filter(request=current_request):
                    for carrier in current_driver_carriers:
                        if models.RequiredClass.objects.filter(request=current_request,
                                                               classification=carrier.classification):
                            new_status = models.TripStatus.objects.get(title='پذیرفته شده')
                            models.Trip.objects.create(request=current_request, carrier=carrier, status=new_status)
                            current_driver.can_accept = False
                            current_driver.save()
                            return Response({"message": "OK!"}, status=status.HTTP_200_OK)
                    return Response({"message": "You dont have required truck!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                return Response({"message": "This request has an active trip!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response({"message": "You have an active trip!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({"message": "This is not a valid request!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def showActiveTrip(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        carriers = models.Carrier.objects.filter(driver=current_driver)
        newStatus = models.TripStatus.objects.get(title="پذیرفته شده")
        loadedStatus = models.TripStatus.objects.get(title="بارگیری شده")
        rsp = []
        flag = False
        for carrier in carriers:
            for trip in models.Trip.objects.filter(carrier=carrier):
                if trip.status == newStatus or trip.status == loadedStatus:
                    if trip.status == newStatus:
                        a = "پذیرفته شده"
                    else:
                        a = "بارگیری شده"
                    rsp.append({"tripid": trip.id,
                                "carrierTag": trip.carrier.tag,
                                "status": a,
                                "requestOrigin": trip.request.origin,
                                "requestDestination": trip.request.destination,
                                "requestReceiverName": trip.request.receiver_name,
                                "requestReceiverPhone": trip.request.receiver_phone,
                                "requestSenderName": trip.request.applicant.user.first_name + " " + trip.request.applicant.user.last_name,
                                "requestSenderPhone": trip.request.applicant.user.phone
                                })
                    flag = True
        return Response({"list": rsp, 'flag': flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def showFinishedTrip(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        carriers = models.Carrier.objects.filter(driver=current_driver)
        unloadedStatus = models.TripStatus.objects.get(title="تخلیه شده")
        rsp = []
        flag = False
        for carrier in carriers:
            for trip in models.Trip.objects.filter(carrier=carrier):
                if trip.status == unloadedStatus:
                    rsp.append({"tripid": trip.id,
                                "carrierTag": trip.carrier.tag,
                                "status": "تخلیه شده",
                                "requestOrigin": trip.request.origin,
                                "requestid": trip.request.id,
                                "requestDestination": trip.request.destination,
                                "requestReceiverName": trip.request.receiver_name,
                                "requestReceiverPhone": trip.request.receiver_phone,
                                "requestSenderName": trip.request.applicant.user.first_name + " " + trip.request.applicant.user.last_name,
                                "requestSenderPhone": trip.request.applicant.user.phone
                                })
                    flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def loadAnnouncement(request):
    try:
        data = request.data
        current_trip = models.Trip.objects.get(id=data["tripId"])
        current_driver = models.Driver.objects.get(user=request.user)
        if current_trip.carrier.driver == current_driver:
            loaded_status = models.TripStatus.objects.get(title='بارگیری شده')
            current_trip.status = loaded_status
            current_trip.save()
            return Response({"currentStatus": "بارگیری شده"}, status=status.HTTP_200_OK)
        return Response({"message": "Just The owner of the trip can edit status!"},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DRIVER DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def unloadAnnouncement(request):
    try:
        data = request.data
        current_trip = models.Trip.objects.get(id=data["tripId"])
        current_driver = models.Driver.objects.get(user=request.user)
        loaded_status = models.TripStatus.objects.get(title='بارگیری شده')

        if current_trip.carrier.driver == current_driver:
            if current_trip.status == loaded_status:
                unloaded_status = models.TripStatus.objects.get(title='تخلیه شده')
                current_trip.status = unloaded_status
                current_trip.save()
                current_driver.can_accept = True
                current_driver.save()
                return Response({"currentStatus": "تخلیه شده"}, status=status.HTTP_200_OK)
            return Response({"message": "You should load first"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({"message": "Just The owner of the trip can edit status!"},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApplicant])
def newRequest(request):
    try:
        data = request.data
        current_user = request.user
        current_applicant = models.Applicant.objects.get(user=current_user)
        origin = data["origin"]
        loading_date = data["loadingDate"]
        destination = data["destination"]
        unloading_date = data["unloadingDate"]
        weight = data["weight"]
        value = data["value"]
        description = data["description"]
        proposed_price = data["proposedPrice"]
        receiver_name = data["receiverName"]
        receiver_phone = data["receiverPhone"]
        truck_classification_requirement = data["truckClassificationRequirement"]
        load_type = models.LoadType.objects.get(title=data["loadType"])
        SpecificReq = models.Request.objects.filter(applicant=current_applicant, origin=origin,
                                                    loading_date=loading_date, destination=destination,
                                                    unloading_date=unloading_date, load_type=load_type,
                                                    weight=weight, value=value, description=description,
                                                    proposed_price=proposed_price, receiver_name=receiver_name,
                                                    receiver_phone=receiver_phone)
        if not SpecificReq:
            new_request = models.Request.objects.create(applicant=current_applicant, origin=origin,
                                                        loading_date=loading_date, destination=destination,
                                                        unloading_date=unloading_date, load_type=load_type,
                                                        weight=weight, value=value, description=description,
                                                        proposed_price=proposed_price, receiver_name=receiver_name,
                                                        receiver_phone=receiver_phone)
            for truck_classification in truck_classification_requirement:
                if models.Classification.objects.filter(title=truck_classification):
                    truck_class = models.Classification.objects.get(title=truck_classification)
                    if not models.RequiredClass.objects.filter(classification=truck_class, request=new_request):
                        models.RequiredClass.objects.create(classification=truck_class, request=new_request)
            return Response({"message": "New Request created Successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You already have a same request!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsApplicant])
def cancelRequest(request):
    try:
        data = request.data
        current_user = request.user
        current_applicant = models.Applicant.objects.get(user=current_user)
        request_id = data["request_id"]
        current_request = models.Request.objects.get(id=request_id)
        if current_request.applicant == current_applicant:
            if not models.Trip.objects.filter(request=current_request):
                models.Request.objects.get(id=request_id).delete()
                return Response({"message": "Request canceled Successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "This Request has an active trip"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "You cannot cancel other's Requests"}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantRequestList(request):
    try:
        current_applicant = models.Applicant.objects.get(user=request.user)
        rsp = []
        requests = models.Request.objects.filter(applicant=current_applicant)
        flag = False
        for request in requests:
            if not models.Trip.objects.filter(request=request):
                rsp.append({"req_id": request.id,
                            "origin": request.origin,
                            "loading_date": request.loading_date,
                            "destination": request.destination,
                            "unloading_date": request.unloading_date,
                            "load_type": request.load_type.title,
                            "weight": request.weight})
                flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantTripList(request):
    try:
        current_applicant = models.Applicant.objects.get(user=request.user)
        rsp = []
        flag = False
        requests = models.Request.objects.filter(applicant=current_applicant)
        for current_request in requests:
            if models.Trip.objects.filter(request=current_request):
                trip = models.Trip.objects.get(request=current_request)
                newStatus = models.TripStatus.objects.get(title="پذیرفته شده")
                loadedStatus = models.TripStatus.objects.get(title="بارگیری شده")
                if trip.status == newStatus or trip.status == loadedStatus:
                    rsp.append({"trip_id": trip.id,
                                "origin": trip.request.origin,
                                "loading_date": trip.request.loading_date,
                                "destination": trip.request.destination,
                                "unloading_date": trip.request.unloading_date,
                                "load_type": trip.request.load_type.title,
                                "weight": trip.request.weight,
                                "carrier_class": trip.carrier.classification.title,
                                "carrier_model": trip.carrier.model,
                                "carrier_tag": trip.carrier.tag,
                                "driverPhone": trip.carrier.driver.user.phone,
                                "driverName": trip.carrier.driver.user.first_name + " " + trip.carrier.driver.user.last_name,
                                "trip_status": trip.status.title})
                    flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantTripDetails(request):
    try:
        data = request.data
        trip_id = data["trip_id"]
        trip = models.Trip.objects.get(id=trip_id)
        current_request = trip.request
        rsp = {"tripId": trip.id, "origin": current_request.origin,
               "loadingDate": current_request.loading_date,
               "destination": current_request.destination,
               "unloadingDate": current_request.unloading_date,
               "loadType": current_request.load_type.title,
               "weight": current_request.weight,
               "proposedPrice": current_request.proposed_price,
               "carrierClass": trip.carrier.classification.title,
               "carrierModel": trip.carrier.model,
               "carrierTag": trip.carrier.tag,
               "driverPhone": trip.carrier.driver.user.phone,
               "driverName": trip.carrier.driver.user.first_name + " " + trip.carrier.driver.user.last_name,
               "tripStatus": trip.status.title}
        return Response({"rsp": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# APPLICANT DASHBOARD SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantFinishedTripList(request):
    try:
        current_applicant = models.Applicant.objects.get(user=request.user)
        rsp = []
        flag = False
        requests = models.Request.objects.filter(applicant=current_applicant)
        for current_request in requests:
            if models.Trip.objects.filter(request=current_request):
                trip = models.Trip.objects.get(request=current_request)
                unloadedStatus = models.TripStatus.objects.get(title="تخلیه شده")
                if trip.status == unloadedStatus:
                    rsp.append({"trip_id": trip.id,
                                "origin": trip.request.origin,
                                "loading_date": trip.request.loading_date,
                                "destination": trip.request.destination,
                                "unloading_date": trip.request.unloading_date,
                                "load_type": trip.request.load_type.title,
                                "weight": trip.request.weight,
                                "carrier_class": trip.carrier.classification.title,
                                "carrier_model": trip.carrier.model,
                                "carrier_tag": trip.carrier.tag,
                                "driverPhone": trip.carrier.driver.user.phone,
                                "driverName": trip.carrier.driver.user.first_name + " " + trip.carrier.driver.user.last_name,
                                "trip_status": trip.status.title})

                    flag = True
        return Response({"list": rsp, "flag": flag}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CHAT SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def chatDriver(request):
    data = request.data
    try:
        sender = request.user
        if models.Request.objects.filter(id=data["request_id"]):
            request = models.Request.objects.get(id=data["request_id"])
            applicant = request.applicant
            receiver = applicant.user
            content = data["content"]
            new_message = models.Message.objects.create(sender=sender, receiver=receiver, request=request,
                                                        content=content)
            new_message.save()
            return Response({"message": "sent!"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid Request!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CHAT SERVICE
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApplicant])
def chatApplicant(request):
    data = request.data
    try:
        sender = request.user
        applicant = models.Applicant.objects.get(user=sender)
        if models.Request.objects.filter(id=data["request_id"], applicant=applicant):
            request = models.Request.objects.get(id=data["request_id"])
            receiver = models.MyUser.objects.get(username=data["receiver_username"])
            content = data["content"]
            new_message = models.Message.objects.create(sender=sender, receiver=receiver, request=request,
                                                        content=content)
            new_message.save()
            return Response({"message": "sent!"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid Request!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CHAT SERVICE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation(request):
    data = request.data
    try:
        rsp = list([])
        interlocutor = models.MyUser.objects.get(username=data["interlocutor_username"])
        current_user = request.user
        for message in models.Message.objects.filter(request=data["request_id"], sender=interlocutor,
                                                     receiver=current_user) | models.Message.objects.filter(
            request=data["request_id"], sender=current_user, receiver=interlocutor):
            rsp.append({message.sender.username: message.content})
            if message.sender == current_user:
                message.is_read = True
                message.save()
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CHAT SERVICE
@csrf_exempt
def streamChat(request):
    if not request.body:
        return JsonResponse(status=200, data={'message': 'No request body'})
    body = json.loads(bytes(request.body).decode('utf-8'))

    if 'username' not in body:
        return JsonResponse(status=400, data={'message': 'Username is required to join the channel'})

    username = body['username']
    client = StreamChat(api_key=settings.STREAM_API_KEY,
                        api_secret=settings.STREAM_API_SECRET)
    channel = client.channel('messaging', 'General')
    try:
        member = models.Member.objects.get(username=username)
        token = bytes(client.create_token(user_id=member.username), encoding='utf-8').decode('utf-8')
        return JsonResponse(status=200,
                            data={"username": member.username, "token": token, "apiKey": settings.STREAM_API_KEY})

    except Exception as e:
        member = models.Member(username=username)
        member.save()
        token = bytes(client.create_token(user_id=username), encoding='utf-8').decode('utf-8')
        client.update_user({"id": username, "role": "admin"})
        channel.add_members([username])

        return JsonResponse(status=200,
                            data={"username": member.username, "token": token, "apiKey": settings.STREAM_API_KEY})
