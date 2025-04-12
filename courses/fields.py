from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # filter by objects with the same field values
                    # for the fields in "for_fields"
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                # get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)


class AutoSlugField(models.SlugField):
    def __init__(self, *args, populate_from=None, **kwargs):
        self.populate_from = populate_from
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.populate_from)
        slug = slugify(value)
        setattr(model_instance, self.attname, slug)
        return slug
