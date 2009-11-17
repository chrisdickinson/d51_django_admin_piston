from django.conf.urls.defaults import *
from piston import handler, resource
from django.core.exceptions import FieldError
from django.http import Http404
from django.conf import settings
API_URL = getattr(settings, 'D51_DJANGO_ADMIN_PISTON_URL', 'api')

def wrap_instancemethod(imeth, with_function):
    with_instancemethod = type(imeth)(with_function, imeth.im_self, imeth.im_class)
    def wrapped(self, *args, **kwargs):
        return with_instancemethod(imeth(*args, **kwargs))
    return type(imeth)(wrapped, imeth.im_self, imeth.im_class)


class D51AdminPiston(handler.BaseHandler):
    allowed_methods = ('GET',)
    def read(self, request):
        user = getattr(request, 'user', None)
        if user is None or user.is_staff is False:
            raise Http404()
        control_keys = ['page', 'page_by']
        query = {}
        [query.update({str(key):request.GET[key]}) for key in request.GET if key not in control_keys]
        try:
            page = request.GET.get('page', 0)
            page_by = request.GET.get('page_by', 15)
            start = page*page_by
            finish = (page+1)*page_by
            return self.model.objects.complex_filter(query)[start:finish]
        except FieldError, e:
            return {'error':str(e)}

def get_handler_for_modeladmin(modeladmin, info):
    our_fields = getattr(modeladmin, 'piston_fields', [field.name for field in modeladmin.model._meta.fields])
    new_type = type(object)("piston_%s_%s"%info, (D51AdminPiston,), {
            'model':modeladmin.model,
            'fields':our_fields,
    })
    return new_type 

def wrapped_piston_urls(self, urls):
    if getattr(self, 'no_piston', False) is False:
        info = self.model._meta.app_label, self.model._meta.module_name

        handler_cls = getattr(self, 'piston_handler', get_handler_for_modeladmin(self, info))
        resource_cls = getattr(self, 'piston_resource', resource.Resource)
        resource_obj = resource_cls(handler=handler_cls)
        urls = patterns('',
            url(r'^%s/(?P<emitter_format>\w+)' % API_URL, resource_obj, name='admin-piston-%s-%s' % info)
        ) + urls
    return urls 

LOADING = False

def autodiscover(site):
    global LOADING
    if LOADING:
        return
    LOADING = True
    for model in site._registry:
        model_admin = site._registry[model]
        model_admin.get_urls = wrap_instancemethod(model_admin.get_urls, wrapped_piston_urls)
    LOADING = False
