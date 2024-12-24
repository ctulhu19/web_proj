from django.shortcuts import render, get_object_or_404, redirect
from .models import Publication, Category, User, Edition, Author, Tags
from django.utils import timezone
from django.core.paginator import Paginator
from django.views import View
from publications.forms import UserEditForm, PublicationForm, EditionForm, CategoryForm, ApplicationForm, TagsForm
from django.views.generic.edit import ModelFormMixin, FormView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

# Create your views here.
PAGE_NUM = 10





def index(request):
    dt_now = timezone.now()
    editions = Edition.objects.filter(
        pub_date__lte=dt_now,
        is_published=True,
        category__is_published=True
    )
    paginator = Paginator(editions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'publications/index.html', {'page_obj': page_obj})


def edition_detail(request, category_slug, edition_slug):
    dt_now = timezone.now()
    if request.user.is_superuser:
        category = get_object_or_404(
            Category,
            slug=category_slug,
        )
        edition = get_object_or_404(
            Edition,
            slug=edition_slug,
            category=category,
        )
        publications = Publication.objects.filter(
            edition=edition,
        )
    else:
        category = get_object_or_404(
            Category,
            pub_date__lte=dt_now,
            slug=category_slug,
        )
        edition = get_object_or_404(
            Edition,
            pub_date__lte=dt_now,
            slug=edition_slug,
            category=category,
        )
        publications = Publication.objects.filter(
            pub_date__lte=dt_now,
            edition=edition,
            is_published=True,
            application=False
        )
    paginator = Paginator(publications, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category,
        'edition': edition,
    }
    return render(request, 'publications/edition.html', context)


def category_list(request):
    dt_now = timezone.now()
    if request.user.is_superuser:
        category = Category.objects.filter(
            pub_date__lte=dt_now,
        )
    else:
        category = Category.objects.all()
    paginator = Paginator(category, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'publications/categories_list.html', context)


def category_detail(request, category_slug):
    dt_now = timezone.now()
    if request.user.is_superuser:
        category = get_object_or_404(
            Category,
            slug=category_slug,
        )
        edition = Edition.objects.filter(
            category=category,
        )
    else:
        category = get_object_or_404(
            Category,
            pub_date__lte=dt_now,
            slug=category_slug,
        )
        edition = Edition.objects.filter(
            pub_date__lte=dt_now,
            category=category,
        )
    paginator = Paginator(edition, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category,
    }
    return render(request, 'publications/category_detail.html', context)


def publication_detail(request, category_slug, edition_slug, post_id):
    dt_now = timezone.now()
    if request.user.is_superuser:
        category = get_object_or_404(
            Category,
            slug=category_slug,
        )
        edition = get_object_or_404(
            Edition,
            slug=edition_slug,
            category=category,
        )
        publication = get_object_or_404(
            Publication,
            edition=edition,
            pk=post_id,
        )
    else:
        category = get_object_or_404(
            Category,
            pub_date__lte=dt_now,
            slug=category_slug,
        )
        edition = get_object_or_404(
            Edition,
            pub_date__lte=dt_now,
            slug=edition_slug,
            category=category,
        )
        publication = get_object_or_404(
            Publication,
            edition=edition,
            pk=post_id,
        )
        user = User.objects.get(pk=request.user.pk)
        if  Author.objects.get(user=user) not in publication.authors.all():
            publication = publication.filter(
                pub_date__lte=dt_now,
                application=False,
            )
    context = {
        'publication': publication,
        'category': category,
        'edition': edition,
    }
    return render(request, 'publications/detail.html', context)


@login_required
def article_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.is_published = False
            obj.application = True
            obj.pub_date = obj.edition.pub_date
            obj.save()
            obj.authors.set(form.cleaned_data["authors"])
        return redirect('publications:index')
    else:
        form = ApplicationForm()
    context = {
        'form': form
    }
    return render(request, 'publications/create_edit.html', context)

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.user.pk)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            author = get_object_or_404(Author, user=user)
            author.affiliation = form.cleaned_data["affiliation"]
            user.save()
            author.save()
        context = {
            "form": form
        }
        return render(request, 'publications/user.html', context)
    form = UserEditForm(instance=request.user)
    context = {
        "form": form
    }
    return render(request, 'publications/user.html', context)


class Profile(View):
    template = 'publications/profile.html'

    def get(self, request, **kwargs):
        username = kwargs['username']
        profile = get_object_or_404(User, username=username)
        author = Author.objects.get(user=profile)
        publications = Publication.objects.filter(authors=author)
        paginator = Paginator(publications, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        contex = {
            "profile": profile,
            'author': author,
            'page_obj': page_obj
        }
        return render(request, self.template, contex)


class PublicationFormView(ModelFormMixin, FormView):
    model = Publication
    form_class = PublicationForm
    template_name = "publications/create_edit.html"
    success_url = reverse_lazy("publications:index")

    def get(self, request, *args, **kwargs):
        if "publication_id" in self.kwargs:
            self.object = get_object_or_404(Publication, pk=self.kwargs["publication_id"])
        else:
            self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "publication_id" in self.kwargs:
            self.object = get_object_or_404(Publication, pk=self.kwargs["publication_id"])
        else:
            self.object = None
        return super().post(request, *args, **kwargs)


class CategoryFormView(ModelFormMixin, FormView):
    model = Category
    form_class = CategoryForm
    template_name = "publications/create_edit.html"
    success_url = reverse_lazy("publications:index")

    def get(self, request, *args, **kwargs):
        if "category_id" in self.kwargs:
            self.object = get_object_or_404(Category, pk=self.kwargs["category_id"])
        else:
            self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "category_id" in self.kwargs:
            self.object = get_object_or_404(Category, pk=self.kwargs["category_id"])
        else:
            self.object = None
        return super().post(request, *args, **kwargs)


class TagsCreate(ModelFormMixin, FormView):
    model = Tags
    form_class = TagsForm
    template_name = "publications/create_edit.html"
    success_url = reverse_lazy("publications:index")

    def get(self, request, *args, **kwargs):
        if "tags_id" in self.kwargs:
            self.object = get_object_or_404(Category, pk=self.kwargs["tag_id"])
        else:
            self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "tags_id" in self.kwargs:
            self.object = get_object_or_404(Category, pk=self.kwargs["tag_id"])
        else:
            self.object = None
        return super().post(request, *args, **kwargs)

class EditionFormView(ModelFormMixin, FormView):
    model = Edition
    form_class = EditionForm
    template_name = "publications/create_edit.html"
    success_url = reverse_lazy("publications:index")

    def get(self, request, *args, **kwargs):
        if "edition_id" in self.kwargs:
            self.object = get_object_or_404(Edition, pk=self.kwargs["edition_id"])
        else:
            self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "edition_id" in self.kwargs:
            self.object = get_object_or_404(Edition, pk=self.kwargs["edition_id"])
        else:
            self.object = None
        return super().post(request, *args, **kwargs)


def editionDowload(request, edition_id):
    edition = get_object_or_404(Edition, id=edition_id)
    response = HttpResponse(edition.edition_file, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{edition.title}.csv"'
    return response


def publicationsDownload(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    response = HttpResponse(publication.article, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{publication.title}.csv"'
    return response


def deleteCategroy(request, category_id):
    edition = get_object_or_404(Category, id=category_id).delete()
    return redirect('publications:index')


def deleteEdition(request, edition_id):
    edition = get_object_or_404(Edition, id=edition_id).delete()
    return redirect('publications:index')


def deletePublication(request, publication_id):
    edition = get_object_or_404(Publication, id=publication_id).delete()
    return redirect('publications:index')
