from syn import do_it_all
from django.http import HttpResponse
from json import dumps

def home(request):
    p = request.POST
    if "s" in p:
        res = do_it_all(p["s"])
        return HttpResponse(res)
    else:
        return HttpResponse(status=404)