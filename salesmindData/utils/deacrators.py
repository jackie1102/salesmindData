from django.http import HttpResponseRedirect


def interceptor(view_func):
    '''
    拦截器
    调用试图函数之前需要登录
    :param view_func:
    :return:
    '''
    def wrapper(request, *view_args, **view_kwargs):
        if request.session.has_key('islogin'):
            request.session.set_expiry(60 * 60 * 5)
            return view_func(request, *view_args, **view_kwargs)
        else:
            return HttpResponseRedirect('/')
    return wrapper