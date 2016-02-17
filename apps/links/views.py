from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView
from taggit.models import Tag

from .models import Link
from .forms import LinkForm


class LinkDetail(DetailView):
    model = Link


def clean_categories(provided_categories):
    cleaned_categories = []
    for cat in [cat.strip(' ,') for cat in provided_categories]:
        # Check first if there's anything left, and if there is,
        # determine if it's one of the checklisted items or from the
        # text box (indicated by comma-separation)
        if cat:
            if (type(cat.split(',') is list)):
                cleaned_categories.extend(
                    [new_cat.strip(' ,') for new_cat in cat.split(',')]
                )
            else:
                cleaned_categories.add(cat)
    return cleaned_categories


def LinkCreate(request):
    link_form = LinkForm(request.POST or None)
    all_existing_categories = Tag.objects.all()

    if request.method == "POST":
        if (link_form.is_valid()):
            new_link = Link(
                name=link_form.instance.name,
                description=link_form.instance.description,
                destination=link_form.instance.destination,
                owner=request.user,
                is_external=link_form.instance.is_external,
            )
            new_link.save()
            provided_categories = link_form.data.getlist('categories')
            cleaned_categories = clean_categories(provided_categories)

            new_link.categories.set(*cleaned_categories)

            new_link.save()

            return redirect('link-detail', pk=new_link.pk)
        else:
            return render(request, "link_form.html", {
                'form': link_form,
                'existing_categories': all_existing_categories
            })
    else:
        return render(request, "link_form.html", {
            'form': link_form,
            'existing_categories': all_existing_categories
        })


def LinkEdit(request, pk):
    link = Link.objects.get(pk=pk)
    link_form = LinkForm(request.POST or None, instance=link)

    all_existing_categories = Tag.objects.all()

    if request.method == "POST":
        if (link_form.is_valid()):
            link.name = link_form.instance.name
            link.description = link_form.instance.description
            link.destination = link_form.instance.destination
            link.owner = request.user
            link.save()
            provided_categories = link_form.data.getlist('categories')
            cleaned_categories = clean_categories(provided_categories)

            link.categories.set(*cleaned_categories)

            link.save()

            return redirect('link-detail', pk=link.pk)
        else:
            return render(request, "link_form.html", {
                'form': link_form,
                'existing_categories': all_existing_categories
            })
    else:
        return render(request, "link_form.html", {
            'form': link_form,
            'existing_categories': all_existing_categories
        })


class LinkList(ListView):
    model = Link
    paginate_by = 5
