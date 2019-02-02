from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import json
from ina_api.models import *
from django.views.decorators.http import require_http_methods
from django.core import serializers


@require_http_methods(['POST'])
def getMember(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        try:
            userObject = User.objects.get(pk=data['userId'])
        except:
            return JsonResponse({"bool": False, "msg": "Gebruiker met id [" + str(data['userId']) + "] bestaat niet"}, safe=True)
        try:
            projectObject = Project.objects.get(pk=data['projectId'])
        except:
            return JsonResponse({"bool": False, "msg": "Groep met id [" + str(data['projectId']) + "] bestaat niet"}, safe=True)
        memberObject = Member.objects.get(user=userObject, project=projectObject)
        userObject = memberObject.user.__repr__()
        projectObject = memberObject.project.__repr__()
        memberJson = serializers.serialize('json', [ memberObject, ])
        return JsonResponse({"bool": True, "msg": "Deelnemer bestaat", "member": memberJson, "user": userObject, "project": projectObject}, safe=True)
    except ObjectDoesNotExist:
        return JsonResponse({"bool": False, "msg": "Deelnemer bestaat niet"}, safe=True)


@require_http_methods(['GET'])
def getMemberById(request, id):
    try:
        memberObject = Member.objects.get(pk=id)
        userObject = memberObject.user.__repr__()
        projectObject = memberObject.project.__repr__()
        memberJson = serializers.serialize('json', [ memberObject, ])
        return JsonResponse({"bool": True, "msg": "Deelnemer bestaat", "member": memberJson, "user": userObject, "project": projectObject}, safe=True)
    except ObjectDoesNotExist:
        return JsonResponse({"bool": False, "msg": "Deelnemer bestaat niet"}, safe=True)


@require_http_methods(['GET'])
def getMembersByProjectId(request, project_id):
    memberList = []
    try:
        memberObjects = Member.objects.filter(project=project_id).all()
        for member in memberObjects:
            userObject = member.user.__repr__()
            memberList.append({
                'id': userObject['id'],
                'firstName': userObject['firstName'],
                'lastName': userObject['lastName'],
                'bio': userObject['bio'],
                'organisation': userObject['organisation'],
                'profilePhotoPath': userObject['profilePhotoPath'],
            })
        return JsonResponse({"bool": True, "msg": "Members found for project", "members": memberList}, safe=True)
    except ObjectDoesNotExist:
        return JsonResponse({"bool": False, "msg": "There are no members for this project"}, safe=True)

@require_http_methods(['GET'])
def getMembersByUserId(request, user_id):
    try:
        userObject = User.objects.get(pk=user_id)
        memberList = Member.objects.filter(user=userObject).all()
        projectsMembered = []
        if (memberList):
            for entry in memberList:
                projectObject = entry.project.__repr__()
                projectsMembered.append(projectObject)
            return JsonResponse({"bool": True, "found": True, "msg": "Deelnemende projecten gevonden", "projects": projectsMembered})
        else:
            return JsonResponse({"bool": True, "found": True, "msg": "Je neemt niet deel aan projecten"})
    except:
        return JsonResponse({"bool": False, "found": False, "msg": "Kon geen deelnemende projecten ophalen"})


@require_http_methods(['POST'])
def createMember(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        try:
            userObject = User.objects.get(pk=data['userId'])
        except:
            return JsonResponse({"bool": False, "msg": "Gebruiker met id [" + str(data['userId']) + "] bestaat niet"}, safe=True)
        try:
            projectObject = Project.objects.get(pk=data['projectId'])
        except:
            return JsonResponse({"bool": False, "msg": "Project met id [" + str(data['projectId']) + "] bestaat niet"}, safe=True)
        try:
            if not Member.objects.filter(user=userObject, project=projectObject).exists():
                memberObject = Member(user=userObject, project=projectObject)
                memberObject.save()
                return JsonResponse({"bool": True, "msg": "Deelnemer aangemaakt", "id": memberObject.pk}, safe=True)
            else:
                return JsonResponse({"bool": False, "msg": "Deelnemer bestaat al"}, safe=True)
        except:
            return JsonResponse({"bool": False, "msg": "Kon deelnemer niet aanmaken"}, safe=True)
    except:
        return JsonResponse({"bool": False, "msg": "Stuur alle verplichte velden mee aub"}, safe=True)


@require_http_methods(['DELETE'])
def deleteMember(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        memberObject = Member.objects.filter(user=data['userId'], project=data['projectId']).first()
        try:
            memberObject.delete()
            return JsonResponse({"bool": True, "msg": "Deelnemer verwijderd"}, safe=True)
        except:
            return JsonResponse({"bool": False, "msg": "Kon deelnemer niet verwijderen"}, safe=True)
    except:
        return JsonResponse({"bool": False, "msg": "Deelnemer met id [" + str(data['userId']) + "] bestaat niet"}, safe=True)
