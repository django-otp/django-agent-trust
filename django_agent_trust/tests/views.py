from django.http import HttpResponse
from django.views.generic.base import View
from django.utils.decorators import method_decorator

from django_agent_trust import trust_current_agent, revoke_current_agent, revoke_other_agents
from django_agent_trust.decorators import trusted_agent_required


class RestrictedView(View):
    @method_decorator(trusted_agent_required)
    def get(self, request):
        return HttpResponse()


class TrustView(View):
    def post(self, request):
        trust_current_agent(request)

        return HttpResponse()


class RevokeView(View):
    def post(self, request):
        revoke_current_agent(request)

        return HttpResponse()


class RevokeOthersView(View):
    def post(self, request):
        revoke_other_agents(request)

        return HttpResponse()
