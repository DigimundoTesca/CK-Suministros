from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BranchOffice


# -------------------------------------  Branch offices -------------------------------------
@login_required(login_url='users:login')
def branch_offices(request):
    if request.POST:
        branch_offices_data = BranchOffice.objects.all()
        branch_offices_array = []

        for branch in branch_offices_data:
            branch_offices_array.append({
                'id': branch.id,
                'abbrev': branch.abbreviated_name,
            })

        return JsonResponse({
            'data': {
                'branch_offices': branch_offices_array
            }
        })
