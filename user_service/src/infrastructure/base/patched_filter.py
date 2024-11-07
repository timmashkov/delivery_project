from fastapi_filter.contrib.sqlalchemy import Filter


class PatchedFilter(Filter):
    def sort(self, query):
        for field_name, _ in self.filtering_fields:
            field_value = getattr(self, field_name)
            if isinstance(field_value, Filter):
                query = field_value.sort(query)
        return super().sort(query)

    @property
    def filtering_fields(self):
        fields = self.model_dump(exclude_none=True)
        fields.pop(self.Constants.ordering_field_name, None)
        return fields.items()
