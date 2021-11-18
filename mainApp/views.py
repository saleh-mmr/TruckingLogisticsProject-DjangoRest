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


@api_view(['POST'])
@permission_classes(())
def signUp(request):
    try:
        data = request.data
        data_first_name = data['firstname']
        data_last_name = data['lastname']
        data_username = data['username']
        data_phone_number = data['pnumber']
        data_type = data['type']
        data_password = data['password']
        data_confirm_password = data['cpassword']
        if data_confirm_password == data_password:
            newUser = models.MyUser.objects.create(first_name=data_first_name, last_name=data_last_name,
                                                   username=data_username, phone=data_phone_number,
                                                   type=data_type)
            newUser.set_password(data_password)
            newUser.save()
            if newUser.type:
                newDriver = models.Driver.objects.create(user=newUser)
            else:
                newApplicant = models.Applicant.objects.create(user=newUser)
            if newUser:
                return Response({"message": "Created Successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Something might be Wrong!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "Something might be Wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes(())
def signIn(request):
    try:
        params = request.data
        user = authenticate(username=params['user'], password=params['pass'], )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            is_expired, token = token_expire_handler(token)
            tmp_response = {
                'access': token.key,
                'userid': token.user_id
            }
            return Response(tmp_response, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong username or password"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signOut(request):
    try:
        django_logout(request)
        Token.objects.filter(key=request.headers.get('Authorization')[7:]).delete()
        return Response({"message": "Logout Successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs in logout!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApplicant])
def newRequest(request):
    try:
        data = request.data
        current_user = request.user
        current_applicant = models.Applicant.objects.get(user=current_user)
        origin = data["origin"]
        loading_date = data["loading_date"]
        destination = data["destination"]
        unloading_date = data["unloading_date"]
        weight = data["weight"]
        value = data["value"]
        description = data["description"]
        proposed_price = data["proposed_price"]
        receiver_name = data["receiver_name"]
        receiver_phone = data["receiver_phone"]
        truck_classification_requirement = data["truck_classification_requirement"]
        load_type = models.LoadType.objects.get(title=data["load_type"])
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
                return Response({"message": "New Truck added Successfully!"}, status=status.HTTP_200_OK)
            return Response({"message": "Classification is not valid!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "This tag is already added!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def showRequestList(request):
    try:
        current_user = request.user
        current_driver = models.Driver.objects.get(user=current_user)
        carriers = models.Carrier.objects.filter(driver=current_driver)
        rsp = set({})
        for carrier in carriers:
            if models.RequiredClass.objects.filter(classification=carrier.classification):
                for i in models.RequiredClass.objects.filter(classification=carrier.classification):
                    if not models.Trip.objects.filter(request=i.request):
                        rsp.add(i.request.id)
        return Response({"request list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                            new_status = models.Status.objects.get(title='new')
                            models.Trip.objects.create(request=current_request, carrier=carrier, status=new_status)
                            current_driver.canAccept = False
                            current_driver.save()
                            return Response({"message": "OK!"}, status=status.HTTP_200_OK)
                    return Response({"message": "You dont have required truck!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                return Response({"message": "This request has an active trip!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"message": "You have an active trip!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "This is not a valid request!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def loadAnnouncement(request):
    try:
        data = request.data
        current_trip = models.Trip.objects.get(id=data["trip_id"])
        current_driver = models.Driver.objects.get(user=request.user)
        if current_trip.carrier.driver == current_driver:
            loaded_status = models.Status.objects.get(title='loaded')
            current_trip.status = loaded_status
            current_trip.save()
            return Response({"message": "OK!"}, status=status.HTTP_200_OK)
        return Response({"message": "Just The owner of the trip can edit status!"},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDriver])
def unloadAnnouncement(request):
    try:
        data = request.data
        current_trip = models.Trip.objects.get(id=data["trip_id"])
        current_driver = models.Driver.objects.get(user=request.user)
        if current_trip.carrier.driver == current_driver:
            unloaded_status = models.Status.objects.get(title='unloaded')
            current_trip.status = unloaded_status
            current_trip.save()
            return Response({"message": "OK!"}, status=status.HTTP_200_OK)
        return Response({"message": "Just The owner of the trip can edit status!"},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantRequestList(request):
    try:
        current_applicant = models.Driver.objects.get(user=request.user)
        rsp = {}
        requests = models.Request.objects.filter(applicant=current_applicant)
        for request in requests:
            if not models.Trip.objects.filter(request=request):
                rsp.update({"req_id": request.id,
                            "origin": request.origin,
                            "loading_date": request.loading_date,
                            "destination": request.destination,
                            "unloading_date": request.unloading_date,
                            "load_type": request.load_type,
                            "weight": request.weight})
        return Response({"list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApplicant])
def showApplicantTripList(request):
    try:
        current_applicant = models.Driver.objects.get(user=request.user)
        rsp = {}
        requests = models.Request.objects.filter(applicant=current_applicant)
        for request in requests:
            if models.Trip.objects.filter(request=request):
                trip = models.Trip.objects.get(request=request)
                rsp.update({"trip_id": trip.id,
                            "origin": request.origin,
                            "loading_date": request.loading_date,
                            "destination": request.destination,
                            "unloading_date": request.unloading_date,
                            "load_type": request.load_type,
                            "weight": request.weight,
                            "carrier_class": trip.carrier.classification,
                            "carrier_model": trip.carrier.model,
                            "carrier_tag": trip.carrier.tag,
                            "driver_username": trip.carrier.driver.user.username,
                            "trip_status": trip.status.title})
        return Response({"list": rsp}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
