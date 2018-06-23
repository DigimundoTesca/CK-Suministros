from users.models import User
from .models import Worker, BranchOffice


def branch_offices_processor(request):
    try:
        user = request.user
        branch_office = Worker.objects.values('branch_office').get(worker=user.id)
        if branch_office:
            branch_office_id = branch_office['branch_office']
            branch_office = BranchOffice.objects.get(id=branch_office_id)
            return {'g_branch_office': branch_office}

    except Exception as ex:
        return {'g_branch_office': '1'}
