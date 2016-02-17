from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, UpdateView
from taggit.models import Tag

from .models import Link
from .forms import LinkForm


class LinkDetail(DetailView):
    model = Link


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
            )
            new_link.save()
            provided_categories = link_form.data.getlist('categories')
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

            for cat in cleaned_categories:
                new_link.categories.add(cat)

            new_link.save()

            return redirect('link-detail', pk=new_link.pk)
    else:
        return render(request, "link_form.html", {
            'form': link_form,
            'existing_categories': all_existing_categories
        })


class LinkEdit(UpdateView):
    model = Link
    fields = ['name', 'description', 'destination', 'categories']

    def get_context_data(self, **kwargs):
        context = super(LinkEdit, self).get_context_data(**kwargs)
        return context


class LinkList(ListView):
    model = Link
    paginate_by = 5
