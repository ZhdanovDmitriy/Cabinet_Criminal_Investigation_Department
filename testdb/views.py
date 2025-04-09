from django.shortcuts import render, redirect, redirect
from .models import Article, FederalWanted, LocalCriminals, Panishment
from .forms import LocalCriminalsForm, PanishmentForm

def home(request):
    criminals = LocalCriminals.objects.all() 
    
    if request.method == "POST":
        form = LocalCriminalsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = LocalCriminalsForm()

    return render(request, "home.html", {"criminals": criminals, "form": form})


def article_list(request):
    if request.method == "POST":
        try:
            Article.objects.create(
                article_num=request.POST.get('article_num'),
                article_text=request.POST.get('article_text'),
                punishment_type=request.POST.get('punishment_type'),
                numerical_value=request.POST.get('numerical_value'),
                punishment_type_relapse=request.POST.get('punishment_type_relapse'),
                numerical_value_relapse=request.POST.get('numerical_value_relapse')
            )
            return redirect('article_list')  # Перенаправляем на GET-запрос после успешного добавления
        except Exception as e:
            return render(request, 'testdb/article_list.html', {
                'articles': Article.objects.all(),
                'error': f"Ошибка при добавлении: {str(e)}"
            })

    articles = Article.objects.all()
    return render(request, 'testdb/article_list.html', {'articles': articles})

def federal_wanted_list(request):
    if request.method == "POST":
        fio = request.POST.get("fio")
        person_id = request.POST.get("person_id")
        article_num = request.POST.get("article_num")

        if fio and person_id and article_num:
            try:
                FederalWanted.objects.create(
                    person_id=person_id,
                    fio=fio,
                    article_num=article_num
                )
                return redirect("federal_wanted_list")

            except Exception as e:
                return render(request, "testdb/federal_wanted_list.html", {
                    "wanted_list": FederalWanted.objects.all(),
                    "error": f"Ошибка при добавлении: {str(e)}"
                })
    
    return render(request, "testdb/federal_wanted_list.html", {"wanted_list": FederalWanted.objects.all()})

def delete_federal_wanted(request, fi):
    try:
        federal_wanted_entry = FederalWanted.objects.get(fi=fi)
        federal_wanted_entry.delete()
    except FederalWanted.DoesNotExist:
        pass
    return redirect('federal_wanted_list')

def local_criminals_list(request):
    criminals = LocalCriminals.objects.all()
    return render(request, "testdb/local_criminals_list.html", {"criminals": criminals})

def panishment_list(request):
    panishments = Panishment.objects.all().order_by('-id')
    return render(request, "testdb/panishment_list.html", {"panishments": panishments})

def add_local_criminal(request):
    if request.method == "POST":
        form = LocalCriminalsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("local_criminals_list")
    else:
        form = LocalCriminalsForm()
    return render(request, "testdb/add_local_criminal.html", {"form": form})

def add_panishment(request):
    if request.method == "POST":
        form = PanishmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("panishment_list")
    else:
        form = PanishmentForm()
    return render(request, "testdb/add_panishment.html", {"form": form})


def archive_panishment(request):
    panishments = Panishment.objects.all()
    return render(request, "testdb/archive_panishment.html", {"panishments": panishments})