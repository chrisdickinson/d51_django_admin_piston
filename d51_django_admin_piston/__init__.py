from django.conf.urls.defaults import *
from piston import handler, resource
from django.core.exceptions import FieldError
from django.http import Http404



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
            return self.model.objects.complex_filter(query)
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
        resource_obj = resource.Resource(handler=get_handler_for_modeladmin(self, info))
        urls = patterns('',
            url(r'^api/(?P<emitter_format>\w+)', resource_obj, name='admin-piston-%s-%s' % info)
        ) + urls
        print urls

    return urls 

def autodiscover(site):
    for model in site._registry:
        model_admin = site._registry[model]
        model_admin.get_urls = wrap_instancemethod(model_admin.get_urls, wrapped_piston_urls)