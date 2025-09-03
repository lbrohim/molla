from datetime import timedelta

from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from apps.blogs.models import BlogModel, BlogCategoryModel, BlogTagModel, BlogViewModel


def blogs_list_view(request):
    blogs = BlogModel.objects.filter(
        status=BlogModel.BlogStatus.PUBLISHED
    )
    categories = BlogCategoryModel.objects.all()
    tags = BlogTagModel.objects.all()
    most_popular_blogs = (
        BlogModel.objects
        .annotate(views_count=Count('views', distinct=True))
        .order_by('-views_count')[:4]
    )

    context = {
        "blogs": blogs,
        "categories": categories,
        "tags": tags,
        "most_popular_blogs": most_popular_blogs,
    }
    return render(
        request, 'blogs/blog-list.html',
        context
    )


def check_blog_view(request, blog):
    # Get user IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        user_ip = x_forwarded_for.split(',')[0]
    else:
        user_ip = request.META.get('REMOTE_ADDR')

    # Find last view of this blog by this IP
    last_view = BlogViewModel.objects.filter(
        user_ip=user_ip, blog=blog
    ).order_by('-created_at').first()

    # If never viewed OR last view was more than 7 days ago → create new record
    if not last_view or (timezone.now() - last_view.created_at) > timedelta(minutes=1):
        BlogViewModel.objects.create(user_ip=user_ip, blog=blog)


def blog_detail_view(request, pk):
    try:
        blog = BlogModel.objects.get(id=pk)
    except BlogModel.DoesNotExist:
        return render(request, 'pages/404.html')

    # update view count of blog
    check_blog_view(request, blog)

    categories = BlogCategoryModel.objects.all()
    tags = BlogTagModel.objects.all()
    related_blogs = BlogModel.objects.filter(
        category__in=blog.category.all()
    ).exclude(id=blog.id).distinct()
    most_popular_blogs = (
        BlogModel.objects
        .annotate(views_count=Count('views', distinct=True))
        .order_by('-views_count')[:4]
    )

    context = {
        "blog": blog,
        "categories": categories,
        "tags": tags,
        "related_blogs": related_blogs,
        "most_popular_blogs": most_popular_blogs,
    }
    return render(
        request, 'blogs/blog-detail.html',
        context
    )
