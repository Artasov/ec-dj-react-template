from polymorphic.models import PolymorphicModel


class PolymorphicModelMixin(PolymorphicModel):
    class Meta:
        abstract = True
