from asgiref.sync import sync_to_async
from rest_framework.serializers import ModelSerializer as DRFModelSerializer, ListSerializer


class AListSerializer(ListSerializer):
    @property
    async def adata(self):
        items_data = []
        for item in self.instance:
            serializer = self.child.__class__(item, context=self.context)
            data = await serializer.adata
            items_data.append(data)
        return items_data


class ASerializer(DRFModelSerializer):
    async def asave(self, **kwargs):
        return await sync_to_async(self.save)(**kwargs)

    async def ais_valid(self, **kwargs):
        return await sync_to_async(self.is_valid)(**kwargs)

    @property
    async def adata(self):
        return await sync_to_async(lambda: self.data)()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return AListSerializer(*args, **kwargs)


class AModelSerializer(DRFModelSerializer):
    async def asave(self, **kwargs):
        return await sync_to_async(self.save)(**kwargs)

    async def ais_valid(self, **kwargs):
        return await sync_to_async(self.is_valid)(**kwargs)

    @property
    async def adata(self):
        return await sync_to_async(lambda: self.data)()

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return AListSerializer(*args, **kwargs)
