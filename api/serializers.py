from rest_framework import serializers
from searcher.helpers import get_variants

variants = get_variants()
if variants['status'] == 'success':
    del variants['status']
    if len(variants):
        VARIANTS = variants.items()
    else:
        VARIANTS = []
else:
    VARIANTS = []

class SearchSerializer(serializers.Serializer):
    l1 = serializers.CharField(required=True)
    l2 = serializers.CharField(required=True)
    variants = serializers.ChoiceFields(choices=VARIANTS, required=False,
                                        allow_blank=True)


