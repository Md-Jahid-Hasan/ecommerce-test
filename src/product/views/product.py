import json

from django.views import generic
from django.db.models import Prefetch,Count
from django.views.generic.list import ListView
from rest_framework.views import APIView
from rest_framework.response import Response

from product.models import Variant, Product, ProductVariant, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ProductListView(ListView):
    template_name = 'products/list.html'
    model = Product
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.objects.prefetch_related(Prefetch('productvariantprice_set')).all()
        x = ProductVariantPrice.objects.filter(product_id=16)
        print(x.values())
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        variants = ProductVariant.objects.filter(variant__active=True).values('variant_title').values('variant__title')
        context['variants'] = variants
        return context


class CreateNewProductView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        product_details = data['details']
        variants = data['variant']
        variants_price = data['price']
        if product_details.get('title') is not None and product_details.get('title') != "":
            if product_details.get('sku') is not None and product_details.get('sku') != "":
                if product_details.get('description') is not None and product_details.get('description') != "":
                    product = Product.objects.create(**data['details'])

        new_variant = {}
        for v in variants:
            variant = Variant.objects.get(id=v['option'])
            for t in v['tags']:
                new_variant[t] = ProductVariant.objects.create(variant_title=t, variant=variant, product=product)
        # variant = ProductVariant.objects.create()
        print(product)
        for price in variants_price:
            titles = price['title'].split('/')[:-1]
            new_variant_price = ProductVariantPrice.objects.create(price=price['price'], stock=price['stock'], product=product)
            try:
                new_variant_price.product_variant_one = new_variant[titles[0]]
                new_variant_price.product_variant_two = new_variant[titles[1]]
                new_variant_price.product_variant_three = new_variant[titles[2]]
            except:
                new_variant_price.save()
        return Response({"success": "Created"})
