import functools
import operator

from django.db.models import Q
from django.utils.translation import ugettext
from django_filters import CharFilter, ChoiceFilter


class AnyChoiceFilter(ChoiceFilter):

    def __init__(self, *args, **kwargs):
        empty_label = kwargs.pop('empty_label', ugettext('Any choice'))
        super(AnyChoiceFilter, self).__init__(*args, **kwargs)
        self.extra['choices'] = [('', empty_label)] + list(self.extra['choices'])


class MultiFieldFilter(CharFilter):
    """
    This filter performs an OR query on the defined fields from a
    single entered value.

    The following will work similar to the default UserAdmin search::

        class UserFilterSet(FilterSet):
            search = MultiFieldFilter([
                'username', 'first_name', 'last_name', 'email'])

            class Meta:
                model = User
                fields = ['search']

    Based on https://gist.github.com/nkryptic/4727865
    """

    def __init__(self, fields, *args, **kwargs):
        super(MultiFieldFilter, self).__init__(*args, **kwargs)
        self.fields = fields
        self.lookup_type = 'icontains'
        self.lookup_types = [
            ('^', 'istartswith'),
            ('=', 'iexact'),
            ('@', 'search'),
        ]

    def filter(self, qs, value):
        if not self.fields or not value:
            return qs

        lookups = [self._get_lookup(str(field)) for field in self.fields]
        queries = [Q(**{lookup: value}) for lookup in lookups]
        qs = qs.filter(functools.reduce(operator.or_, queries))
        return qs

    def _get_lookup(self, field_name):
        for key, lookup_type in self.lookup_types:
            if field_name.startswith(key):
                return '{0}__{1}'.format(field_name[len(key):], lookup_type)
        return '{0}__{1}'.format(field_name, self.lookup_type)
