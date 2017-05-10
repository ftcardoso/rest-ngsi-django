from django.db.models import AutoField, ManyToManyField

def get_fields(obj, attributes=[]):
    fields = []
    for each in obj._meta.fields:
        if isinstance(each, AutoField):
            continue
        if not attributes:
            fields.append(each)
        elif each.name in attributes:
            fields.append(each)
    for each in obj._meta.many_to_many:
        if not isinstance(each, ManyToManyField):
            continue
        if not attributes:
            fields.append(each)
        elif each.name in attributes:
            fields.append(each)    
    return fields
