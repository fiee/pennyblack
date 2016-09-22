from django.shortcuts import render


def unsubscribe(request, person, group_object=None):
    """
    Unsubscribe view
    """
    context = {
        'person': person,
        'group_object': group_object,
    }
    if request.GET.get('unsubscribe', False):
        person.unsubscribe()
        context.update({'done': True})
    return render(
        request,
        'pennyblack/subscriber/unsubscribe.html',
        context)
