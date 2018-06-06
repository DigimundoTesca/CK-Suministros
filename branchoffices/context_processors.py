from .models import Worker, BranchOffice


def branch_offices_processor(request):
    user = request.user
    branch_office_id = Worker.objects.values('branch_office').get(worker=user.id)['branch_office']
    branch_office = BranchOffice.objects.get(id=branch_office_id)
    return {'g_branch_office': branch_office}
