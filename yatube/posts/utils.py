from django.core.paginator import Paginator

POST_COUNT = 10


def paginator(post_list, request):
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
