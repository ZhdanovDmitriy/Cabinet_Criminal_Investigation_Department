from django.db import models

class PunishmentType(models.TextChoices):
    FINE = 'Fine', 'Штраф'
    ARREST = 'Arrest', 'Арест'
    COMMUNITY_SERVICE = 'Community Service', 'Общественные работы'
    DEATH = 'Death', 'Смертная казнь'

class Article(models.Model):
    article_num = models.IntegerField(verbose_name="Номер статьи")
    article_text = models.TextField(verbose_name="Текст статьи")
    punishment_type = models.CharField(
        max_length=20,
        choices=PunishmentType.choices,
        verbose_name="Тип наказания"
    )
    numerical_value = models.IntegerField(verbose_name="Числовое значение")
    punishment_type_relapse = models.CharField(
        max_length=20,
        choices=PunishmentType.choices,
        verbose_name="Тип наказания при рецидиве"
    )
    numerical_value_relapse = models.IntegerField(verbose_name="Числовое значение при рецидиве")

    def __str__(self):
        return f"Статья {self.article_num}: {self.article_text[:50]}..."

class FederalWanted(models.Model):
    fi = models.AutoField(primary_key=True) 
    person_id = models.IntegerField(verbose_name="ID человека")
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    article_num = models.IntegerField(verbose_name="Номер статьи")

    def __str__(self):
        return f"{self.fio} (ID: {self.person_id}, FI: {self.fi}, Статья: {self.article_num})"

class LocalCriminals(models.Model):
    cs = models.AutoField(primary_key=True)
    article_num = models.IntegerField(verbose_name="Номер статьи")
    person_id = models.IntegerField(verbose_name="ID человека")
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    arrest_time = models.DateField(verbose_name="Дата ареста")
    final_panishment = models.TextField(blank=True, verbose_name="Окончательное наказание")

    def __str__(self):
        return f"{self.fio} (ID: {self.person_id})"
 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Перенос федеральных записей
        federal_records = FederalWanted.objects.filter(person_id=self.person_id)
        for record in federal_records:
            try:
                federal_article = Article.objects.get(article_num=record.article_num)
                has_previous = (
                    Panishment.objects.filter(person_id=record.person_id).exists()
                )
                Panishment.objects.create(
                    cs=self,
                    person_id=record.person_id,
                    fio=record.fio,
                    article_num=record.article_num,
                    punishment_type=federal_article.punishment_type_relapse if has_previous else federal_article.punishment_type,
                    numerical_value=federal_article.numerical_value_relapse if has_previous else federal_article.numerical_value,
                    fi_flag=1
                )
            except Article.DoesNotExist:
                continue
        federal_records.delete()

        # Обработка локального наказания
        try:
            article = Article.objects.get(article_num=self.article_num)
            has_previous = (
                Panishment.objects.filter(person_id=self.person_id).exists()
                or FederalWanted.objects.filter(person_id=self.person_id).exists()
            )
            Panishment.objects.create(
                cs=self,
                person_id=self.person_id,
                fio=self.fio,
                article_num=self.article_num,
                punishment_type=article.punishment_type_relapse if has_previous else article.punishment_type,
                numerical_value=article.numerical_value_relapse if has_previous else article.numerical_value,
                fi_flag=0
            )
        except Article.DoesNotExist:
            pass

        # Формирование final_panishment
        panishments = Panishment.objects.filter(cs=self)
        
        total_fine = 0
        total_arrest = 0
        other_punishments = []
        has_death = False
        
        for p in panishments:
            punishment_name = p.get_punishment_type_display()
            value = p.numerical_value
            
            if p.punishment_type == PunishmentType.DEATH:
                has_death = True
            elif p.punishment_type == PunishmentType.FINE:
                total_fine += value
            elif p.punishment_type == PunishmentType.ARREST:
                total_arrest += value
            else:
                other_punishments.append(f"{punishment_name} {value}")
        
        if has_death:
            self.final_panishment = "Смертная казнь"
        else:
            parts = []
            if total_fine > 0:
                parts.append(f"Штраф {total_fine}")
            if total_arrest > 0:
                parts.append(f"Арест {total_arrest}")
            parts.extend(other_punishments)
            
            self.final_panishment = ", ".join(parts) if parts else "Нет наказания"

        super(LocalCriminals, self).save(update_fields=['final_panishment'])


class Panishment(models.Model):
    panishment_num = models.AutoField(primary_key=True)
    cs = models.ForeignKey(LocalCriminals, on_delete=models.CASCADE, verbose_name="Номер дела")
    person_id = models.IntegerField(verbose_name="ID человека")
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    article_num = models.IntegerField(verbose_name="Номер статьи")
    punishment_type = models.CharField(
        max_length=20,
        choices=PunishmentType.choices,
        verbose_name="Тип наказания"
    )
    numerical_value = models.IntegerField(verbose_name="Числовое значение")
    fi_flag = models.IntegerField(choices=[(0, "Локальное"), (1, "Федеральное")], verbose_name="Статус дела")

    def __str__(self):
        return f"Дело {self.cs.cs} - {self.fio} (Статья {self.article_num})"
