from django.db.models import Sum
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, redirect
from .models import Article, FederalWanted, LocalCriminals, Panishment, PunishmentType
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
    panishments = Panishment.objects.all().order_by('-panishment_num')
    
    # Получаем все параметры фильтрации
    cs_filter = request.GET.get('cs')
    person_id_filter = request.GET.get('person_id')
    fio_filter = request.GET.get('fio')
    article_num_filter = request.GET.get('article_num')  # Новый параметр

    # Применяем фильтры
    if cs_filter:
        panishments = panishments.filter(cs__cs=cs_filter)
    if person_id_filter:
        panishments = panishments.filter(person_id=person_id_filter)
    if fio_filter:
        panishments = panishments.filter(fio__icontains=fio_filter)
    if article_num_filter:  # Новый фильтр
        panishments = panishments.filter(article_num=article_num_filter)

    return render(request, "testdb/archive_panishment.html", {
        "panishments": panishments,
    })

def reports_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    article_num = request.GET.get('article_num')
    action = request.GET.get('action')

    start_date = None
    end_date = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    context = {
        'start_date': start_date_str,
        'end_date': end_date_str,
        'article_num': article_num,
        'report_type': None,
        'report_data': None,
    }

    if action == 'caught':
        queryset = LocalCriminals.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(arrest_time__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(arrest_time__gte=start_date)
        elif end_date:
            queryset = queryset.filter(arrest_time__lte=end_date)
        if article_num:
            queryset = queryset.filter(article_num=article_num)
        context['report_data'] = queryset
        context['report_type'] = 'caught'

    elif action == 'release':
        release_data = []
        person_ids = Panishment.objects.filter(
            punishment_type=PunishmentType.ARREST
        ).values_list('person_id', flat=True).distinct()

        for person_id in person_ids:
            if article_num:
                if not Panishment.objects.filter(
                    person_id=person_id,
                    article_num=article_num,
                    punishment_type=PunishmentType.ARREST
                ).exists():
                    continue

            cs_list = LocalCriminals.objects.filter(person_id=person_id).order_by('arrest_time')
            if not cs_list.exists():
                continue

            current_end = None
            total_arrest_days = 0

            for cs in cs_list:
                arrest_days = Panishment.objects.filter(
                    cs=cs,
                    punishment_type=PunishmentType.ARREST
                ).aggregate(total=Sum('numerical_value'))['total'] or 0

                total_arrest_days += arrest_days

                if current_end is None:
                    current_end = cs.arrest_time + timedelta(days=arrest_days)
                else:
                    if cs.arrest_time < current_end:
                        overlap = (current_end - cs.arrest_time).days
                        arrest_days += overlap
                    current_end = cs.arrest_time + timedelta(days=arrest_days)

            if total_arrest_days <= 0:
                continue

            if start_date and current_end < start_date:
                continue
            if end_date and current_end > end_date:
                continue

            last_cs = cs_list.last()
            release_data.append({
                'person_id': person_id,
                'fio': last_cs.fio,
                'article_num': last_cs.article_num,
                'arrest_time': last_cs.arrest_time,
                'release_date': current_end,
            })

        context['report_data'] = release_data
        context['report_type'] = 'release'

    elif action == 'stats':
        stats_data = []
        articles = Article.objects.all()
        if article_num:
            articles = articles.filter(article_num=article_num)

        for article in articles:
            panishments = Panishment.objects.filter(article_num=article.article_num)
            if start_date and end_date:
                panishments = panishments.filter(cs__arrest_time__range=[start_date, end_date])
            elif start_date:
                panishments = panishments.filter(cs__arrest_time__gte=start_date)
            elif end_date:
                panishments = panishments.filter(cs__arrest_time__lte=end_date)

            stats_data.append({
                'article_num': article.article_num,
                'count': panishments.count(),
            })

        context['report_data'] = stats_data
        context['report_type'] = 'stats'

    return render(request, 'testdb/reports.html', context)