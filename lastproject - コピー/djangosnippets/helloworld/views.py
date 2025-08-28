from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from helloworld.models import Helloworld,Shop,Sighting,Comment
from helloworld.forms import SnippetForm,ShopForm,SightingForm

# Create your views here.
def top(request):
    all_snippets = Helloworld.objects.order_by('-created_at')

    query = request.GET.get('q')
    if query:
        filtered_snippets = all_snippets.filter(created_by__username__icontains=query)
    else:
        filtered_snippets = all_snippets


    shops = Shop.objects.all()

    paginator = Paginator(filtered_snippets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_count = all_snippets.count() + shops.count()
    context = {
        'all_snippets': all_snippets,
        'shops': shops,
        'total_count': total_count,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'snippets/top.html', context)


@login_required
def snippet_new(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            snippet.save()
            return redirect('snippet_detail', snippet_id=snippet.pk)
    else:
        form = SnippetForm()
    return render(request, 'snippets/snippet_new.html', {'form': form})

def snippet_detail(request, snippet_id):
    snippet = get_object_or_404(Helloworld, pk=snippet_id)
    sightings = snippet.sightings.all().order_by('-sighting_datetime')
    return render(request, 'snippets/snippet_detail.html', {
        'snippet': snippet,
        'sightings': sightings,
    })


@login_required
def shop_new(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.created_by = request.user
            shop.save()
            return redirect('top')
    else:
        form = ShopForm()
    return render(request, 'snippets/snippet_new_map.html', {'form': form})


@login_required
def snippet_edit(request, snippet_id):
    snippet = get_object_or_404(Helloworld, pk=snippet_id)
    if snippet.created_by_id != request.user.id:
        return HttpResponseForbidden('このスニペットの編集は許可されていません．')

    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = SnippetForm(instance=snippet)

    context = {'form': form, 'snippet': snippet}
    return render(request, 'snippets/snippet_edit.html', context)

@login_required
def sighting_new(request, snippet_id):
    snippet = get_object_or_404(Helloworld, pk=snippet_id)
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.theft_report = snippet
            sighting.created_by = request.user
            sighting.save()
            return redirect('snippet_detail', snippet_id=snippet.pk)
    else:
        form = SightingForm()
    return render(request, 'snippets/sighting_new.html', {
        'form': form,
        'snippet': snippet,
    })
def sighting_detail(request, pk):
    sighting = get_object_or_404(Sighting, pk=pk)
    comments = sighting.comments.all().order_by('-created_at')  # コメント一覧
    return render(request, 'snippets/sighting_detail.html', {
        'sighting': sighting,
        'comments': comments,
    })


@login_required
def toggle_resolved(request, snippet_id):
    if request.method == 'POST':
        snippet = get_object_or_404(Helloworld, pk=snippet_id)
        if snippet.created_by == request.user:
            snippet.is_resolved = not snippet.is_resolved
            snippet.save()
    return redirect('snippet_detail', snippet_id=snippet_id)

@login_required
def add_comment(request, pk):
    sighting = get_object_or_404(Sighting, pk=pk)
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Comment.objects.create(
                sighting=sighting,
                user=request.user,
                content=content
            )
    return redirect("sighting_detail", pk=pk)  # 詳細ページにリダイレクト


